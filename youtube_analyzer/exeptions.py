
class YoutubeAnalyzerExceptions(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        """
        Retorna a representação em string da exceção.

        Returns:
            str: Mensagem de erro formatada com detalhes adicionais, se presentes.
        """

        return super().__str__()
