import uuid

from fastapi import APIRouter
from livekit.api import AccessToken, VideoGrants
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class TokenRequest(BaseModel):
    identity: str | None = None
    room: str = "voicd-room"


class TokenResponse(BaseModel):
    token: str
    url: str


@router.post("/token", response_model=TokenResponse)
async def create_token(req: TokenRequest):
    identity = req.identity or f"user-{uuid.uuid4().hex[:8]}"

    token = AccessToken(
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )
    token.identity = identity
    token.name = identity
    token.with_grants(VideoGrants(room_join=True, room=req.room))

    return TokenResponse(
        token=token.to_jwt(),
        url=settings.livekit_url,
    )
