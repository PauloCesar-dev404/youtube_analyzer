import os
import tempfile
import time
import requests
from .adaptive_formats import FormatStream
from .api import debug, YOUTUBE_PLAYER_HEADERS, YOUTUBE_PLAYER_ENDPOINT, YOUTUBE_CLIENT_VERSION, \
    YOUTUBE_CLIENT_USER_AGENT, YOUTUBE_PLAYER_KEY, get_id, convert_xml_to_srt
from .exeptions import YoutubeAnalyzerExceptions
from .playlists import create_urls, get_videos_playlist, extract_meta_og_title, extract_meta_og_description, \
    extract_meta_og_image


class CaptionsParser:
    def __init__(self, caption_tracks):
        if caption_tracks == 'Not Captions' or caption_tracks is None:
            raise YoutubeAnalyzerExceptions("Not Captions")
        self.__caption_tracks = caption_tracks

    @property
    def get_languages(self) -> list[dict]:
        """Retorna ums lista de dicionários com os idiomas disponíveis"""
        dt = []
        if 'Not Legend' in self.__caption_tracks:
            return [{'caption': 'Not Captions'}]
        else:
            for track in self.__caption_tracks:
                d = {
                    'lang': track['name']['runs'][0]['text'],
                    'code': track['languageCode'],
                    'url': track['baseUrl']
                }
                dt.append(d)
            return dt

    def __get_subtitle_url(self, language_code):
        """Retorna a URL da legenda para o código de idioma especificado."""
        for track in self.__caption_tracks:
            if track['languageCode'] == language_code:
                return track['baseUrl']
        return None

    def download_subtitles(self, language_code, out_dir, logs: bool = None):
        """
        Faz o download das legendas em texto para o idioma especificado.
        :param logs:
        :param language_code: código do idioma
        :param out_dir: diretório para salvar a legenda
        :return:
        """
        if not os.path.exists(out_dir):
            raise TypeError("este diretório não existe!")
        subtitle_url = self.__get_subtitle_url(language_code)
        lang_list = self.get_languages
        output_file_name = 'captions_video'
        for item in lang_list:
            if item['code'] == language_code:
                output_file_name = item.get('lang')

        if not subtitle_url:
            raise YoutubeAnalyzerExceptions(f"Legendas para o idioma '{language_code}' não encontradas.")
        if logs:
            debug('info', "Baixando legenda...", end=' ')
        try:
            response = requests.get(subtitle_url, stream=True)
            response.raise_for_status()  # Verifica por erros HTTP
        except requests.exceptions.RequestException as e:
            raise YoutubeAnalyzerExceptions(f" Erro ao baixar legendas: {e}")
        # Armazenar o conteúdo XML como uma string
        xml_caption = response.text
        if logs:
            time.sleep(1.5)
            debug("true", "\tOK")
            time.sleep(0.4)
        if not output_file_name:
            return xml_caption
        out_file = os.path.join(out_dir, output_file_name)
        # Criar um arquivo temporário e escrever o XML nele
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode='w', encoding='utf-8') as temp_file:
            temp_file.write(xml_caption)
            temp_file_path = temp_file.name
        if logs:
            debug("info", "convertendo para srt....", end=" ")
            time.sleep(1.5)
        # Converter o XML para o formato SRT
        convert_xml_to_srt(xml_input_file=temp_file_path, srt_file_name=out_file)
        if logs:
            debug("true", "\tOK!")
        os.remove(temp_file_path)
        if logs:
            time.sleep(1.5)
            debug('warn', f"Legendas salvas como: {output_file_name}")


class Captions:
    def __init__(self, url_video: str, hl='en', gl='US', timeZone="America/Los_Angeles"):
        """
        :type url_video: str
        :param url_video: url do video
        :param hl: ex: pt,en
        :param gl: BR,..
        :param timeZone:
        """
        self.__timeZone = timeZone
        self.__gl = gl
        self.__hl = hl
        self.__url = url_video
        self.__data = self.__get_youtube_video_info

    @property
    def __get_youtube_video_info(self):
        url_video = get_id(self.__url)
        video_id = url_video.split("/")[-1]

        headers = YOUTUBE_PLAYER_HEADERS.copy()
        headers["Referer"] = url_video

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
                    "hl": self.__hl,
                    "gl": self.__gl,
                    "timeZone": self.__timeZone,
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
        response.raise_for_status()
        data = response.json()

        playability_status = data.get("playabilityStatus", {})
        status = playability_status.get("status")
        if status != "OK":
            raise YoutubeAnalyzerExceptions("Não foi possível obter detalhes do vídeo!")
        captions_dict = data.get('captions', {})
        playerCaptionsTracklistRenderer = captions_dict.get('playerCaptionsTracklistRenderer', {})
        captionTracks = playerCaptionsTracklistRenderer.get('captionTracks', 'Not Legend')

        return {
            "captionTracks": captionTracks
        }

    @property
    def captions_in_video(self) -> CaptionsParser:
        """Obtem objeto CaptionsParser com as  Legendas inclusas no vídeo"""
        data = self.__data

        ca = CaptionsParser(data.get('captionTracks', 'Not Captions'))
        return ca



class VideoParser:
    def __init__(self, url: str):
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
        response.raise_for_status()
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
    def uris_stream(self) -> FormatStream:
        """objeto de streams"""
        data = self.__data
        return FormatStream(streamingData=data.get('streams', 'Not Streams'))

    @property
    def title(self):
        data = self.__data
        return data.get('title', 'Not title')

    @property
    def captions(self) -> Captions:
        """obter objeto captions"""
        return Captions(url_video=self.__url)


class ParserPlaylist:
    def __init__(self, playlist_url: str):
        self.__url_playlist = playlist_url
        self.__data = self.__get_youtube_playlist_info

    @property
    def __get_youtube_playlist_info(self):
        playlist_url = get_videos_playlist(playlist_url=self.__url_playlist)
        if playlist_url is None:
            return {'title': None, 'description': None, 'count': 0, 'image': None,
                    'is_private': True, 'videos': []}
        urls = create_urls(playlist_url)
        videos = []  # Cria uma lista para armazenar todos os vídeos
        title_p = extract_meta_og_title(playlist_url=self.__url_playlist)
        description = extract_meta_og_description(self.__url_playlist)
        image = extract_meta_og_image(playlist_url=self.__url_playlist)
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
                'videos': videos}

    @property
    def get_all_videos(self):
        """obter todos os vídeos da playlist"""
        dt = self.__data
        return dt.get('videos')

    @property
    def playlist_name(self):
        """obter nome da playlist"""
        dt = self.__data
        return dt.get('title')

    @property
    def description(self):
        """obter descrição da playlist"""
        dt = self.__data
        return dt.get('description')

    @property
    def count(self):
        """obter a quantidade de vídeos da playlist"""
        dt = self.__data
        return dt.get('count')

    @property
    def image(self):
        """obter imagem da playlist"""
        dt = self.__data
        return dt.get('image')

    @property
    def is_private(self):
        """verifica se é privada"""
        dt = self.__data
        return dt.get('is_private')