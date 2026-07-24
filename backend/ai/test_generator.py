import os
from pydantic import BaseModel
from typing import Optional
from google import genai
from core.models import Endpoint, TestCase

# Schema for Structured Output (Avoids Any/dict to prevent additionalProperties error in Gemini API)
class AiTestCase(BaseModel):
    path: str
    method: str
    name: str
    request_body_json_string: Optional[str] = None
    expected_status: list[int]

class TestList(BaseModel):
    tests: list[AiTestCase]


def rule_based_generate_tests(endpoints: list[Endpoint]) -> list[TestCase]:
    """
    Takes a list of Endpoints and generates actionable TestCases using basic rules.
    This serves as the fallback if AI generation fails.
    """
    print("⚠️ Using rule-based generator fallback...")
    test_cases = []
    
    for endpoint in endpoints:
        if endpoint.method in ["GET", "DELETE"]:
            test_cases.append(TestCase(
                endpoint=endpoint,
                name=f"Valid {endpoint.method} Request",
                request_body=None,
                expected_status=endpoint.expected_success_codes
            ))
        elif endpoint.method in ["POST", "PUT", "PATCH"]:
            test_cases.append(TestCase(
                endpoint=endpoint,
                name=f"Valid {endpoint.method} Request (Generic Body)",
                request_body={"test_data": "placeholder_value"},
                expected_status=endpoint.expected_success_codes
            ))
            test_cases.append(TestCase(
                endpoint=endpoint,
                name=f"Negative {endpoint.method} Request (Empty Body)",
                request_body={},
                expected_status=[400]
            ))
            test_cases.append(TestCase(
                endpoint=endpoint,
                name=f"Bad data type {endpoint.method}",
                request_body="This is just a text, not JSON!",
                expected_status=[415]
            ))
        else:
            test_cases.append(TestCase(
                endpoint=endpoint,
                name=f"Standard {endpoint.method} Request",
                request_body=None,
                expected_status=endpoint.expected_success_codes
            ))
            
    return test_cases

async def generate_tests(endpoints: list[Endpoint]) -> list[TestCase]:
    """
    AI-powered test generator using Gemini Structured Outputs.
    Batches endpoints and falls back to rule-based generation on failure.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Falling back to rule-based generator.")
        return rule_based_generate_tests(endpoints)
        
    all_tests = []
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Dynamic Batching: Split endpoints into chunks of 10 to avoid token limits
        batch_size = 10
        batches = [endpoints[i:i + batch_size] for i in range(0, len(endpoints), batch_size)]
        
        for i, batch in enumerate(batches):
            print(f"🤖 [AI Generator] Generating tests for batch {i+1}/{len(batches)}...")
            
            # Construct JSON-like prompt representation of endpoints to save tokens
            batch_data = []
            for ep in batch:
                batch_data.append({
                    "path": ep.path,
                    "method": ep.method,
                    "summary": ep.summary,
                    "parameters": ep.parameters,
                    "request_body_schema": ep.request_body_schema
                })
                
            prompt = f"""
            You are a Senior API QA Engineer. Generate realistic positive and negative test cases from the available endpoint metadata below.
            If metadata is missing, make reasonable assumptions based on REST conventions.
            
            Rules:
            1. Don't invent endpoints. Only generate tests for the endpoints provided.
            2. Generate exactly 2-4 test cases per endpoint depending on its HTTP method (e.g., GET: Valid request, Invalid path parameter; POST: Valid payload, Missing required field, Invalid datatype, Empty body).
            3. Use realistic JSON payloads based on the provided OpenAPI metadata (parameters/requestBody).
            4. Keep payloads concise and avoid optional fields unless relevant.
            
            Endpoints:
            {batch_data}
            """
            
            # Using synchronous client method for generation, though it blocks, 
            # for MVP this is perfectly fine, or we could use client.aio.models
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TestList,
                    temperature=0.2
                )
            )
            
            if response.parsed:
                import json
                for ai_test in response.parsed.tests:
                    # Find original endpoint
                    matched_ep = next((e for e in batch if e.path == ai_test.path and e.method == ai_test.method), batch[0])
                    
                    req_body = None
                    if ai_test.request_body_json_string:
                        try:
                            req_body = json.loads(ai_test.request_body_json_string)
                        except json.JSONDecodeError:
                            req_body = ai_test.request_body_json_string
                            
                    all_tests.append(TestCase(
                        endpoint=matched_ep,
                        name=ai_test.name,
                        request_body=req_body,
                        expected_status=ai_test.expected_status
                    ))
            else:
                raise ValueError("AI returned empty or unparsed structured output.")
                
        return all_tests
        
    except Exception as e:
        print(f"\n⚠️ AI Generation Failed: {str(e)}")
        print("Fallback on: Rate limit, Timeout, Invalid structured output, or API/network errors.")
        return rule_based_generate_tests(endpoints)

