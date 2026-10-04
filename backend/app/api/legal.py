from fastapi import APIRouter, Query
from typing import Dict, Any, List
from app.services.legal_knowledge_base import legal_kb

router = APIRouter(prefix="/legal", tags=["Legal Knowledge Explorer"])

@router.get("/explorer", response_model=Dict[str, Any])
def explore_statutory_laws(query: str = Query("", description="Search term for statutory provisions")):
    if not query.strip():
        # Return all indexed laws
        return {
            "status": "success",
            "total_statutes": len(legal_kb.laws),
            "jurisdiction": "Maharashtra, India",
            "indexed_acts": [
                "Maharashtra Rent Control Act, 1999",
                "Transfer of Property Act, 1882",
                "Indian Contract Act, 1872"
            ],
            "laws": legal_kb.laws
        }

    results = legal_kb.search_legal_context(query_text=query, top_k=5)
    return {
        "status": "success",
        "query": query,
        "total_results": len(results),
        "laws": results
    }
