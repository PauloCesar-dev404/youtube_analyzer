from .api import is_valid
from .exeptions import YoutubeAnalyzerExceptions
from .parsers import ParserPlaylist, VideoParser


class VideoMetadates:
    @staticmethod
    def get_video_info(url_video: str) -> VideoParser:
        """
        :param url_video: url do vídeo
        :return: Objeto
        """
        if not is_valid(url=url_video):
            raise YoutubeAnalyzerExceptions("url não é válida!")
        else:
            a = VideoParser(url=url_video)
            return a


class PlaylistMetadates:
    @staticmethod
    def get_playlist_info(playlist_url: str) -> ParserPlaylist:
        """
        ATENÇÃO ESTA AÇÃO VAI DEMORAR DEVIDO AS REQUISIÇÃO PARA OBTER TODOS OS ELEMENTOS DE UMA PLAYLIST,DEPENDENDO
        DO TAMANHO VAI SER DEMORADO... :param playlist_url: url da playlist :return: object
        """
        if not is_valid(url=playlist_url):
            raise YoutubeAnalyzerExceptions("url não é válida!")
        else:
            a = ParserPlaylist(playlist_url=playlist_url)
            return a
