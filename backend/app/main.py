from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.token import router as token_router
from app.config import settings

app = FastAPI(title="VoiceOps AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
