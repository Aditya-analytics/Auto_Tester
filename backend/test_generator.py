from models import Endpoint, TestCase

def generate_tests(endpoints: list[Endpoint]) -> list[TestCase]:
    """
    Takes a list of Endpoints and generates actionable TestCases.
    Applies basic Negative Testing for POST/PUT requests.
    """
    test_cases = []
    
    for endpoint in endpoints:
        
        # Rule 1: GET and DELETE usually don't need a body. 
        # We just generate one standard "Happy Path" test.
        if endpoint.method in ["GET", "DELETE"]:
            test_cases.append(
                TestCase(
                    endpoint=endpoint,
                    name=f"Valid {endpoint.method} Request",
                    request_body=None,
                    expected_status=200 # Usually 200 OK
                )
            )
            
        # Rule 2: POST, PUT, PATCH usually expect data.
        # We generate a Valid test AND a Negative test to try to break it.
        elif endpoint.method in ["POST", "PUT", "PATCH"]:
            
            # 1. Happy Path
            test_cases.append(
                TestCase(
                    endpoint=endpoint,
                    name=f"Valid {endpoint.method} Request (Generic Body)",
                    request_body={"test_data": "placeholder_value"}, # Generic mock data for MVP
                    expected_status=201 # Usually 201 Created for POST, or 200 OK
                )
            )
            
            # 2. Negative Test: Empty Body
            test_cases.append(
                TestCase(
                    endpoint=endpoint,
                    name=f"Negative {endpoint.method} Request (Empty Body)",
                    request_body={}, # Intentionally empty to see if the API handles it gracefully
                    expected_status=400 # 400 Bad Request or 422 Unprocessable Entity
                )
            )

            # 3. Bad data type (Your addition!)
            test_cases.append(
                TestCase(
                    endpoint=endpoint,
                    name=f"Bad data type {endpoint.method}",
                    request_body="This is just a text, not JSON!",
                    expected_status=415 # 415 Unsupported Media Type or 400 Bad Request
                )
            )
            
        else:
            # Fallback for anything else (e.g., OPTIONS, HEAD)
            test_cases.append(
                TestCase(
                    endpoint=endpoint,
                    name=f"Basic {endpoint.method} Request",
                    request_body=None,
                    expected_status=200
                )
            )
            
    return test_cases

# ==========================================
# MANUAL TESTING
# ==========================================
