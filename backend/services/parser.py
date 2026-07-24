from core.models import Endpoint

def extract_endpoints(swagger_data: dict) -> list[Endpoint]:
    """
    Module 3 & 4: Parser + Extractor
    Extracts only the useful metadata with minimal complexity.
    Acts as the Single Source of Truth for the UI and AI.
    """
    endpoints = []
    
    # Global security schemes in Swagger 2.0 / OpenAPI 3.0
    global_security = swagger_data.get("security", [])
    has_global_security = len(global_security) > 0
    
    paths = swagger_data.get("paths", {})
    
    for path, path_data in paths.items():
        for method, operation in path_data.items():
            
            valid_methods = ["get", "post", "put", "delete", "patch", "options", "head"]
            if method.lower() not in valid_methods:
                continue
                
            # 1. Basic Metadata
            summary = operation.get("summary")
            description = operation.get("description")
            tags = operation.get("tags", [])
            parameters = operation.get("parameters", [])
            
            # 2. Authentication
            method_security = operation.get("security")
            auth_required = False
            auth_type = None
            
            # If the method explicitly declares security, or if there's global security
            if method_security is not None:
                if len(method_security) > 0:
                    auth_required = True
                    auth_type = list(method_security[0].keys())[0] if method_security[0] else None
            elif has_global_security:
                auth_required = True
                auth_type = list(global_security[0].keys())[0] if global_security[0] else None

            # 3. Request Body Schema & Content-Type
            request_schema = None
            content_type = None
            
            # Swagger 2.0 uses 'consumes' or 'in: body' parameters
            if "consumes" in operation and len(operation["consumes"]) > 0:
                content_type = operation["consumes"][0]
            
            for param in parameters:
                if param.get("in") == "body":
                    request_schema = param.get("schema")
                    if not content_type:
                        content_type = "application/json" # fallback
                    break
            
            # OpenAPI 3.0 uses 'requestBody'
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})
                if content:
                    content_type = list(content.keys())[0] # e.g. application/json
                    request_schema = content[content_type].get("schema")

            # 4. Response Codes
            responses = []
            for status_code in operation.get("responses", {}).keys():
                if status_code.isdigit():
                    responses.append(int(status_code))
            
            # Create our beautiful V2 Canonical Endpoint
            endpoint = Endpoint(
                path=path,
                method=method.upper(),
                summary=summary,
                description=description,
                tags=tags,
                auth_required=auth_required,
                auth_type=auth_type,
                content_type=content_type,
                parameters=parameters,
                request_schema=request_schema,
                responses=responses
            )
            endpoints.append(endpoint)
            
    return endpoints
