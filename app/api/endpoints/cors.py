import httpx
from fastapi import APIRouter, Request
from fastapi.responses import (StreamingResponse, JSONResponse)
from starlette.background import BackgroundTask
from urllib.parse import unquote
from pydantic import AnyHttpUrl

client = httpx.AsyncClient()
router = APIRouter()


@router.get("/play")
async def cors(url: AnyHttpUrl, request: Request):
    url = unquote(str(request.url).split('url=')[1])
    try:
        req = client.build_request("GET", url)
        r = await client.send(req, stream=True)
        return StreamingResponse(r.aiter_bytes(),
                                 background=BackgroundTask(r.aclose))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
