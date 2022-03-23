from fastapi import APIRouter

from app.api.endpoints import cors, ytdl, ytsr

api_router = APIRouter()
api_router.include_router(cors.router, prefix="/cors", tags=["cors"])
api_router.include_router(ytdl.router, prefix="/ytdl", tags=["ytdl"])
api_router.include_router(ytsr.router, prefix="/ytsr", tags=["ytsr"])