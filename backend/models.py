from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal, Any

class ApiConfig(BaseModel):
    """
    Configuration model for the API Test Agent.
    Validates user inputs before they enter the system.
    """
    base_url: HttpUrl = Field(..., description="The base URL of the API to test.")
    
    auth_type: Literal["none", "bearer", "api_key", "basic","oauth2"] = Field(
        default="none", description="The type of authentication used."
    )
    
    credentials: Optional[str] = Field(
        default=None, description="The token or key for authentication."
    )

class Endpoint(BaseModel):
    path: str = Field(...)
    method: str = Field(...,description="Method in uppercase")

class TestCase(BaseModel):
    endpoint: Endpoint
    name: str = Field(..., description="Name of the test scenario")
    request_body: Optional[Any] = Field(default=None, description="Body to send in the request")
    expected_status: int = Field(..., description="Expected HTTP Status Code")

class TestResult(BaseModel):
    test_case: TestCase
    actual_status: int
    response_time_ms: float
    response_body: str

class ValidationResult(BaseModel):
    test_result: TestResult
    passed: bool
    failure_reason: Optional[str] = None
    ai_explanation: Optional[str] = None