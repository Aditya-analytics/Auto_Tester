import os
import asyncio
from dotenv import load_dotenv
from google import genai
from core.models import ValidationResult

# Load environment variables from the .env file one level up (in auto_test)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

async def analyze_failure(validation: ValidationResult) -> ValidationResult:
    """
    Takes a FAILED ValidationResult and uses the official Google GenAI SDK to analyze the failure.
    Attaches the 'ai_explanation' string to the object.
    """
    if validation.passed:
        validation.ai_explanation = "Test passed perfectly. No analysis needed."
        return validation
        
    print(f"🤖 [Gemini AI Engine] Analyzing failure for: {validation.test_result.test_case.name}...")
    
    expected = validation.test_result.test_case.expected_status
    actual = validation.test_result.actual_status
    method = validation.test_result.test_case.endpoint.method
    path = validation.test_result.test_case.endpoint.path
    
    # Truncate response body to save tokens
    body = validation.test_result.response_body[:300]
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        validation.ai_explanation = "⚠️ GEMINI_API_KEY is missing from .env file."
        return validation

    prompt = f"""
    Act as a Senior API QA Engineer. 
    The automated test for `{method} {path}` failed.
    We expected one of these HTTP status codes {expected}, but the server returned {actual}.
    The server's response body snippet is: {body}
    
    First, categorize this failure by prefixing your response with exactly ONE of these tags:
    - 🚨 Backend Bug (for 500-level crashes)
    - ⚠️ False Positive / Test Assumption (e.g. 404 because resource wasn't created)
    - ❌ Schema Violation (e.g. 415/400 due to bad payload)
    - 📝 API Documentation Mismatch (e.g. Swagger says 200, API returns 201)
    
    Then, explain what likely went wrong and how the backend developer can fix it in exactly 2 concise sentences. Do not use markdown formatting.
    """
    
    try:
        # Using the official Google GenAI SDK (async client)
        client = genai.Client(api_key=api_key)
        
        # We use the aio (async io) namespace for async calls
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        explanation = response.text.strip()
                
    except Exception as e:
        explanation = f"⚠️ SDK Error calling Gemini: {str(e)}"
        
    validation.ai_explanation = explanation
    return validation

# ==========================================
# MANUAL TESTING
# ==========================================
