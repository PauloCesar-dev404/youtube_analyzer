import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable
import requests
from .utils import format_bytes, timestamp, ms_convert, mon_ste, convert_bitrate_precise
from .exeptions import YoutubeAnalyzerExceptions


class VideoStream:
    """
    Representa um objeto de stream de vídeo com funcionalidades para
    carregar dados de URI e realizar o download em paralelo.
    """

    def __init__(self, uri):
        """
        Inicializa o objeto VideoStream carregando dados a partir da URI fornecida.

        :param uri: Dicionário contendo informações do vídeo, como URL, bitrate, qualidade, etc.
        """
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
        """
        Carrega os dados do vídeo a partir da URI fornecida.

        :param uri: Dicionário contendo informações sobre o vídeo.
        :return: Dicionário com os dados do vídeo padronizados.
        """
        self.__data = {
            'itag': uri.get('itag', 'Not itag'),
            'url': uri.get('url', 'Not Url'),
            'mimeType': uri.get('mimeType', 'Not MimeType'),
            'bitrate': uri.get('bitrate', 'Not Bitrate'),
            'width': uri.get('width', 'Not Width'),
            'height': uri.get('height', 'Not Height'),
            'initRange': uri.get('initRange', 'Not InitRange'),
            'indexRange': uri.get('indexRange', 'Not indexRange'),
            'lastModified': uri.get('lastModified', 'Not lastModified'),
            'contentLength': uri.get('contentLength', 'Not contentLength'),
            'quality': uri.get('quality', 'Not quality'),
            'fps': uri.get('fps', 'Not fps'),
            'qualityLabel': uri.get('qualityLabel', 'Not qualityLabel'),
            'projectionType': uri.get('projectionType', 'Not projectionType'),
            'averageBitrate': uri.get('averageBitrate', 'Not averageBitrate'),
            'approxDurationMs': uri.get('approxDurationMs', 'Not approxDurationMs'),
            'audioQuality': uri.get('audioQuality', 'Not audio'),
            'audioSampleRate': uri.get('audioSampleRate', 'Not audioSampleRate'),
            'audioChannels': uri.get("audioChannels", 'Not audioChannels')
        }
        return self.__data

    @property
    def itag(self):
        """Retorna o identificador do formato (itag) do vídeo."""
        return self.__data.get('itag')

    @property
    def url(self):
        """Retorna a URL do vídeo."""
        return self.__data.get('url')

    @property
    def mimeType(self):
        """Retorna o tipo MIME do vídeo."""
        return self.__data.get('mimeType')

    @property
    def bitrate(self):
        """Retorna o bitrate do vídeo em formato convertido."""
        return convert_bitrate_precise(self.__data.get('bitrate'))

    @property
    def width(self):
        """Retorna a largura do vídeo em pixels."""
        return self.__data.get('width')

    @property
    def height(self):
        """Retorna a altura do vídeo em pixels."""
        return self.__data.get('height')

    @property
    def initRange(self):
        """Retorna o intervalo inicial de bytes do vídeo."""
        return self.__data.get('initRange')

    @property
    def indexRange(self):
        """Retorna o intervalo de índice de bytes do vídeo."""
        return self.__data.get('indexRange')

    @property
    def lastModified(self):
        """Retorna a última data de modificação do vídeo, convertida para timestamp."""
        return timestamp(self.__data.get('lastModified'))

    @property
    def contentLength(self):
        """Retorna o tamanho do conteúdo do vídeo, formatado em bytes."""
        return format_bytes(self.__data.get('contentLength'))

    @property
    def quality(self):
        """Retorna a qualidade do vídeo."""
        return self.__data.get('quality')

    @property
    def fps(self):
        """Retorna a taxa de quadros por segundo (FPS) do vídeo."""
        return self.__data.get('fps')

    @property
    def qualityLabel(self):
        """Retorna o rótulo de qualidade do vídeo (ex.: 720p, 1080p)."""
        return self.__data.get('qualityLabel')

    @property
    def projectionType(self):
        """Retorna o tipo de projeção do vídeo."""
        return self.__data.get('projectionType')

    @property
    def averageBitrate(self):
        """Retorna o bitrate médio do vídeo."""
        return self.__data.get('averageBitrate')

    @property
    def approxDurationMs(self):
        """Retorna a duração aproximada do vídeo, convertida de milissegundos para um formato legível."""
        return ms_convert(self.__data.get('approxDurationMs'))

    @property
    def audioQuality(self):
        """Retorna a qualidade do áudio do vídeo."""
        return self.__data.get('audioQuality')

    @property
    def audioSampleRate(self):
        """Retorna a taxa de amostragem do áudio do vídeo."""
        return self.__data.get('audioSampleRate')

    @property
    def audioChannels(self):
        """Retorna o número de canais de áudio do vídeo (mono/estéreo)."""
        return mon_ste(self.__data.get('audioChannels'))

    def download_video(self, title: str,
                       output_dir: str = 'youtube_analyzer_downloads',
                       overwrite_output: bool = False,
                       logs: bool = None,
                       capture_chunks: Optional[Callable[[int], None]] = None,
                       connections: int = 32):
        """

        Faz o download de um arquivo de vídeo

        Args:
            title (str): Título de Saída do Vídeo.
            output_dir (str): Diretório onde Salvar o Vídeo.
            overwrite_output (bool): Sobrescreve o Vídeo se Existir.
            logs (bool): Exibe o progresso.
            capture_chunks (Optional[Callable[[int], None]]): Função de callback para capturar saidas em bytes(chunks) do download ela deve receber um int.
            connections (int): Número de conexões para baixar um vídeo mais rápido.


        Returns:
            uma string com o caminho do vídeo

        Examples:
            yt_videoStreams.download_video(title="exemplo", output_dir="exemplo", overwrite_output=True, logs=True)

        """
        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp4")
        if os.path.exists(file_path) and not overwrite_output:
            raise FileExistsError(f"Arquivo já existe: {file_path}")

        # Obter o tamanho total do arquivo
        response = requests.head(self.url, allow_redirects=True)
        total_size = int(response.headers.get('Content-Length', 0))
        if total_size == 0:
            raise ValueError("Erro ao determinar o tamanho do arquivo.")

        # Dividir em partes para download paralelo
        ranges = []
        chunk_size = total_size // connections
        for i in range(connections):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < connections - 1 else total_size - 1
            ranges.append((start, end))

        progress = [0] * connections  # Progresso por conexão

        def download_segment(start, end, temp_file, index):
            headers = {'Range': f"bytes={start}-{end}"}
            downloaded = 0
            with requests.get(self.url, headers=headers, stream=True) as r:
                with open(temp_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress[index] = downloaded
                            if capture_chunks:
                                capture_chunks(len(chunk))
                            if logs:
                                show_progress(sum(progress), total_size)

        def show_progress(current, total):
            bar_length = 40
            filled_length = int(bar_length * current / total)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            percentage = (current / total) * 100
            sys.stdout.write(f"\r[{bar}] {percentage:.2f}%")
            sys.stdout.flush()

        temp_files = []
        with ThreadPoolExecutor(max_workers=connections) as executor:
            futures = []
            for idx, (start, end) in enumerate(ranges):
                temp_file = f"{file_path}.part{idx}"
                temp_files.append(temp_file)
                futures.append(executor.submit(download_segment, start, end, temp_file, idx))
            for future in futures:
                future.result()  # Espera pelo término de todas as conexões

        # Combinar arquivos temporários
        with open(file_path, 'wb') as final_file:
            for temp_file in temp_files:
                with open(temp_file, 'rb') as f:
                    final_file.write(f.read())
                os.remove(temp_file)  # Apaga o arquivo temporário

        if logs:
            print("\nDownload completo!")
        return file_path


class AudioStream:
    """
    Classe para manipular e realizar operações em streams de áudio.

    Permite carregar dados de um URI, acessar propriedades do stream e fazer download de arquivos
    de áudio com múltiplas conexões simultâneas.
    """

    def __init__(self, uri: dict):
        """
        Inicializa uma instância da classe AudioStream.

        :param uri: Um dicionário contendo informações do URI do stream de áudio.
        """
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
        """
        Carrega os dados do URI e inicializa as propriedades do stream.

        :param uri: Um dicionário contendo informações do URI do stream de áudio.
        :return: Um dicionário com os dados do stream processados.
        """
        self.__data = {
            'itag': uri.get('itag', 'Not itag'),
            'url': uri.get('url', 'Not url'),
            'mimeType': uri.get('mimeType', 'Not mimeType'),
            'bitrate': uri.get('bitrate', 'Not bitrate'),
            'initRange': uri.get('initRange', 'Not initRange'),
            'indexRange': uri.get('indexRange', 'Not indexRange'),
            'lastModified': uri.get('lastModified', 0),
            'contentLength': uri.get('contentLength', 0),
            'quality': uri.get('quality', 'Not quality'),
            'projectionType': uri.get('projectionType', 'Not projectionType'),
            'averageBitrate': uri.get('averageBitrate', 'Not averageBitrate'),
            'highReplication': uri.get('highReplication', 'Not highReplication'),
            'audioQuality': uri.get('audioQuality', 'Not audioQuality'),
            'approxDurationMs': uri.get('approxDurationMs', 'Not approxDurationMs'),
            'audioSampleRate': uri.get('audioSampleRate', 'Not audioSampleRate'),
            'audioChannels': uri.get('audioChannels', 'Not audioChannels'),
            'loudnessDb': uri.get('loudnessDb', 'Not loudnessDb')
        }
        return self.__data

    # Propriedades do stream
    @property
    def itag(self):
        """Obtém o identificador do stream (itag)."""
        return self.__data.get('itag')

    @property
    def url(self):
        """Obtém a URL do stream."""
        return self.__data.get('url')

    @property
    def mimeType(self):
        """Obtém o tipo MIME do stream."""
        return self.__data.get('mimeType')

    @property
    def bitrate(self):
        """Obtém a taxa de bits (bitrate) do stream."""
        return convert_bitrate_precise(self.__data.get('bitrate'))

    @property
    def initRange(self):
        """Obtém o intervalo inicial do stream."""
        return self.__data.get('initRange')

    @property
    def indexRange(self):
        """Obtém o intervalo do índice do stream."""
        return self.__data.get('indexRange')

    @property
    def lastModified(self):
        """Obtém a data de última modificação do stream."""
        return timestamp(self.__data.get('lastModified'))

    @property
    def contentLength(self):
        """Obtém o tamanho do conteúdo do stream."""
        return format_bytes(self.__data.get('contentLength'))

    @property
    def quality(self):
        """Obtém a qualidade do stream."""
        return self.__data.get('quality')

    @property
    def projectionType(self):
        """Obtém o tipo de projeção do stream."""
        return self.__data.get('projectionType')

    @property
    def averageBitrate(self):
        """Obtém a taxa de bits média do stream."""
        return self.__data.get('averageBitrate')

    @property
    def highReplication(self):
        """Obtém a indicação de alta replicação do stream."""
        return self.__data.get('highReplication')

    @property
    def audioQuality(self):
        """Obtém a qualidade de áudio do stream."""
        return self.__data.get('audioQuality')

    @property
    def approxDurationMs(self):
        """Obtém a duração aproximada do stream em milissegundos."""
        return ms_convert(self.__data.get('approxDurationMs'))

    @property
    def audioSampleRate(self):
        """Obtém a taxa de amostragem de áudio do stream."""
        return self.__data.get('audioSampleRate')

    @property
    def audioChannels(self):
        """Obtém o número de canais de áudio do stream."""
        return mon_ste(self.__data.get('audioChannels'))

    @property
    def loudnessDb(self):
        """Obtém o nível de intensidade sonora (dB) do stream."""
        return self.__data.get('loudnessDb')

    def download_audio(self, title: str, output_dir: str = 'youtube_analyzer_downloads',
                       overwrite_output: bool = False, logs: bool = None,
                       capture_chunks: Optional[Callable[[int], None]] = None, connections: int = 32):
        """

        Faz o download de um arquivo de áudio

        Args:
            title (str): Título de Saída do áudio.
            output_dir (str): Diretório onde Salvar o áudio.
            overwrite_output (bool): Sobrescreve o áudio se Existir.
            logs (bool): Exibe o progresso.
            capture_chunks (Optional[Callable[[int], None]]): Função de callback para capturar saidas em bytes(chunks)
             do download ela deve receber um int.
            connections (int): Número de conexões para baixar um áudio mais rápido.


        Returns:
            uma string com o caminho do vídeo

        Examples:
            yt_videoStreams.download_video(title="exemplo", output_dir="exemplo", overwrite_output=True, logs=True)

        """
        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp3")  # Ajustado para extensão de áudio
        if os.path.exists(file_path) and not overwrite_output:
            raise FileExistsError(f"Arquivo já existe: {file_path}")

        # Obter informações do arquivo
        response = requests.head(self.url, allow_redirects=True)
        total_size = int(response.headers.get('Content-Length', 0))
        if total_size == 0:
            raise ValueError("Erro ao determinar o tamanho do arquivo.")

        # Dividir em partes para conexões simultâneas
        ranges = []
        chunk_size = total_size // connections
        for i in range(connections):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < connections - 1 else total_size - 1
            ranges.append((start, end))

        progress = [0] * connections  # Progresso por conexão

        def download_segment(start, end, temp_file, index):
            headers = {'Range': f"bytes={start}-{end}"}
            downloaded = 0
            with requests.get(self.url, headers=headers, stream=True) as r:
                with open(temp_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress[index] = downloaded
                            if capture_chunks:
                                capture_chunks(len(chunk))
                            if logs:
                                show_progress(sum(progress), total_size)

        def show_progress(current, total):
            bar_length = 40
            filled_length = int(bar_length * current / total)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            percentage = (current / total) * 100
            sys.stdout.write(f"\r[{bar}] {percentage:.2f}%")
            sys.stdout.flush()

        temp_files = []
        with ThreadPoolExecutor(max_workers=connections) as executor:
            futures = []
            for idx, (start, end) in enumerate(ranges):
                temp_file = f"{file_path}.part{idx}"
                temp_files.append(temp_file)
                futures.append(executor.submit(download_segment, start, end, temp_file, idx))
            for future in futures:
                future.result()  # Espera pelo término de todas as conexões

        # Combinar arquivos temporários
        with open(file_path, 'wb') as final_file:
            for temp_file in temp_files:
                with open(temp_file, 'rb') as f:
                    final_file.write(f.read())
                os.remove(temp_file)  # Apaga o arquivo temporário

        if logs:
            print("\nDownload completo!")
        return file_path


class Streams:
    """
    Classe para processar e filtrar fluxos de vídeo e áudio de dados de streaming.

    Esta classe facilita a análise de formatos adaptativos, extraindo informações
    como resoluções disponíveis, qualidades de áudio e fluxos específicos de mídia.
    """

    def __init__(self, streamingData):
        """
        Inicializa o objeto FormatStream com os dados de streaming fornecidos.

        :param streamingData: Dados brutos do streaming extraídos.
        :raises YoutubeAnalyzerExceptions: Caso 'adaptiveFormats' não esteja presente nos dados.
        """
        self.__data = streamingData
        self.__adaptiveFormats = self.__data.get('adaptiveFormats', [])
        self.__formats = self.__data.get('formats', [])

        self.__videos_streams_data = self.__load_videos_streams
        self.__audios_streams_data = self.__load_audio_streams

        if not self.__adaptiveFormats:
            raise YoutubeAnalyzerExceptions("Not adaptiveFormats")

    def __load_streams_by_mime(self, mime_types: list[str]) -> list[dict]:
        formats = []
        add = []
        for i in self.__adaptiveFormats + self.__formats:
            mimeType = i.get("mimeType", None)
            if any(mime in mimeType for mime in mime_types):
                if not i in add:
                    formats.append(i)
                    add.append(i)
        return formats

    def __load_videos_streams(self):
        """
        Carrega fluxos de vídeo disponíveis.

        :return: Lista de fluxos com MIME 'video/mp4' ou 'video/webm'.
        """
        return self.__load_streams_by_mime(['video/mp4', 'video/webm'])

    @property
    def __load_audio_streams(self):
        """
        Carrega fluxos de áudio disponíveis.

        :return: Lista de fluxos com MIME 'audio/mp4' ou 'audio/webm'.
        """
        return self.__load_streams_by_mime(['audio/mp4', 'audio/webm'])

    def get_resolutions(self) -> list[dict]:
        """
        Obtém todas as resoluções de vídeo disponíveis.

        Observação: Apenas resoluções de até 720p possuem áudio embutido.
        Resoluções mais altas têm faixas de áudio separadas.

    Returns:

        list[dict]: Lista de dicionários com as resoluções disponíveis.

    Examples:

        Your_Escope.get_resolutions()

    """
        resolutions = []
        mimeTypes_add = []
        for uri in self.__videos_streams_data():
            width = uri.get("width", None)
            height = uri.get("height", None)
            mimeType = uri.get("mimeType", None)
            if width and height and mimeType:
                resolution = f'{width}x{height}'
                dt = {"resolution": resolution, "typeUri": str(mimeType).split(';')[0]}
                if not dt in mimeTypes_add:
                    resolutions.append(dt)
                    mimeTypes_add.append(dt)
        return resolutions

    def filter_resolution(self, resolution_filter: str, typeuri: str) -> VideoStream:
        """

        Filtra por resolução um específica e obtém o Objeto Stream de um vídeo,para saber aplicar um filtro veja quais
         as resoluções estão disponíveis usando o método `get_resolutions()`

        Args:
            resolution_filter (str): A resolução que deseja
            typeuri (str): Tipo de Faixa


        Returns:

            youtube_analyzer.adaptive_formats.VideoStream: Objeto Stream de faixa de vídeo que contém em um vídeo.

        Examples:

            Your_Escope.filter_resolution(resolution_filter="1920x1080", typeuri="video/mp4")

        """
        try:
            width, height = map(int, resolution_filter.split('x'))
        except ValueError:
            raise YoutubeAnalyzerExceptions("Invalid resolution format. Expected format 'WIDTHxHEIGHT'.")

        for stream_data in self.__videos_streams_data():
            stream_width = int(stream_data.get('width', 0))
            stream_height = int(stream_data.get('height', 0))
            mime_type = stream_data.get('mimeType', None)

            if stream_width == width and stream_height == height and typeuri in str(mime_type).split(';')[0]:
                return VideoStream(uri=stream_data)

    def get_all_audios_quality(self) -> list[dict]:
        """

        Obtém todas qualiadades de áudio disponíveis no vídeo

        Returns:

            list[dict]: Uma lista de dicionários

        Examples:

            Your_Escope.get_all_audios_quality()

        """
        audios = []
        add = []
        for uri in self.__audios_streams_data:
            quality = uri.get("audioQuality", None)
            mimeType = uri.get("mimeType", None)
            if quality and mimeType:
                dt = {"audioQuality": quality, "typeAudio": str(mimeType).split(';')[0]}

                if not dt in add:
                    audios.append(dt)
                    add.append(dt)
        return audios

    def filter_audio_quality(self, audio_quality: str, type_audio: str) -> AudioStream:
        """

        Filtra por uma qualidade específica de áudio e obtém o Objeto Stream de um áudio,para saber aplicar um filtro veja quais
         as qualidades estão disponíveis usando o método `get_all_audios_quality()`

    Args:

        audio_quality (str): A qualidade que deseja.
        type_audio (str): Tipo de Faixa.


    Returns:

        youtube_analyzer.adaptive_formats.AudioStream: Objeto Stream de faixa de áudio de um vídeo.

    Examples:

        Your_Escope.filter_audio_quality(audio_quality="", type_audio="")

    """
        for stream_data in self.__audios_streams_data:
            audioQuality = stream_data.get('audioQuality', '')
            mime_type = stream_data.get('mimeType', '')
            if audioQuality == audio_quality and type_audio in str(mime_type).split(';')[0]:
                return AudioStream(uri=stream_data)

    def get_highest_resolution(self) -> VideoStream:
        """
        Encontra a maior resolução disponível no vídeo.

        Atenção As Resoluções de qualidade mais altas geralmente não possuem áudio embutido.

    Returns:

        youtube_analyzer.adaptive_formats.VideoStream: Objeto de Stream de um vídeo.

    Examples:

        Your_Escope.get_highest_resolution()

    """
        resolutions = self.get_resolutions()
        if not resolutions:
            raise YoutubeAnalyzerExceptions("Not resolutions in video...")

        highest_resolution = max(resolutions,
                                 key=lambda r: (int(r['resolution'].split('x')[0]), int(r['resolution'].split('x')[1])))
        return self.filter_resolution(resolution_filter=highest_resolution.get('resolution'),
                                      typeuri=highest_resolution.get('typeUri'))

    def get_best_audio_quality(self) -> AudioStream:
        """
        Obtém a melhor qualidade de áudio disponível.


        Returns:

            youtube_analyzer.adaptive_formats.AudioStream: Objeto Stream da faixa de áudio.

        Examples:

            Your_Escope.get_best_audio_quality()

    """
        quality_order = {
            'AUDIO_QUALITY_LOW': 1,
            'AUDIO_QUALITY_MEDIUM': 2,
            'AUDIO_QUALITY_HIGH': 3
        }
        best_quality = None
        best_audio = None
        audio_list = self.get_all_audios_quality()

        for audio in audio_list:
            quality = audio.get('audioQuality')
            if quality and (best_quality is None or quality_order.get(quality, 0) > quality_order.get(best_quality, 0)):
                best_quality = quality
                best_audio = audio

        return self.filter_audio_quality(audio_quality=best_audio.get('audioQuality'),
                                         type_audio=best_audio.get('typeAudio'))

    def get_format_contained_audio(self) -> VideoStream:
        """

        Obtém a Stream que contém áudio e vídeo


        Returns:

            youtube_analyzer.adaptive_formats.VideoStream: Objeto Stream contendo as informações da faixa

        Examples:

            yt.get_format_contained_audio()

        """
        f = max(self.__formats, key=lambda x: x['width'])
        return VideoStream(f)
