import os
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

from core.models import Endpoint, StructuredTestCase

# Load environment variables from the root .env file
load_dotenv(dotenv_path="../.env")

# We need a wrapper Pydantic model for Gemini to return a list of test cases
class TestSuite(BaseModel):
    tests: list[StructuredTestCase]

def generate_tests(endpoints: list[Endpoint]) -> list[StructuredTestCase]:
    """
    Module 8: AI Test Generator
    Uses Google Gemini 2.5 Flash with strict structured output 
    to generate test payloads.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    # Initialize the new google-genai client
    client = genai.Client(api_key=api_key)
    
    # Convert Pydantic models to a dict so we can dump them into the prompt
    endpoints_json = [ep.model_dump() for ep in endpoints]
    
    prompt = f"""
You are an API QA Engineer.

Generate exactly TWO contract test cases for every endpoint below:

1. One valid request.
2. One high-value negative request (missing required field OR invalid datatype OR invalid path/query parameter).

Rules:
- Use ONLY the provided endpoints.
- Never invent URLs, fields, or status codes.
- Build request bodies strictly from request_schema.
- Respect request_content_type.
- Replace path parameters with realistic values.
- Authentication is handled externally; never generate Authorization headers.
- If no body is required, set request_body_json="null".
- headers_json and request_body_json MUST be JSON-encoded strings.
- expected_status MUST be a list of integers (e.g., [200, 201] for success, or [400, 422] for negative).
- Return ONLY valid JSON matching the provided Pydantic schema. No markdown or explanations.

Endpoints:
{endpoints_json}
"""
    
    # Call Gemini Flash Lite with Structured Outputs
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': TestSuite,
            'temperature': 0.2, # Low temperature for more deterministic, factual generation
        },
    )
    
    if not response.parsed:
        raise ValueError("Failed to generate structured test cases from Gemini.")
        
    return response.parsed.tests

if __name__ == "__main__":
    # A quick local test for the generator
    print("Testing AI Generator locally...")
    sample_endpoint = Endpoint(
        path="/pet/{petId}",
        method="GET",
        summary="Find pet by ID",
        tags=["pet"],
        auth_required=False,
        parameters=[{"name": "petId", "in": "path", "required": True, "type": "integer"}],
        responses=[200, 400, 404]
    )
    
    try:
        tests = generate_tests([sample_endpoint])
        for t in tests:
            print(f"Generated Test: {t.method} {t.url} (Expects {t.expected_status})")
    except Exception as e:
        print(f"Error: {e}")
