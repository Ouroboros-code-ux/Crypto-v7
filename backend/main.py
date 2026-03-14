from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from .limiter import limiter
from .database import init_db
from .routers import auth, scan, report, web, blockchain_routes
import os

init_db()

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CryptoShield AI", docs_url="/api/docs")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Mount Static Files (css, videos, etc.) from the root
# IMPORTANT: We do this BEFORE including routers to ensure assets are reachable
app.mount("/static", StaticFiles(directory="."), name="static")

# Hardened CORS Policy: Only allow requests from our frontend.
# In production, this should be set to your actual domain.
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"], # Restrict headers
)

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(report.router)
app.include_router(web.router)
app.include_router(blockchain_routes.router)
