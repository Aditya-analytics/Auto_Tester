# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from httpx import Response

def discover_openapi(base_url: str) -> dict:
    """
    Attempts to discover and download the OpenAPI/Swagger JSON document.
    It first checks if the user provided the direct file URL. 
    If not, it guesses common paths.
    """
    # Common paths where developers hide their API documentation
    common_paths = [
        "",                     # First, check if base_url IS the exact file
        "/openapi.json",
        "/swagger.json",
        "/api-docs",
        "/docs/openapi.json",
        "/api/swagger.json",
        "/api/docs/swagger.json"
    ]
    
    # Strip any trailing slashes from the base_url so we don't get double slashes
    base_url = base_url.rstrip("/")

    # We use a context manager (with) to ensure the client closes the connection properly
    with httpx.Client(timeout=5.0) as client:
        for path in common_paths:
            test_url = f"{base_url}{path}"
            print(f"Knocking on: {test_url}")
            
            try:
                response: Response = client.get(test_url)
                
                # If we get a 200 OK, let's try to parse it as JSON
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # A quick check to see if it actually looks like an OpenAPI file
                        if "openapi" in data or "swagger" in data:
                            version = data.get("openapi") or data.get("swagger")
                            print(f"🎉 Found OpenAPI documentation at: {test_url}")
                            print(f"✅ OpenAPI Version detected: {version}")
                            return data
                    except ValueError:
                        # It was a 200 OK, but not JSON (maybe it was just a normal HTML webpage)
                        pass
                        
            except httpx.RequestError:
                # The server didn't exist, or the connection failed. Move to the next path.
                pass
                
    # If the loop finishes entirely and we are still here, we failed.
    raise Exception(f"Could not discover OpenAPI documentation for {base_url}")

# ==========================================
# MANUAL TESTING & ERROR SIMULATION
# ==========================================
if __name__ == "__main__":
    # We can just call the function directly since it's in this same file!
    raw_json = discover_openapi("https://petstore.swagger.io/v2")
