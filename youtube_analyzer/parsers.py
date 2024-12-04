import requests
from .adaptive_formats import Streams
from .captions import CaptionsParser, Captions
from .utils import YOUTUBE_PLAYER_HEADERS, YOUTUBE_PLAYER_ENDPOINT, YOUTUBE_CLIENT_VERSION, \
    YOUTUBE_CLIENT_USER_AGENT, YOUTUBE_PLAYER_KEY, get_id
from .exeptions import YoutubeAnalyzerExceptions
from .playlists import create_urls, get_videos_playlist, extract_meta_og_title, extract_meta_og_description, \
    extract_meta_og_image


class VideoContent:
    def __init__(self, url: str):
        """obtem detalhes de um video"""
        self.__url = url
        self.__data = self.__get_youtube_video_info

    @property
    def __get_youtube_video_info(self):
        url = get_id(self.__url)
        video_id = url.split("/")[-1]

        headers = YOUTUBE_PLAYER_HEADERS.copy()
        headers["Referer"] = url

        params = {
            "token": YOUTUBE_PLAYER_KEY,
            "prettyPrint": "false"
        }

        payload = {
            "context": {
                "client": {
                    "clientName": "ANDROID",
                    "clientVersion": YOUTUBE_CLIENT_VERSION,
                    "androidSdkVersion": 33,
                    "userAgent": YOUTUBE_CLIENT_USER_AGENT,
                    "hl": "pt",
                    "gl": "BR",
                    "timeZone": "America/Sao_Paulo",
                    "utcOffsetMinutes": 0
                }
            },
            "playbackContext": {
                "contentPlaybackContext": {
                    "html5Preference": "HTML5_PREF_WANTS"
                }
            },
            "videoId": video_id
        }

        response = requests.post(YOUTUBE_PLAYER_ENDPOINT, headers=headers, params=params, json=payload)
        data = response.json()

        playability_status = data.get("playabilityStatus", {})
        status = playability_status.get("status")
        if status != "OK":
            raise YoutubeAnalyzerExceptions("Não foi possível obter detalhes do vídeo!")
        streaming_data = data.get("streamingData", {})
        self.__formats = streaming_data.get("formats", [])
        video_details = data.get("videoDetails", {})
        title = video_details.get("title", "")
        detalhes = data['videoDetails']
        shortDescription = detalhes.get('shortDescription', [])
        isLiveContent = detalhes.get("isLiveContent", None)
        isPrivate = detalhes.get("isPrivate", None)
        author = detalhes.get("author", None)
        thumbnail = detalhes.get('thumbnail', {})
        thumbnails = thumbnail.get('thumbnails', [])
        viewCount = detalhes.get("viewCount", 0)

        return {
            "video_id": video_id,
            "title": title,
            "thumbnails": thumbnails,
            "viewCount": viewCount,
            "shortDescription": shortDescription,
            "isLiveContent": isLiveContent,
            "isPrivate": isPrivate,
            'author': author,
            "streams": streaming_data
        }

    @property
    def is_private(self):
        """verifica se o vídeo é privado"""
        data = self.__data
        return data.get('isPrivate', 'Not IsPrivate')

    @property
    def description(self):
        """obter desrcrição"""
        data = self.__data
        return data.get('shortDescription', 'Not Descriptions')

    @property
    def viewCount(self):
        """visualizações"""
        data = self.__data
        return data.get('viewCount', 'Not Views')

    @property
    def thumbnails(self):
        """obter uma lista de urls de thumbs do vídeo"""
        data = self.__data
        return data.get('thumbnails', 'Not thumbnails')

    @property
    def isLiveContent(self):
        """verifiar se é uma live"""
        data = self.__data
        return data.get('isLiveContent', 'Not IsLive')

    @property
    def author(self):
        """obter autor"""
        data = self.__data
        return data.get('author', 'Not Author')

    @property
    def uris_stream(self) -> Streams:
        """objeto de streams"""
        data = self.__data
        return Streams(streamingData=data.get('streams', 'Not Streams'))

    @property
    def title(self):
        data = self.__data
        return data.get('title', 'Not title')

    @property
    def Captions(self) -> CaptionsParser:
        """obter objeto captions"""
        caption = Captions(url_video=self.__url)
        return caption.captions_in_video


class PlaylistContent:
    def __init__(self, playlist_url: str):
        self.__url_playlist = playlist_url
        self.__data = self.__get_youtube_playlist_info

    @property
    def __get_youtube_playlist_info(self):
        playlist_url = get_videos_playlist(playlist_url=self.__url_playlist)
        if playlist_url is None:
            return {'title': '', 'description': '', 'count': 0, 'image': '',
                    'is_private': True, 'videos': [], 'channel_name': '', 'last_updated': '', 'views': ''}
        urls = create_urls(playlist_url)
        videos = []  # Cria uma lista para armazenar todos os vídeos
        title_p = extract_meta_og_title(playlist_url=self.__url_playlist)
        description = extract_meta_og_description(self.__url_playlist)
        image = extract_meta_og_image(playlist_url=self.__url_playlist)
        views = playlist_url.get('views')
        channel_name = playlist_url.get('channel_name')
        last_updated = playlist_url.get('last_updated')
        for e in urls:
            url = e.get('url')
            index = e.get("index")
            thumbnails = e.get('thumbnail')
            title = e.get('title')
            video = {"title": f"{index}.{title}", "url_watch": url, "thumbnails": thumbnails}
            videos.append(video)

        counts = len(videos)
        return {'title': title_p,
                'description': description,
                'count': counts,
                'image': image,
                'is_private': None,
                'last_updated': last_updated,
                'views': views,
                'channel_name': channel_name,
                'videos': videos}

    def get_all_videos(self) -> list[dict]:
        """obter todos os vídeos da playlist"""
        dt = self.__data
        return dt.get('videos')

    @property
    def playlist_name(self) -> str:
        """obter nome da playlist"""
        dt = self.__data
        return dt.get('title')

    @property
    def description(self) -> str:
        """obter descrição da playlist"""
        dt = self.__data
        return dt.get('description')

    @property
    def count(self) -> str:
        """obter a quantidade de vídeos da playlist"""
        dt = self.__data
        return dt.get('count')

    @property
    def image(self) -> str:
        """obter imagem da playlist"""
        dt = self.__data
        return dt.get('image')

    @property
    def is_private(self) -> bool:
        """verifica se é privada"""
        dt = self.__data
        return dt.get('is_private')

    @property
    def last_updated(self) -> str:
        """ultima modificação"""
        return self.__data.get('last_updated')

    @property
    def views(self) -> str:
        """visualozações"""
        return self.__data.get('views')

    @property
    def channel_name(self) -> str:
        """canal de origem da playlist"""
        return self.__data.get('channel_name')
