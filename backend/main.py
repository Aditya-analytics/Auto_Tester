from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Explicitly load environment variables from .env
load_dotenv()

from routes.discovery import router as discovery_router
from routes.filter import router as filter_router
from routes.generator import router as generator_router
from routes.executor import router as executor_router
from routes.report import router as report_router
from routes.explainer import router as explainer_router
from routes.test_endpoints import router as test_endpoints_router

app = FastAPI(
    title="TestPilot AI Backend",
    description="Backend services for discovery and test generation.",
    version="2.0.0"
)

# Configure CORS so the React frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000","http://localhost:5173","http://localhost:5174"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our routes
app.include_router(discovery_router)
app.include_router(filter_router)
app.include_router(generator_router)
app.include_router(executor_router)
app.include_router(report_router)
app.include_router(explainer_router)
app.include_router(test_endpoints_router)

@app.get("/")
async def root():
    return {"message": "TestPilot AI Backend is running!"}
