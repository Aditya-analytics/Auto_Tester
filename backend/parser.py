from models import Endpoint
# pyrefly: ignore [missing-import]
from discovery import discover_openapi

def extract_endpoints(swagger_data: dict) -> list[Endpoint]:
    """
    Parses a raw OpenAPI/Swagger dictionary and flattens it into a 
    clean list of Endpoint objects.
    """
    endpoints = []
    
    # 1. Grab the "paths" dictionary. If it doesn't exist, default to an empty dictionary {}.
    paths = swagger_data.get("paths", {})
    
    # 2. Loop through every path (e.g., "/pets", "/store/order")
    for path, path_data in paths.items():
        
        # 3. Loop through every key under that path (usually "get", "post", etc.)
        for method in path_data.keys():
            
            # OpenAPI sometimes puts non-HTTP keys here like "parameters" or "$ref". 
            # We only want to extract standard HTTP methods.
            valid_methods = ["get","post", "put", "delete", "patch", "options", "head"]
            
            if method.lower() in valid_methods:
                
                # Create our clean Pydantic object
                endpoint = Endpoint(
                    path=path,
                    method=method.upper() # Standardize to uppercase (e.g., "GET")
                )
                endpoints.append(endpoint)
            else :
                print(f"Skipping non-HTTP key: {method} on path {path}")
                
    return endpoints

# ==========================================
# MANUAL TESTING (INTEGRATION TEST)
# ==========================================
