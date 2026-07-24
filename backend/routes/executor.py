from fastapi import APIRouter, HTTPException
from typing import List

from core.models import ExecutionRequest, TestResult
from services.executor import execute_test_suite

router = APIRouter(
    prefix="/api",
    tags=["Executor"]
)

@router.post("/execute", response_model=List[TestResult])
async def execute_tests(request: ExecutionRequest):
    """
    Module 9 & 10: Executor Endpoint.
    Accepts the test cases and credentials, injects them securely,
    executes them concurrently against the target API, and validates the response.
    """
    try:
        if not request.test_cases:
            raise ValueError("No test cases provided for execution.")
            
        # Call our async execution engine
        results = await execute_test_suite(request)
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
