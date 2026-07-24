from fastapi import APIRouter, HTTPException
from typing import List

from core.models import TestResult, ReportMetrics
from services.report import generate_report

router = APIRouter(
    prefix="/api",
    tags=["Report"]
)

@router.post("/report", response_model=ReportMetrics)
async def create_report(results: List[TestResult]):
    """
    Module 11: Report Generator Endpoint.
    Accepts the array of executed TestResults from the frontend,
    calculates the health metrics, and returns the raw HTML string 
    for the frontend to download or render.
    """
    try:
        if not results:
            raise ValueError("No test results provided for reporting.")
            
        metrics = generate_report(results)
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
