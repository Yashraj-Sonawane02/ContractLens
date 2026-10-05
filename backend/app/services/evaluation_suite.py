import os
import json
import logging
import asyncio
from typing import Dict, Any, List

from app.services.parallel_analyzer import analyze_full_contract_parallel

logger = logging.getLogger(__name__)

PUNE_DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../testing data/data 1/contract_answer_key.json"))
THANE_DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../testing data/data 2/contract_answer_key_thane.json"))

async def evaluate_single_dataset(dataset_path: str, dataset_name: str) -> Dict[str, Any]:
    """
    Evaluates ContractLens statutory compliance pipeline against a ground-truth labeled legal agreement dataset.
    Calculates Precision, Recall, F1-Score, Multi-Class Accuracy, and Health Score Alignment.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Evaluation dataset file not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        ground_truth_data = json.load(f)

    gt_clauses = ground_truth_data.get("clauses", [])
    expected_health_score = ground_truth_data.get("expected_health_score", 100)

    # 1. Format clauses for parallel analyzer
    segmented_clauses = []
    for c in gt_clauses:
        segmented_clauses.append({
            "clause_id": f"clause_{c['clause_no']}",
            "section_number": c["clause_no"],
            "title": c["title"],
            "text": c["text"],
            "topic": c.get("expected_category", "General")
        })

    # 2. Execute ContractLens Pipeline Analysis
    analysis_result = await analyze_full_contract_parallel(segmented_clauses, language="English")
    predicted_clauses = analysis_result.get("analyzed_clauses", [])
    predicted_health_score = analysis_result.get("health_score", 100)

    total_clauses = len(gt_clauses)
    exact_risk_matches = 0
    tp, fp, fn, tn = 0, 0, 0, 0

    detailed_clause_eval = []

    for gt in gt_clauses:
        c_no = gt["clause_no"]
        exp_risk = gt["expected_risk"]

        # Find matching predicted clause
        matched_pred = None
        for p in predicted_clauses:
            if p.get("section_number") == c_no or p.get("clause_id") == f"clause_{c_no}":
                matched_pred = p
                break

        if not matched_pred and c_no <= len(predicted_clauses):
            matched_pred = predicted_clauses[c_no - 1]

        pred_risk = matched_pred.get("risk_level", "LOW") if matched_pred else "UNKNOWN"

        # Exact multi-class risk match
        is_exact_match = (exp_risk == pred_risk)
        if is_exact_match:
            exact_risk_matches += 1

        # Binary Risky Clause Detection (Risky: CRITICAL/HIGH/MEDIUM vs Compliant: LOW)
        is_actual_risky = (exp_risk in ["CRITICAL", "HIGH", "MEDIUM"])
        is_predicted_risky = (pred_risk in ["CRITICAL", "HIGH", "MEDIUM"])

        if is_actual_risky and is_predicted_risky:
            tp += 1
        elif not is_actual_risky and is_predicted_risky:
            fp += 1
        elif is_actual_risky and not is_predicted_risky:
            fn += 1
        else:
            tn += 1

        detailed_clause_eval.append({
            "clause_no": c_no,
            "title": gt["title"],
            "expected_category": gt.get("expected_category"),
            "expected_risk": exp_risk,
            "predicted_risk": pred_risk,
            "is_exact_match": is_exact_match,
            "expected_legal_basis": gt.get("legal_basis"),
            "predicted_statutes": [f"{s.get('act_short')} {s.get('section')}" for s in matched_pred.get("relevant_statutes", [])] if matched_pred else []
        })

    # Metric Calculations
    overall_exact_accuracy = round((exact_risk_matches / total_clauses) * 100, 2)
    precision = round((tp / (tp + fp)) * 100, 2) if (tp + fp) > 0 else 100.0
    recall = round((tp / (tp + fn)) * 100, 2) if (tp + fn) > 0 else 100.0
    f1_score = round((2 * precision * recall / (precision + recall)), 2) if (precision + recall) > 0 else 0.0
    health_score_delta = abs(predicted_health_score - expected_health_score)

    return {
        "dataset_name": dataset_name,
        "document_title": ground_truth_data.get("document", dataset_name),
        "total_evaluated_clauses": total_clauses,
        "metrics": {
            "risky_clause_precision": precision,
            "risky_clause_recall": recall,
            "f1_score": f1_score,
            "exact_multi_class_accuracy": overall_exact_accuracy,
            "expected_health_score": expected_health_score,
            "predicted_health_score": predicted_health_score,
            "health_score_alignment_delta": health_score_delta,
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "true_negatives": tn
            }
        },
        "clause_evaluations": detailed_clause_eval
    }

async def run_comprehensive_project_evaluation() -> Dict[str, Any]:
    """
    Runs multi-dataset empirical evaluation across Data 1 (Pune Agreement) and Data 2 (Thane Agreement).
    Computes overall benchmark performance metrics for ContractLens.
    """
    pune_eval = await evaluate_single_dataset(PUNE_DATASET_PATH, "Dataset 1: Pune Leave & License Agreement")
    thane_eval = await evaluate_single_dataset(THANE_DATASET_PATH, "Dataset 2: Thane Leave & License Agreement")

    # Aggregate Metrics
    avg_precision = round((pune_eval["metrics"]["risky_clause_precision"] + thane_eval["metrics"]["risky_clause_precision"]) / 2, 2)
    avg_recall = round((pune_eval["metrics"]["risky_clause_recall"] + thane_eval["metrics"]["risky_clause_recall"]) / 2, 2)
    avg_f1 = round((pune_eval["metrics"]["f1_score"] + thane_eval["metrics"]["f1_score"]) / 2, 2)
    avg_accuracy = round((pune_eval["metrics"]["exact_multi_class_accuracy"] + thane_eval["metrics"]["exact_multi_class_accuracy"]) / 2, 2)
    avg_health_delta = round((pune_eval["metrics"]["health_score_alignment_delta"] + thane_eval["metrics"]["health_score_alignment_delta"]) / 2, 2)

    total_tp = pune_eval["metrics"]["confusion_matrix"]["true_positives"] + thane_eval["metrics"]["confusion_matrix"]["true_positives"]
    total_fp = pune_eval["metrics"]["confusion_matrix"]["false_positives"] + thane_eval["metrics"]["confusion_matrix"]["false_positives"]
    total_fn = pune_eval["metrics"]["confusion_matrix"]["false_negatives"] + thane_eval["metrics"]["confusion_matrix"]["false_negatives"]
    total_tn = pune_eval["metrics"]["confusion_matrix"]["true_negatives"] + thane_eval["metrics"]["confusion_matrix"]["true_negatives"]

    return {
        "status": "success",
        "evaluation_summary": {
            "total_datasets_evaluated": 2,
            "total_clauses_evaluated": pune_eval["total_evaluated_clauses"] + thane_eval["total_evaluated_clauses"],
            "overall_risky_detection_precision": avg_precision,
            "overall_risky_detection_recall": avg_recall,
            "overall_f1_score": avg_f1,
            "overall_multi_class_accuracy": avg_accuracy,
            "average_health_score_delta": avg_health_delta,
            "cumulative_confusion_matrix": {
                "true_positives": total_tp,
                "false_positives": total_fp,
                "false_negatives": total_fn,
                "true_negatives": total_tn
            }
        },
        "datasets": [pune_eval, thane_eval]
    }
