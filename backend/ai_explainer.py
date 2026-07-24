from models import ValidationResult
import asyncio

async def analyze_failure(validation: ValidationResult) -> ValidationResult:
    """
    Takes a FAILED ValidationResult and simulates an AI analyzing the failure.
    Attaches the 'ai_explanation' string to the object.
    """
    # If the test passed, there's nothing to explain!
    if validation.passed:
        validation.ai_explanation = "Test passed perfectly. No analysis needed."
        return validation
        
    print(f"🤖 [AI Engine] Analyzing failure for: {validation.test_result.test_case.name}...")
    
    # Simulate network delay for calling the OpenAI/Gemini API
    await asyncio.sleep(1.5)
    
    expected = validation.test_result.test_case.expected_status
    actual = validation.test_result.actual_status
    method = validation.test_result.test_case.endpoint.method
    
    # ---------------------------------------------------------
    # MOCK AI LOGIC (Replace this with real LLM API call later)
    # ---------------------------------------------------------
    if "SLA" in str(validation.failure_reason):
        explanation = "The API is functionally correct but unacceptably slow. Consider adding database indexes or caching to speed up the response."
        
    elif expected == 204 and actual == 200:
        explanation = f"The {method} request was processed, but the developer forgot to set the HTTP status to 204 (No Content). The router is defaulting to 200 (OK). Update the router return code."
        
    elif expected == 201 and actual == 200:
        explanation = f"The {method} request succeeded, but the standard for creation is 201 Created. The server incorrectly returned 200 OK."
        
    elif actual in [400, 422]:
        explanation = "The server correctly caught bad data, but ensure the error message in the body is user-friendly and explains exactly which field was missing."
        
    elif actual == 0:
        explanation = "The connection completely failed. Check if the server is offline, or if the URL is misspelled."
        
    else:
        explanation = f"Unexpected error. Expected {expected} but got {actual}. Check server logs for a potential crash or unhandled exception."
        
    validation.ai_explanation = explanation
    return validation

# ==========================================
# MANUAL TESTING
# ==========================================
