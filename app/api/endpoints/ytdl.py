import yt_dlp
from yt_dlp.version import __version__ as yt_dlp_version
from fastapi import APIRouter
from typing import Optional
from pydantic import AnyHttpUrl

router = APIRouter()


class SimpleYDL(yt_dlp.YoutubeDL):

    def __init__(self, *args, **kargs):
        super(SimpleYDL, self).__init__(*args, **kargs)
        self.add_default_info_extractors()


@router.get('/extractors')
async def list_extractors():
    ie_list = [{
        'name': ie.IE_NAME,
        'working': ie.working(),
    } for ie in yt_dlp.gen_extractors()]
    return {"extractors": ie_list}


@router.get('/version')
async def version():
    return {'yt_dlp': yt_dlp_version}


@router.get("/info")
async def info(
    url: AnyHttpUrl,
    flatten: bool = False,
    format: Optional[str] = None,
    playliststart: Optional[int] = None,
    playlistend: Optional[int] = None,
    playlist_items: Optional[str] = None,
    playlistreverse: Optional[bool] = None,
    matchtitle: Optional[str] = None,
    rejecttitle: Optional[str] = None,
    writesubtitles: Optional[bool] = None,
    writeautomaticsub: Optional[bool] = None,
    allsubtitles: Optional[bool] = None,
    subtitlesformat: Optional[str] = None,
    subtitleslangs: Optional[list] = None,
):

    def get_videos(url, extra_params):
        ydl_params = {'format': 'best', 'cachedir': False}
        ydl_params.update(extra_params)
        ydl = SimpleYDL(ydl_params)
        res = ydl.extract_info(url, download=False)
        return res

    def flatten_result(result):
        r_type = result.get('_type', 'video')
        if r_type == 'video':
            videos = [result]
        elif r_type == 'playlist':
            videos = []
            for entry in result['entries']:
                videos.extend(flatten_result(entry))
        elif r_type == 'compat_list':
            videos = []
            for r in result['entries']:
                videos.extend(flatten_result(r))
        return videos

    extra_params = {
        'format': format,
        'playliststart': playliststart,
        'playlistend': playlistend,
        'playlist_items': playlist_items,
        'playlistreverse': playlistreverse,
        'matchtitle': matchtitle,
        'rejecttitle': rejecttitle,
        'writesubtitles': writesubtitles,
        'writeautomaticsub': writeautomaticsub,
        'allsubtitles': allsubtitles,
        'subtitlesformat': subtitlesformat,
        'subtitleslangs': subtitleslangs
    }

    for key in [x for x, _ in extra_params.items()]:
        if extra_params[key] is None:
            extra_params.pop(key)

    result = get_videos(url, extra_params)
    if flatten:
        result = flatten_result(result)
    return {
        'url': url,
        'videos': result,
    }