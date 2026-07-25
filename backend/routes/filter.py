from fastapi import APIRouter, HTTPException
from core.models import BaseConfig, Endpoint
from services.discovery import discover_openapi
from services.parser import extract_endpoints
from services.filter import apply_safety_filter

router = APIRouter(
    prefix="/api",
    tags=["Endpoints"]
)

@router.post("/endpoints", response_model=list[Endpoint])
def get_filtered_endpoints(config: BaseConfig):
    """
    Modules 2, 3 & 5 integration endpoint.
    Accepts the base URL, discovers the raw OpenAPI spec, parses it into 
    clean Endpoint objects, applies safety filters, and returns the result.
    """
    try:
        base_url_str = str(config.base_url)
        
        # Module 2: Discover
        raw_swagger = discover_openapi(base_url_str)
        
        # Module 3: Parse
        endpoints = extract_endpoints(raw_swagger)
        
        # Module 5: Filter
        # Extract security schemes for the filter to check auth types
        security_defs = raw_swagger.get("securityDefinitions", {})
        if not security_defs and "components" in raw_swagger:
            security_defs = raw_swagger["components"].get("securitySchemes", {})
            
        safe_endpoints = apply_safety_filter(endpoints, security_defs)
        
        return safe_endpoints
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
