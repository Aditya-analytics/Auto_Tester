from core.models import Endpoint

# Explicitly supported vs hidden authentication types according to V2 architecture
SUPPORTED_AUTH_TYPES = ["apiKey", "http", "oauth2"] # Note: OAuth2 is tricky, we might map to specific strings based on Swagger config
# Actually, the spec says Supported: None, API Key, Basic Auth, Bearer Token / JWT.
# Hidden: OAuth2, OpenID Connect, Mutual TLS, AWS Signature, Custom Auth.
# Let's map these to standard OpenAPI security scheme types/formats.

# OpenAPI types: "apiKey", "http" (scheme: basic, bearer), "oauth2", "openIdConnect"

RISKY_KEYWORDS = [
    "payment", "checkout", "refund", "wallet", "bank", 
    "withdraw", "transfer", "payout", "invoice", "reset", 
    "drop", "shutdown", "deleteall"
]

def apply_safety_filter(endpoints: list[Endpoint], swagger_security_schemes: dict) -> list[Endpoint]:
    """
    Module 5: Endpoint Safety Filter
    Evaluates each endpoint to see if we can support its authentication, 
    and checks if it performs dangerous actions (risky keywords).
    """
    filtered_endpoints = []
    
    for endpoint in endpoints:
        # Default assumptions
        endpoint.supported = True
        endpoint.unsupported_reason = None
        endpoint.risk_level = "safe"
        
        # 1. Evaluate Authentication Support
        if endpoint.auth_required and endpoint.auth_type:
            # Look up the definition in the global swagger schemes
            scheme_def = swagger_security_schemes.get(endpoint.auth_type, {})
            scheme_type = scheme_def.get("type", "").lower()
            
            # According to specs: Hide OAuth2, OpenID Connect, Mutual TLS, etc.
            if scheme_type in ["oauth2", "openidconnect", "mutualtls"]:
                endpoint.supported = False
                endpoint.unsupported_reason = f"Unsupported Auth Type: {scheme_type}"
            
            # Some APIs use weird custom auth types or AWS signature
            elif scheme_type not in ["apikey", "http", "basic"]:
                # petstore uses oauth2 which would trigger the above, but wait:
                # petstore_auth is oauth2 in the petstore swagger!
                # Since we are building this for learning, let's mark it as unsupported 
                # but STILL return it in the list so the UI can show it as grayed out!
                endpoint.supported = False
                endpoint.unsupported_reason = f"Unsupported Auth Type: {scheme_type}"
                
        # 2. Evaluate Risk Level
        path_lower = endpoint.path.lower()
        summary_lower = (endpoint.summary or "").lower()
        
        for keyword in RISKY_KEYWORDS:
            if keyword in path_lower or keyword in summary_lower:
                endpoint.risk_level = "high_risk"
                endpoint.supported = False
                endpoint.unsupported_reason = f"High Risk Keyword Detected: {keyword}"
                break # No need to check other keywords
                
        filtered_endpoints.append(endpoint)
        
    return filtered_endpoints

if __name__ == "__main__":
    from services.discovery import discover_openapi
    from services.parser import extract_endpoints
    
    raw = discover_openapi("https://petstore.swagger.io/v2")
    endpoints = extract_endpoints(raw)
    
    # We need the security definitions to know WHAT petstore_auth actually is
    security_defs = raw.get("securityDefinitions", {})
    
    processed_endpoints = apply_safety_filter(endpoints, security_defs)
    
    print("\n--- SAFETY FILTER RESULTS ---")
    for ep in processed_endpoints[:5]:
        print(f"{ep.method} {ep.path} -> Supported: {ep.supported}, Risk: {ep.risk_level}")
        if not ep.supported:
            print(f"  Reason: {ep.unsupported_reason}")
