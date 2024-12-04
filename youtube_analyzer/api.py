from .exeptions import InvalidIdUrlYoutube
from .parsers import PlaylistContent, VideoContent
from .utils import is_valid


class VideoMetadates:
    @staticmethod
    def get_video_info(url_video: str) -> VideoContent:
        """
        Obtém informações de um vídeo do YouTube

        Args:
            url_video (str): Url do Vídeo padrão YouTube

        Returns:
            youtube_analyzer.parsers.VideoContent: Objeto com os dados do contidos video

        Examples:
            yt.get_video_info(url_video="https://www.youtube.com/watch?v=.......")


        """
        if not is_valid(url=url_video):
            raise InvalidIdUrlYoutube("url não é válida!")
        else:
            a = VideoContent(url=url_video)
            return a


class PlaylistMetadates:
    @staticmethod
    def get_playlist_info(playlist_url: str) -> PlaylistContent:
        """
        Obtém informações de uma playlist do YouTube.

        Args:
            playlist_url (str): Url da playlist padrão YouTube



        Returns:
            youtube_analyzer.parsers.PlaylistContent: Objeto contendo informações da playlist


        Examples:
            yt.get_playlist_info(playlist_url="https://www.youtube.com/playlist?list=.......")
        """
        if not is_valid(url=playlist_url):
            raise InvalidIdUrlYoutube()
        else:
            a = PlaylistContent(playlist_url=playlist_url)
            return a
