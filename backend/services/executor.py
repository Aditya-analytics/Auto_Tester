# pyrefly: ignore [missing-import]
import httpx
import json
import base64
import asyncio
import time
from typing import Any
from core.models import ExecutionRequest, StructuredTestCase, AuthCredentials, TestResult

def inject_credentials(headers: dict[str, Any], credentials: AuthCredentials) -> dict[str, Any]:
    """
    Injects credentials into the HTTP headers based on the auth type.
    """
    if credentials.auth_type == 'apikey' and credentials.token:
        # Some APIs use Authorization, some use api_key. We inject standard Bearer/api_key for MVP.
        headers['Authorization'] = f"Bearer {credentials.token}"
        headers['api_key'] = credentials.token
        
    elif credentials.auth_type == 'basic' and credentials.username and credentials.password:
        auth_str = f"{credentials.username}:{credentials.password}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        headers['Authorization'] = f"Basic {b64_auth}"
        
    return headers

async def execute_single_test(
    client: httpx.AsyncClient, 
    base_url: str,
    test: StructuredTestCase, 
    credentials: AuthCredentials,
    sla_threshold_ms: int
) -> TestResult:
    """
    Executes a single test case using the shared httpx AsyncClient.
    """
    try:
        # 1. Parse AI JSON strings back to dicts
        headers = json.loads(test.headers_json) if test.headers_json and test.headers_json != "null" else {}
        body = json.loads(test.request_body_json) if test.request_body_json and test.request_body_json != "null" else None
        
        # 2. Inject Secrets
        headers = inject_credentials(headers, credentials)
        
        # 3. Construct full URL
        clean_base = base_url.rstrip("/")
        clean_path = test.url if test.url.startswith("/") else f"/{test.url}"
        full_url = f"{clean_base}{clean_path}"
        
        # 4. Fire network request and track time
        start_time = time.time()
        response = await client.request(
            method=test.method,
            url=full_url,
            headers=headers,
            json=body
        )
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        
        # 5. Determine success and SLA (Module 10 Validator)
        success = response.status_code in test.expected_status
        is_slow = response_time_ms > sla_threshold_ms
        
        # 6. Parse response safely
        try:
            response_body = response.json()
        except:
            response_body = response.text

        return TestResult(
            test_case=test,
            success=success,
            status_code=response.status_code,
            response_body=response_body,
            response_time_ms=response_time_ms,
            is_slow=is_slow
        )
        
    except Exception as e:
        # Handle network failures, timeouts, connection refused
        return TestResult(
            test_case=test,
            success=False,
            error_message=str(e)
        )

async def execute_test_suite(request: ExecutionRequest) -> list[TestResult]:
    """
    Module 9: The Execution Engine core.
    Uses asyncio.gather to execute all tests concurrently for high performance.
    """
    # Create a single client connection pool for efficiency
    async with httpx.AsyncClient(timeout=request.timeout) as client:
        
        # Create a list of async tasks
        tasks = [
            execute_single_test(
                client, 
                request.base_url, 
                test, 
                request.credentials, 
                request.sla_threshold_ms
            )
            for test in request.test_cases
        ]
        
        # Execute them all concurrently!
        results = await asyncio.gather(*tasks)
        
        return list(results)
