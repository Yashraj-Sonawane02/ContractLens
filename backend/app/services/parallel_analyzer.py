import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from app.services.rag_engine import analyze_clause_with_rag

# ThreadPoolExecutor for concurrent clause evaluations
executor = ThreadPoolExecutor(max_workers=8)

def process_single_clause_task(args):
    clause, language = args
    return analyze_clause_with_rag(clause, language=language)

async def analyze_full_contract_parallel(clauses: List[Dict[str, Any]], language: str = "English") -> Dict[str, Any]:
    start_time = time.time()
    loop = asyncio.get_event_loop()

    # Prepare parallel task arguments
    tasks = [
        loop.run_in_executor(executor, process_single_clause_task, (clause, language))
        for clause in clauses
    ]

    # Execute all clause analysis tasks concurrently
    analyzed_clauses = await asyncio.gather(*tasks)

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    top_concerns = []

    for result in analyzed_clauses:
        r_level = result["risk_level"]
        if r_level == "CRITICAL":
            critical_count += 1
            top_concerns.append(f"[{result['title']}] {result['reason']}")
        elif r_level == "HIGH":
            high_count += 1
            top_concerns.append(f"[{result['title']}] {result['reason']}")
        elif r_level == "MEDIUM":
            medium_count += 1
        else:
            low_count += 1

    # Contract Health Score calculation
    score_deductions = (critical_count * 20) + (high_count * 10) + (medium_count * 4)
    contract_health_score = max(10, min(100, 100 - score_deductions))

    processing_time = round(time.time() - start_time, 3)

    # Executive Summary
    exec_summary = (
        f"Analyzed {len(clauses)} clauses under Maharashtra Legal Jurisdiction in {processing_time}s. "
        f"Identified {critical_count} critical-risk issues and {high_count} high-risk concerns. "
        f"Overall Contract Health Score is {contract_health_score}/100."
    )

    # Risk Heatmap
    risk_heatmap = [
        {
            "clause_id": c["clause_id"],
            "title": c["title"],
            "risk_level": c["risk_level"],
            "section": c["section_number"]
        }
        for c in analyzed_clauses
    ]

    return {
        "health_score": contract_health_score,
        "total_clauses": len(clauses),
        "risk_summary": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "executive_summary": exec_summary,
        "top_concerns": top_concerns[:5],
        "analyzed_clauses": list(analyzed_clauses),
        "risk_heatmap": risk_heatmap,
        "processing_time_seconds": processing_time
    }
