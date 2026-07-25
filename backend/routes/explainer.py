from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.models import TestResult
from ai.ai_explainer import analyze_failure

router = APIRouter(
    prefix="/api",
    tags=["Explainer"]
)

class ExplanationResponse(BaseModel):
    explanation: str

@router.post("/explain", response_model=ExplanationResponse)
async def explain_test_failure(test_result: TestResult):
    """
    Module 12: AI Fix Suggestion (On Demand).
    Takes a failed TestResult and uses Gemini to explain the root cause and provide a fix.
    """
    try:
        explanation = await analyze_failure(test_result)
        return ExplanationResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
