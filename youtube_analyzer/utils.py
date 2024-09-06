import datetime
import os
import re
import tempfile
import time
from urllib.parse import urlparse
import colorama
import requests
import xml.etree.ElementTree as et
from .playlists import create_urls, get_videos_playlist, extract_meta_og_title, extract_meta_og_description, \
    extract_meta_og_image
from .adaptive_formats import FormatStream
colorama.init(autoreset=True)

YOUTUBE_PLAYER_ENDPOINT = "https://www.youtube.com/youtubei/v1/player"
YOUTUBE_PLAYER_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
YOUTUBE_CLIENT_VERSION = "17.43.36"
YOUTUBE_CLIENT_USER_AGENT = f"com.google.android.youtube/{YOUTUBE_CLIENT_VERSION} (Linux; U; Android 13)"
YOUTUBE_PLAYER_HEADERS = {
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": YOUTUBE_CLIENT_VERSION,
    "Origin": "https://www.youtube.com",
    "Content-Type": "application/json",
    "User-Agent": YOUTUBE_CLIENT_USER_AGENT
}


class VideoParser:
    def __init__(self, url: str):
        self.__url = url
        self.__data = self.__get_youtube_video_info

    @property
    def __get_youtube_video_info(self):
        url = self.__get_id(self.__url)
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
            return None
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
        captions = ''

        return {
            "video_id": video_id,
            "title": title,
            "thumbnails": thumbnails,
            "viewCount": viewCount,
            "shortDescription": shortDescription,
            "isLiveContent": isLiveContent,
            "isPrivate": isPrivate,
            'author': author,
            "captions": captions,
            "streams": streaming_data
        }

    @staticmethod
    def __get_id(url):
        """
        Obtém o ID do vídeo do YouTube a partir de uma URL.

        :param url: URL do vídeo do YouTube.
        :return: ID do vídeo do YouTube, ou None se não for possível extrair o ID.
        """
        # Expressão regular para capturar o ID do vídeo em diferentes tipos de URLs do YouTube
        regex = (
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'  # Captura o ID do vídeo (11 caracteres alfanuméricos)
        )
        match = re.search(regex, url)
        if match:
            video_id = match.group(1)  # Captura o ID do vídeo
            # Verifica se é uma URL de vídeo regular, transmissão ao vivo ou vídeo curto (shorts)
            if 'live/' in url:
                return f"https://www.youtube.com/live/{video_id}"
            elif 'shorts/' in url:
                return f"https://www.youtube.com/shorts/{video_id}"
            else:
                return f"https://www.youtube.com/embed/{video_id}"
        else:
            return None  # Retorna None se não encontrar correspondência

    @property
    def is_private(self):
        """verifica se o vídeo é privado"""
        data = self.__data
        return data.get('isPrivate', None)

    @property
    def description(self):
        """obter desrcrição"""
        data = self.__data
        return data.get('shortDescription', None)

    @property
    def viewCount(self):
        """visualizações"""
        data = self.__data
        return data.get('viewCount', None)

    @property
    def thumbnails(self):
        """obter uma lista de urls de thumbs do vídeo"""
        data = self.__data
        return data.get('thumbnails', None)

    @property
    def isLiveContent(self):
        """verifiar se é uma live"""
        data = self.__data
        return data.get('isLiveContent', None)

    @property
    def author(self):
        """obter autor"""
        data = self.__data
        return data.get('author', None)

    @property
    def uris_stream(self) -> FormatStream:
        """objeto de streams"""
        data = self.__data
        return FormatStream(streamingData=data.get('streams', {}))

    @property
    def title(self):
        data = self.__data
        return data.get('title', None)


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
            thumbnails = VideoParser(url).thumbnails
            title = VideoParser(url).title
            video = {"title": f"{index}.{title}", "url_watch": url, "thumbnails": thumbnails}
            videos.append(video)  # Adiciona o vídeo à lista
        counts = len(videos)
        return {'title': title_p,
                'description': description,
                'count': counts,
                'image': image,
                'is_private': None,
                'videos': videos}

    @staticmethod
    def __get_id(url: str) -> str:
        """
        Obtém o ID do vídeo do YouTube a partir de uma URL.

        :param url: URL do vídeo do YouTube.
        :return: ID do vídeo do YouTube, ou None se não for possível extrair o ID.
        """
        regex = (
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'
        )
        match = re.search(regex, url)
        if match:
            video_id = match.group(1)
            if 'live/' in url:
                return f"https://www.youtube.com/live/{video_id}"
            elif 'shorts/' in url:
                return f"https://www.youtube.com/shorts/{video_id}"
            else:
                return f"https://www.youtube.com/embed/{video_id}"
        return ''

    @staticmethod
    def __get_id_playlists(url: str) -> str:
        """
        :param url: url da playlist
        :return: id
        """
        regex = r'[?&]list=([a-zA-Z0-9_-]+)'
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return ''

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


class VideoMetadates:
    def get_video_info(self, url_video: str) -> VideoParser:
        """
        :param url_video: url do vídeo
        :return: Objeto
        """
        if not self.__is_valid(url=url_video):
            raise ValueError("url não é válida!")
        else:
            a = VideoParser(url=url_video)
            return a

    @staticmethod
    def __is_valid(url: str) -> bool:
        """Verifica se a URL fornecida é válida e pertence ao YouTube.

        Args:
            url (str): A URL a ser verificada.

        Returns:
            bool: True se a URL for válida e pertencer ao YouTube, False caso contrário.
        """
        if not url.startswith("https://"):
            return False
        regex = (
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'
        )
        return bool(re.search(regex, url))


class PlaylistMetadates:
    def get_playlist_info(self, playlist_url: str) -> ParserPlaylist:
        """
        ATENÇÃO ESTA AÇÃO VAI DEMORAR DEVIDO AS REQUISIÇÃO PARA OBTER TODOS OS ELEMENTOS DE UMA PLAYLIST,DEPENDENDO
        DO TAMANHO VAI SER DEMORADO... :param playlist_url: url da playlist :return: object
        """
        if not self.__is_valid(url=playlist_url):
            raise ValueError("url não é válida!")
        else:
            a = ParserPlaylist(playlist_url=playlist_url)
            return a

    @staticmethod
    def __is_valid(url: str) -> bool:
        """
        Verifica se a URL fornecida é válida e pertence ao YouTube (vídeo ou playlist).

        Args:
            url (str): A URL a ser verificada.

        Returns:
            bool: True se a URL for válida e pertencer ao YouTube, False caso contrário.
        """
        if not url.startswith("https://"):
            return False

        # Verifica se o domínio é do YouTube
        parsed_url = urlparse(url)
        if parsed_url.netloc not in ["www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be"]:
            return False

        # Expressão regular para verificar IDs de vídeos e playlists
        regex = (
            r'(?:youtube\.com\/(?:.*?\/)?(?:playlist\?list=|watch\?v=|e(?:mbed)?\/|shorts\/|live\/)?|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'  # ID de vídeo
            r'|playlist\?list=([a-zA-Z0-9_-]+)'  # ID de playlist
        )

        return bool(re.search(regex, url))


class CaptionsParser:
    def __init__(self, caption_tracks):
        self.caption_tracks = caption_tracks

    def get_languages(self):
        """Retorna um dicionário com os idiomas disponíveis"""
        dt = []
        for track in self.caption_tracks:
            d = {
                'lang': track['name']['runs'][0]['text'],
                'code': track['languageCode'],
                'url': track['baseUrl']
            }
            dt.append(d)
        return dt

    def __get_subtitle_url(self, language_code):
        """Retorna a URL da legenda para o código de idioma especificado."""
        for track in self.caption_tracks:
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
        lang_list = self.get_languages()
        output_file_name = 'captions_video'
        for item in lang_list:
            if item['code'] == language_code:
                output_file_name = item.get('lang')

        if not subtitle_url:
            raise ValueError(f"Legendas para o idioma '{language_code}' não encontradas.")
        if logs:
            debug('info', "Baixando legenda...", end=' ')
        try:
            response = requests.get(subtitle_url, stream=True)
            response.raise_for_status()  # Verifica por erros HTTP
        except requests.exceptions.RequestException as e:
            raise Exception(f" Erro ao baixar legendas: {e}")
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
        CaptionsParser.__convert_xml_to_srt(xml_input_file=temp_file_path, srt_file_name=out_file)
        if logs:
            debug("true", "\tOK!")
        os.remove(temp_file_path)
        if logs:
            time.sleep(1.5)
            debug('warn', f"Legendas salvas como: {output_file_name}")

    @staticmethod
    def __convert_xml_to_srt(xml_input_file, srt_file_name):
        tree = et.parse(xml_input_file)
        root = tree.getroot()

        with open(srt_file_name, 'w', encoding='utf-8') as srt_file:
            counter = 1
            for p in root.findall('.//p'):
                start_time = int(p.attrib['t'])
                duration = int(p.attrib.get('d', 0))
                end_time = start_time + duration

                # Formatar o tempo no formato SRT (horas:minutos:segundos,milissegundos)
                start_time_srt = CaptionsParser.__format_time(start_time)
                end_time_srt = CaptionsParser.__format_time(end_time)

                # Se p.text for None, tentamos pegar o texto das subtags <s>
                if p.text is not None:
                    text = re.sub(r'<.*?>', '', p.text).replace("\n", " ")  # Remover tags e substituir quebras de linha
                else:
                    # Caso o texto esteja nas subtags <s>, concatenamos o texto de cada subtag
                    text = ''.join([s.text if s.text is not None else '' for s in p.findall('.//s')])

                # Formatar o conteúdo como uma legenda SRT
                srt_file.write(f"{counter}\n")
                srt_file.write(f"{start_time_srt} --> {end_time_srt}\n")
                srt_file.write(f"{text.strip()}\n\n")
                counter += 1

    @staticmethod
    def __format_time(time_ms):
        """Converte o tempo de milissegundos para o formato SRT"""
        hours = time_ms // (1000 * 60 * 60)
        minutes = (time_ms // (1000 * 60)) % 60
        seconds = (time_ms // 1000) % 60
        milliseconds = time_ms % 1000
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


class Captions:
    def __init__(self, url_video: str, hl='en', gl='US', timeZone="America/Los_Angeles"):
        """
        :type url_video: str
        :param url_video: url do video
        :param hl: ex: pt,en
        :param gl: BR,..
        :param timeZone:
        """
        self.timeZone = timeZone
        self.gl = gl
        self.hl = hl
        self.__url = url_video
        self.__data = self.__get_youtube_video_info

    @property
    def __get_youtube_video_info(self):
        url_video = self.__get_id(self.__url)
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
                    "hl": self.hl,
                    "gl": self.gl,
                    "timeZone": self.timeZone,
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
            return None
        captions_dict = data.get('captions', {})
        playerCaptionsTracklistRenderer = captions_dict['playerCaptionsTracklistRenderer']
        captionTracks = playerCaptionsTracklistRenderer['captionTracks']
        return {
            "captionTracks": captionTracks
        }

    @staticmethod
    def __get_id(url_video):
        """
        Obtém o ID do vídeo do YouTube a partir de uma URL.

        :param url_video: URL do vídeo do YouTube.
        :return: ID do vídeo do YouTube, ou None se não for possível extrair o ID.
        """
        # Expressão regular para capturar o ID do vídeo em diferentes tipos de URLs do YouTube
        regex = (
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'  # Captura o ID do vídeo (11 caracteres alfanuméricos)
        )
        match = re.search(regex, url_video)
        if match:
            video_id = match.group(1)  # Captura o ID do vídeo
            # Verifica se é uma URL de vídeo regular, transmissão ao vivo ou vídeo curto (shorts)
            if 'live/' in url_video:
                return f"https://www.youtube.com/live/{video_id}"
            elif 'shorts/' in url_video:
                return f"https://www.youtube.com/shorts/{video_id}"
            else:
                return f"https://www.youtube.com/embed/{video_id}"
        else:
            return None  # Retorna None se não encontrar correspondência

    @property
    def captions_in_video(self) -> CaptionsParser:
        """verifica captionTracks"""
        data = self.__data
        ca = CaptionsParser(data.get('captionTracks', {}))
        return ca


def debug(type: str, msg: str, end='\n'):
    """Exibe mensagens de depuração com cores baseadas no tipo.

    Args:
        type (str): Tipo da mensagem (erro, info, warn).
        msg (str): Mensagem a ser exibida.
        end (str, optional): String a ser impressa após a mensagem. Padrão é '\n'.
    """
    colors = {
        'erro': colorama.Fore.LIGHTRED_EX,
        'info': colorama.Fore.LIGHTCYAN_EX,
        'warn': colorama.Fore.LIGHTYELLOW_EX,
        'true': colorama.Fore.LIGHTGREEN_EX
    }

    # Obter a cor com base no tipo
    color = colors.get(type, colorama.Fore.RESET)

    # Imprimir a mensagem com a cor especificada
    print(color + msg, end=end)



