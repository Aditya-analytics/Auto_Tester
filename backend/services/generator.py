import os
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

import json
from core.models import Endpoint, StructuredTestCase

def normalize_json_keys(data, schema):
    """Recursively normalizes JSON keys to strictly match the OpenAPI schema properties."""
    if not isinstance(data, dict) or not isinstance(schema, dict):
        if isinstance(data, list) and isinstance(schema, dict) and "items" in schema:
            return [normalize_json_keys(item, schema["items"]) for item in data]
        return data
        
    properties = schema.get("properties", {})
    
    # Create a mapping of lowercased stripped keys to actual schema keys
    valid_key_map = {}
    for k in properties.keys():
        normalized_k = k.lower().replace("_", "").replace("-", "")
        valid_key_map[normalized_k] = k
        
    normalized_data = {}
    for k, v in data.items():
        search_k = k.lower().replace("_", "").replace("-", "")
        if search_k in valid_key_map:
            actual_k = valid_key_map[search_k]
            prop_schema = properties.get(actual_k, {})
            normalized_data[actual_k] = normalize_json_keys(v, prop_schema)
        else:
            normalized_data[k] = v
            
    return normalized_data

# Load environment variables from the root .env file
load_dotenv(dotenv_path="../.env")

# We need a wrapper Pydantic model for Gemini to return a list of test cases
class TestSuite(BaseModel):
    tests: list[StructuredTestCase]

def generate_tests(endpoints: list[Endpoint], test_count: int = 2) -> list[StructuredTestCase]:
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

Generate exactly {test_count} contract test cases for every endpoint below.

Rules:
- Generate a mix of valid positive requests and high-value negative requests.
- You MUST provide at least 2 safe expected status codes for positive test cases (e.g., [200, 201]).
- You MUST provide appropriate and realistic `request_body_json` data based on schemas.
- CRITICAL: Use the EXACT key names specified in the `request_schema` properties. For example, if the schema requires `base_url`, you MUST output {{"base_url": "..."}} and NOT `baseUrl`.
- You MUST generate a short, descriptive `name` for each test case (e.g., "Valid User Login").
- Use ONLY the provided endpoints.
- Never invent URLs, fields, or status codes.
- Build request bodies strictly from `request_schema`.
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
        
    # Post-process AI outputs to ensure exact key casing matches the schemas
    test_cases = response.parsed.tests
    for test in test_cases:
        # Find matching endpoint to get its request schema
        matching_ep = next((ep for ep in endpoints if ep.path == test.url and ep.method.upper() == test.method.upper()), None)
        
        if matching_ep and matching_ep.request_schema and test.request_body_json and test.request_body_json != "null":
            try:
                body_dict = json.loads(test.request_body_json)
                normalized_body = normalize_json_keys(body_dict, matching_ep.request_schema)
                test.request_body_json = json.dumps(normalized_body, indent=2)
            except json.JSONDecodeError:
                pass # If AI somehow failed to generate valid JSON, leave it as is
                
    return test_cases

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
