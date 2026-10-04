import asyncio
from app.services.parallel_analyzer import analyze_full_contract_parallel

async def test_parallel_execution():
    sample_clauses = [
        {"clause_id": f"clause_{i}", "section_number": str(i), "title": f"Test Clause {i}", "text": "The Licensee agrees to pay ₹50,000 rent and ₹1,000 daily penalty.", "topic": "Penalty & Interest", "triage_status": "flagged_for_rag"}
        for i in range(1, 11)
    ]

    result = await analyze_full_contract_parallel(sample_clauses, language="English")
    
    assert len(result["analyzed_clauses"]) == 10
    assert result["processing_time_seconds"] < 5.0

    print("PHASE 7 PARALLEL ANALYSIS & SPEED BENCHMARK PASSED CLEANLY!")
    print(f"Processed 10 clauses concurrently in: {result['processing_time_seconds']} seconds")

if __name__ == "__main__":
    asyncio.run(test_parallel_execution())
