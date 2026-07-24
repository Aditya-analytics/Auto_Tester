from fastapi import APIRouter, HTTPException
from core.models import BaseConfig
from services.discovery import discover_openapi

router = APIRouter(
    prefix="/api",
    tags=["Discovery"]
)

@router.post("/discover")
async def discover_api(config: BaseConfig):
    """
    Module 1 & 2 integration endpoint.
    Accepts the base URL, attempts to discover the OpenAPI spec, 
    and returns the detected version or throws an error.
    """
    try:
        # Convert Pydantic HttpUrl to string for our discovery service
        base_url_str = str(config.base_url)
        
        # Module 2: Discover OpenAPI documentation
        raw_swagger = discover_openapi(base_url_str)
        
        # Extract version
        version = raw_swagger.get("openapi") or raw_swagger.get("swagger") or "Unknown"
        
        return {
            "success": True,
            "message": "OpenAPI documentation discovered successfully!",
            "version": version
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
