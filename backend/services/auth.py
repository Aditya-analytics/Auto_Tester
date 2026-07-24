from core.models import ApiConfig

def get_auth_headers(config: ApiConfig) -> dict:
    """
    Takes an ApiConfig object and returns the correct HTTP headers dictionary
    for the specified authentication type.
    """
    # 1. Edge Case: Auth is requested, but no credentials were provided
    if config.auth_type != "none" and not config.credentials:
        raise ValueError(f"Credentials are required for auth_type: '{config.auth_type}'")

    # 2. Map the auth_type to the correct header format
    if config.auth_type == "none":
        return {}
        
    elif config.auth_type == "bearer":
        return {"Authorization": f"Bearer {config.credentials}"}
    
    elif config.auth_type == "oauth2":
        return {"Authorization": f"Bearer {config.credentials}"}
        
    elif config.auth_type == "api_key":
        # Note: Some APIs use 'X-API-Key', others might use something else.
        return {"X-API-Key": config.credentials}
        
    elif config.auth_type == "basic":
        # Basic auth usually requires base64 encoding, but for this MVP,
        # we will assume the user provides the pre-encoded string.
        return {"Authorization": f"Basic {config.credentials}"}
        
    else:
        # Safety fallback
        return {}

# ==========================================
# MANUAL TESTING & ERROR SIMULATION
# ==========================================
