# Exceções da biblioteca Youtube Analyzer.


class YoutubeAnalyzerExceptions(Exception):
    """
    Exceção base para a biblioteca Youtube Analyzer.
    """

    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return super().__str__()


class InvalidIdUrlYoutube(YoutubeAnalyzerExceptions):
    """
    Exceção levantada para IDs ou URLs inválidos do YouTube.
    """

    def __init__(self, message: str = "Esta url não é de um Vídeo ou Playlist do YouTube!"):
        super().__init__(message)


class NotCaptions(YoutubeAnalyzerExceptions):
    """
    Exceção levantada quando um vídeo não possui legendas.
    """

    def __init__(self, message: str = "O vídeo não possui legendas!"):
        super().__init__(message)


class YoutubeRequestError(YoutubeAnalyzerExceptions):
    """
    Exceção levantada quando ocorre um erro em uma requisição à API do YouTube.
    """

    def __init__(self, message: str = "Erro ao realizar requisição!"):
        super().__init__(message)


class TranslationNotRequiredError(YoutubeAnalyzerExceptions):
    """
    Exceção levantada quando a tradução é desnecessária, pois o idioma de origem
    é igual ao idioma de destino.
 """

    def __init__(self, message: str = "Não é possível traduzir pois este já é o idioma da legenda!"):
        super().__init__(message)


class InvalidPlaylistError(YoutubeAnalyzerExceptions):
    """
    Exceção levantada quando uma playlist é privada ou inválida.
    """

    def __init__(self, message: str = "A playlist é privada ou inválida! Verifique a url fornecida."):
        super().__init__(message)


class TransCribeError(YoutubeAnalyzerExceptions):
    """
    Exceção levantada quando não foi possível obter a trasncrição
    """

    def __init__(self, message: str = "Não foi posível obter a trasncrição do vídeo!"):
        super().__init__(message)
