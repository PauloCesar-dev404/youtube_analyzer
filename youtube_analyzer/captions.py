import os
import re
import time

import requests
from .exeptions import YoutubeAnalyzerExceptions, YoutubeRequestError, NotCaptions, TranslationNotRequiredError,TransCribeError
from .utils import debug, YOUTUBE_PLAYER_HEADERS, YOUTUBE_PLAYER_ENDPOINT, YOUTUBE_CLIENT_VERSION, \
    YOUTUBE_CLIENT_USER_AGENT, YOUTUBE_PLAYER_KEY, get_id
from urllib.parse import urlparse, parse_qs, urlunparse


class Caption:
    def __init__(self, captions_data: dict):
        """objeto caption translate"""
        self._transcript = None
        self.__data = captions_data

    @property
    def lang(self) -> str:
        """código da linguagem"""
        return self.__data.get('code')

    @property
    def url(self) -> str:
        """url da legenda"""
        return self.__data.get('url')

    @property
    def content(self) -> str:
        """obtém o conteudo da legenda"""
        try:
            rep = requests.get(url=self.url)
            if rep.status_code == 200:
                return rep.text
            else:
                raise YoutubeRequestError("Não foi posível obter o conteúdo da legenda!")
        except Exception as e:
            raise YoutubeRequestError(f'Não foi posível obter o conteúdo da legenda! \"{e}\"')

    def download(self, output_dir, logs: bool = None) -> str:
        """
        Faz o download das legendas em texto para o idioma especificado.
        :param logs: exibir progresso
        :param output_dir: diretório para salvar a legenda
        :return: filepath
        """
        if not os.path.exists(output_dir):
            raise TypeError("este diretório não existe!")
        subtitle_url = self.url
        exte = '.srt'
        output_file_name = f'{self.lang}{exte}'
        if not subtitle_url:
            raise YoutubeAnalyzerExceptions(f"Legendas para o idioma não encontradas.")
        if logs:
            debug('info', "Baixando legenda...", end=' ')
        try:
            response = requests.get(subtitle_url, stream=True)
            if '<title>Error 404 (Not Found)!!' in response.text:
                raise YoutubeAnalyzerExceptions(f"Não foi possíevl baixar a legenda.. '{self.url}'")
        except requests.exceptions.RequestException as e:
            raise YoutubeAnalyzerExceptions(f"Erro ao baixar legendas: {e}")

        out_file = os.path.join(output_dir, output_file_name)

        # Salvando a legenda no arquivo
        with open(out_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        if logs:
            time.sleep(1.5)
            debug('true', f"Legendas salvas com sucesso!")
        return out_file

    def transcript(self) -> str:
        """
        Obtém o texto transcrito da legenda.

        Returns:
            str: O texto limpo da legenda.
        """
        return self._transcribe(srt_content=self.content)

    @staticmethod
    def _transcribe(srt_content):
        """
        Remove elementos desnecessários de uma legenda `.srt`, deixando apenas o texto.

        Args:
            srt_content (str): O conteúdo da legenda no formato `.srt`.

        Returns:
            str: O texto limpo da legenda.
        """
        try:
            # Remove números de sequência
            cleaned = re.sub(r"^\d+\s*$", "", srt_content, flags=re.MULTILINE)

            # Remove timestamps
            cleaned = re.sub(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", "", cleaned)

            # Remove linhas vazias adicionais
            cleaned = re.sub(r"\n{2,}", "\n", cleaned).strip()
        except Exception as e:
            raise TransCribeError()
        return cleaned


class TradutionCaptions:
    def __init__(self, url_caption):
        """traduzir legendas do youtube utilizando a própia api de tradução automática do youtube
        :param url_caption: url da legenda"""
        self.__url = url_caption

    def translate(self, tlang) -> Caption:
        """
        Traduzir legenda para um idioma....
        :param tlang: a lingugem que você deseja tarduzir por ex:'pt' -> português, 'en' -> 'inglês' etc...
        :return: objeto Caption
        """
        url_srv3 = self.__url
        new_url = TradutionCaptions.__convert_url_to_previous_format(url_srv3=url_srv3, tlang=tlang)
        dt = {'code': tlang, 'url': new_url}
        captions_object = Caption(captions_data=dt)
        return captions_object

    @staticmethod
    def __convert_url_to_previous_format(url_srv3, tlang):
        """criar a url da legenda traduzida"""
        # Parse a URL em partes
        parsed_url = urlparse(url_srv3)
        query_params = parse_qs(parsed_url.query)

        # Extrai os valores necessários da URL passada
        v = query_params.get("v", [""])[0]
        ei = query_params.get("ei", [""])[0]
        expire = query_params.get("expire", [""])[0]
        signature = query_params.get("signature", [""])[0]
        hl = query_params.get("hl", [""])[0]
        fmt = query_params.get("fmt", [""])[0]
        lang = query_params.get("lang", [""])[0]
        kind = query_params.get("kind", [None])[0]

        # Monta os parâmetros na ordem correta
        ordered_params = {
            "v": v,
            "ei": ei,
            "caps": "asr",
            "opi": "112496729",
            "exp": "xbt",
            "xoaf": "5",
            "hl": hl,
            "ip": "0.0.0.0",
            "ipbits": "0",
            "expire": expire,
            "sparams": "ip,ipbits,expire,v,ei,caps,opi,exp,xoaf",
            "signature": signature,
            "key": "yt8",
            "lang": lang,
            "fmt": 'srt',
            "xorb": "2",
            "xobt": "3",
            "xovt": "3",
            "tlang": tlang,
            "cbr": "Chrome",
            "cbrver": "131.0.0.0",
            "c": "WEB",
            "cver": "2.20241125.01.00",
            "cplayer": "UNIPLAYER",
            "cos": "Windows",
            "cosver": "10.0",
            "cplatform": "DESKTOP"
        }

        # Adiciona o 'kind' apenas se ele não for None
        if kind is not None:
            ordered_params["kind"] = kind

        # Monta a query string com os parâmetros
        ordered_query_string = "&".join(f"{key}={value}" for key, value in ordered_params.items())

        # Cria a nova URL com os parâmetros ordenados
        new_url = urlunparse(parsed_url._replace(query=ordered_query_string))
        if lang == tlang:
            raise TranslationNotRequiredError()
        return new_url


class CaptionsParser:
    def __init__(self, caption_tracks):
        """parsea trilhas de legendas
        :param caption_tracks: trilha de legenda"""
        if caption_tracks == 'Not Captions' or caption_tracks is None:
            raise NotCaptions()
        self.__caption_tracks = caption_tracks

    def get_caption_for_video(self) -> Caption:
        """Retorna as legendas disponíveis no vídeo"""
        dt = []
        if 'Not Legend' in self.__caption_tracks:
            raise NotCaptions()
        else:
            for track in self.__caption_tracks:
                d = {
                    'lang': track['name']['runs'][0]['text'],
                    'code': track['languageCode'],
                    'url': track['baseUrl'].replace('srv3', 'srt')
                }
                dt.append(d)
            cpts = Caption(captions_data=dt[0])
            return cpts

    def translate(self, tlang: str) -> Caption:
        """
        Traduza automaticamente as legendas de um vídeo do YouTube para um idioma de destino.

        Esta função utiliza o recurso de tradução automática do YouTube para traduzir as legendas
        de um vídeo. O idioma de destino deve ser especificado utilizando códigos de idioma
        no formato ISO 639-1 (por exemplo, "pt" para português ou "en" para inglês).

        Args:
            tlang (str): Código do idioma de destino no formato ISO 639-1.

        Returns:
            youtube_analyzer.parsers.Caption: Objeto legenda
        """
        url_srv3 = self.get_caption_for_video().url
        new_url = TradutionCaptions(url_caption=url_srv3)
        srt_y = new_url.translate(tlang=tlang)
        return srt_y


class Captions:
    def __init__(self, url_video: str):
        """
        :param url_video: url do video do youtube para obter as trilhas de legendas
        """
        self.__timeZone = "America/Los_Angeles"
        self.__gl = 'US'
        self.__hl = 'en'
        self.__url = url_video
        self.__data = self.__get_youtube_video_info

    @property
    def __get_youtube_video_info(self):
        """obter metadados do video"""
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
        if not response.status_code == 200:
            raise YoutubeRequestError()
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
        """Obtem as  Legendas inclusas no vídeo
        :return objeto CaptionsParser"""
        data = self.__data

        ca = CaptionsParser(data.get('captionTracks', 'Not Captions'))
        return ca
