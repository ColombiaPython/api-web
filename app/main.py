from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGIN_REGEX
from app.router import router as api_router

app = FastAPI(
    title="Python Colombia API",
    description="API for Python Colombia project",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)