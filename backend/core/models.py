from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal, Any

class BaseConfig(BaseModel):
    """
    Module 1: User Input Configuration.
    Collects the minimum required information to start testing.
    """
    base_url: HttpUrl = Field(
        ..., 
        description="The base URL of the API to test.",
        json_schema_extra={"example": "http://127.0.0.1:8000"}
    )

class Endpoint(BaseModel):
    path: str = Field(..., description="The URL path (e.g., /users/{id})")
    method: str = Field(..., description="The HTTP method in uppercase (e.g., GET, POST)")
    summary: Optional[str] = Field(default=None, description="A short summary of what the endpoint does")
    description: Optional[str] = Field(default=None, description="A detailed explanation of the endpoint behavior")
    tags: list[str] = Field(default_factory=list, description="Categorization tags from Swagger used for grouping")
    auth_required: bool = Field(default=False, description="True if a security scheme applies to this endpoint")
    auth_type: Optional[str] = Field(default=None, description="The name of the security scheme (e.g., Bearer, api_key)")
    content_type: Optional[str] = Field(default=None, description="The expected Content-Type (e.g., application/json)")
    parameters: list[dict] = Field(default_factory=list, description="List of path, query, and header parameters")
    request_schema: Optional[dict] = Field(default=None, description="JSON schema for the request body")
    responses: list[int] = Field(default_factory=list, description="List of expected HTTP status codes (e.g., [200, 404])")
    
    # Module 5: Safety and Support Flags
    supported: bool = Field(default=True, description="True if the endpoint can be safely tested")
    unsupported_reason: Optional[str] = Field(default=None, description="Reason if supported is False")
    risk_level: str = Field(default="safe", description="Risk level (e.g., safe, high_risk)")

class AuthCredentials(BaseModel):
    """
    Module 7: Credential Collector.
    Holds the credentials collected from the user to be used ONLY in Module 9.
    """
    auth_type: str = Field(..., description="The type of auth (e.g., apikey, basic, bearer, none)")
    token: Optional[str] = Field(default=None, description="Used for API Key or Bearer Token")
    username: Optional[str] = Field(default=None, description="Used for Basic Auth")
    password: Optional[str] = Field(default=None, description="Used for Basic Auth")

class StructuredTestCase(BaseModel):
    """
    Module 8: AI Test Generator Output.
    The strict Pydantic model that the Gemini AI will output.
    """
    url: str = Field(..., description="The path of the endpoint, e.g. /users/{id}")
    method: str = Field(..., description="The HTTP method, e.g. GET, POST")
    name: str = Field(..., description="A short, descriptive name for this test case, e.g. 'Successful User Login'")
    headers_json: str = Field(default="{}", description="JSON stringified dictionary of expected headers")
    request_body_json: str = Field(default="null", description="JSON stringified request body to send")
    expected_status: list[int] = Field(..., description="List of expected HTTP Status Codes for this test")

class ExecutionRequest(BaseModel):
    """
    Module 9: Executor Input.
    Combines the user's secret credentials with the AI's generated payloads
    so the Executor can inject the credentials right before sending.
    """
    base_url: str = Field(..., description="The base URL of the API (e.g. https://petstore.swagger.io/v2)")
    credentials: AuthCredentials
    test_cases: list[StructuredTestCase]
    timeout: int = Field(default=5, description="Network timeout in seconds")
    sla_threshold_ms: int = Field(default=2000, description="Max allowed response time in ms before marked as slow")

class TestResult(BaseModel):
    test_case: StructuredTestCase
    success: bool
    status_code: Optional[int] = None
    response_body: Optional[Any] = None
    response_time_ms: Optional[float] = None
    is_slow: Optional[bool] = None
    error_message: Optional[str] = None

class ValidationResult(BaseModel):
    test_result: TestResult
    passed: bool
    failure_reason: Optional[str] = None
    ai_explanation: Optional[str] = None

class ReportMetrics(BaseModel):
    """
    Module 11: Report Aggregation.
    Holds the calculated health scores for the final report.
    """
    total_tests: int
    passed_tests: int
    failed_tests: int
    slow_tests: int
    health_score: float
    pass_rate: float
    html_content: str = Field(default="")

# if __name__=="__main__":
#     from services.discovery import discover_openapi
#     from services.parser import extract_endpoints

# # Download the raw data
#     raw = discover_openapi("https://petstore.swagger.io/v2")

# # Extract the beautiful Endpoint objects
#     endpoints = extract_endpoints(raw)

# # Let's inspect the very first endpoint we found
#     first_endpoint = endpoints[0]
#     print(f"Path: {first_endpoint.method} {first_endpoint.path}")
#     print(f"Auth Required: {first_endpoint.auth_required}")
#     print(f"Content Type: {first_endpoint.content_type}")
#     print(f"Tags: {first_endpoint.tags}")
#     print(f"auth type: {first_endpoint.auth_type}")
