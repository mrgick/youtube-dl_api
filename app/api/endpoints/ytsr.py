from fastapi import APIRouter, Query
from youtubesearchpython import __version__ as ytsr_version
from youtubesearchpython.__future__ import StreamURLFetcher, Video, Playlist, VideosSearch, PlaylistsSearch
from pydantic import AnyHttpUrl
from datetime import datetime, timedelta

router = APIRouter()


class StreamURLFetcherDate(StreamURLFetcher):

    def __init__(self):
        self.checkWait = 3600
        self.lastCheck = None
        super().__init__()

    async def updateJS(self):
        date = datetime.now()
        if not self.lastCheck:
            self.lastCheck = date
            await self.getJavaScript()
        else:
            if date - self.lastCheck > timedelta(seconds=self.checkWait):
                await self.getJavaScript()


fetcher = StreamURLFetcherDate()


@router.on_event("startup")
async def ytsr_init():
    await fetcher.updateJS()


@router.get('/version')
async def version():
    return {'youtube-search-python': ytsr_version}


@router.get('/info')
async def info(url: AnyHttpUrl,
               playlist: bool = False,
               info: bool = True,
               formats: bool = True):
    result = {}
    if playlist:
        if info and formats:
            result = await Playlist.get(url)
        elif info and not formats:
            result = await Playlist.getInfo(url)
        elif not info and formats:
            result = await Playlist.getVideos(url)
    else:
        if info and formats:
            result = await Video.get(url)
        elif info and not formats:
            result = await Video.getInfo(url)
        elif not info and formats:
            result = await Video.getFormats(url)

    return result


@router.get('/search')
async def search(keyword: str,
                 playlist: bool = False,
                 limit: int = Query(..., ge=1, lt=10)):
    result = {}
    if playlist:
        search = PlaylistsSearch(keyword, limit)
    else:
        search = VideosSearch(keyword, limit)
    result = await search.next()
    return result


@router.get('/get_direct_stream')
async def get_direct_stream(url: AnyHttpUrl,
                            itag: int = None):
    result = await Video.get(url)
    await fetcher.updateJS()
    if itag:
        result = await fetcher.get(result, itag)
        result = {"url": result}
    else:
        result = await fetcher.getAll(result)
    return result
