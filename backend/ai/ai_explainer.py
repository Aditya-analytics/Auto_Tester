import os
import asyncio
from dotenv import load_dotenv
from google import genai
from core.models import TestResult

# Load environment variables from the .env file one level up (in auto_test)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

async def analyze_failure(test_result: TestResult) -> str:
    """
    Module 12: AI Fix Suggestion (On Demand).
    Takes a FAILED TestResult and uses the official Google GenAI SDK to analyze the failure.
    Returns a markdown formatted explanation.
    """
    if test_result.success:
        return "Test passed perfectly. No analysis needed."
        
    print(f"🤖 [Gemini AI Engine] Analyzing failure for: {test_result.test_case.url}...")
    
    expected = test_result.test_case.expected_status
    actual = test_result.status_code
    method = test_result.test_case.method
    path = test_result.test_case.url
    
    # Truncate response body to save tokens
    body = str(test_result.response_body)[:500] if test_result.response_body else "No response body"
    request_body = test_result.test_case.request_body_json
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ GEMINI_API_KEY is missing from .env file."

    prompt = f"""
    Act as a Senior API QA Engineer. 
    The automated test for `{method} {path}` failed.
    We sent this request body: {request_body}
    We expected one of these HTTP status codes {expected}, but the server returned {actual}.
    The server's response body snippet is: {body}
    
    Please provide a brief, actionable analysis structured EXACTLY with these markdown headings:
    
    ### Possible Cause
    (Explain why the server likely rejected the request)
    
    ### Suggested Fix
    (Provide the exact steps to fix the backend API code)
    
    ### Code Example
    (Provide a small pseudo-code snippet showing the fix)
    
    ### Best Practice
    (A 1-sentence tip on avoiding this in the future)
    """
    
    try:
        # Using the official Google GenAI SDK (async client)
        client = genai.Client(api_key=api_key)
        
        # We use the aio (async io) namespace for async calls
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
                
    except Exception as e:
        return f"⚠️ SDK Error calling Gemini: {str(e)}"

# ==========================================
# MANUAL TESTING
# ==========================================
