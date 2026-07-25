from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr

router = APIRouter(
    prefix="/api/test",
    tags=["Test Endpoints"]
)

class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="The user's email address.",
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ..., 
        min_length=8, 
        description="A strong password.",
        json_schema_extra={"example": "SuperSecret123!"}
    )
    username: str = Field(
        ..., 
        min_length=3,
        description="A unique username.",
        json_schema_extra={"example": "testuser99"}
    )

class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="The registered user's email address.",
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ..., 
        description="The user's password.",
        json_schema_extra={"example": "SuperSecret123!"}
    )

@router.post(
    "/register", 
    summary="Register a new user",
    description="This endpoint is intentionally designed to ALWAYS fail to test the AI Test Explainer.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Validation error or username taken"}
    }
)
def fake_register(request: RegisterRequest):
    # Intentionally failing 100% of the time
    raise HTTPException(
        status_code=400, 
        detail="Username is already taken by another user in the system."
    )

@router.post(
    "/login", 
    summary="User Login",
    description="This endpoint is intentionally designed to ALWAYS fail to test the AI Test Explainer.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"}
    }
)
def fake_login(request: LoginRequest):
    # Intentionally failing 100% of the time
    raise HTTPException(
        status_code=401, 
        detail="Invalid credentials provided. Please check your email and password."
    )
