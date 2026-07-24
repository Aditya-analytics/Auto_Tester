from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.discovery import router as discovery_router
from routes.filter import router as filter_router
from routes.generator import router as generator_router
from routes.executor import router as executor_router

app = FastAPI(
    title="API Test Agent V2 Backend",
    description="Backend services for discovery and test generation.",
    version="2.0.0"
)

# Configure CORS so the React frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our routes
app.include_router(discovery_router)
app.include_router(filter_router)
app.include_router(generator_router)
app.include_router(executor_router)

@app.get("/")
