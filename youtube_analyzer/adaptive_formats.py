import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable
import requests
from .api import debug, format_bytes, timestamp, ms_convert, mon_ste, convert_bitrate_precise
from .exeptions import YoutubeAnalyzerExceptions


class VideoStream:
    def __init__(self, uri):
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
        self.__data = {'itag': uri.get('itag', 'Not itag'),
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
        return self.__data.get('itag')

    @property
    def url(self):
        return self.__data.get('url')

    @property
    def mimeType(self):
        return self.__data.get('mimeType')

    @property
    def bitrate(self):
        return convert_bitrate_precise(self.__data.get('bitrate'))

    @property
    def width(self):
        return self.__data.get('width')

    @property
    def height(self):
        return self.__data.get('height')

    @property
    def initRange(self):
        return self.__data.get('initRange')

    @property
    def indexRange(self):
        return self.__data.get('indexRange')

    @property
    def lastModified(self):
        return timestamp(self.__data.get('lastModified'))

    @property
    def contentLength(self):
        return format_bytes(self.__data.get('contentLength'))

    @property
    def quality(self):
        return self.__data.get('quality')

    @property
    def fps(self):
        return self.__data.get('fps')

    @property
    def qualityLabel(self):
        return self.__data.get('qualityLabel')

    @property
    def projectionType(self):
        return self.__data.get('projectionType')

    @property
    def averageBitrate(self):
        return self.__data.get('averageBitrate')

    @property
    def approxDurationMs(self):
        return ms_convert(self.__data.get('approxDurationMs'))

    @property
    def audioQuality(self):
        return self.__data.get('audioQuality')

    @property
    def audioSampleRate(self):
        return self.__data.get('audioSampleRate')

    @property
    def audioChannels(self):
        return mon_ste(self.__data.get('audioChannels'))

    def download_video(self, title: str,
                       output_dir: str = 'youtube_analyzer_downloads',
                       overwrite_output: bool = False,
                       logs: bool = None,
                       capture_chunks: Optional[Callable[[int], None]] = None,
                       connections: int = 32):
        """
            Faz o download de um vídeo usando múltiplas conexões.

            :param logs: progresso
            :param title: Título do vídeo.
            :param output_dir: Diretório de saída onde o vídeo será salvo.
            :param overwrite_output: Se True, sobrescreve o arquivo se ele já existir.
            :param capture_chunks: Função de callback para capturar o andamento do download.
            :param connections: Número de conexões simultâneas.
            :return: file_path
            """
        if connections > 120:
            raise Warning("Esse número de conexões extrapolou! Use um valor menor ou igual a 120.")

        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp4")
        if os.path.exists(file_path) and not overwrite_output:
            raise FileExistsError(f"Arquivo já existe: {file_path}")

        # Obter o tamanho total do arquivo
        response = requests.head(self.url)
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
    def __init__(self, uri: dict):
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
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

    @property
    def itag(self):
        return self.__data.get('itag')

    @property
    def url(self):
        return self.__data.get('url')

    @property
    def mimeType(self):
        return self.__data.get('mimeType')

    @property
    def bitrate(self):
        return convert_bitrate_precise(self.__data.get('bitrate'))

    @property
    def initRange(self):
        return self.__data.get('initRange')

    @property
    def indexRange(self):
        return self.__data.get('indexRange')

    @property
    def lastModified(self):
        return timestamp(self.__data.get('lastModified'))

    @property
    def contentLength(self):
        return format_bytes(self.__data.get('contentLength'))

    @property
    def quality(self):
        return self.__data.get('quality')

    @property
    def projectionType(self):
        return self.__data.get('projectionType')

    @property
    def averageBitrate(self):
        return self.__data.get('averageBitrate')

    @property
    def highReplication(self):
        return self.__data.get('highReplication')

    @property
    def audioQuality(self):
        return self.__data.get('audioQuality')

    @property
    def approxDurationMs(self):
        return ms_convert(self.__data.get('approxDurationMs'))

    @property
    def audioSampleRate(self):
        return self.__data.get('audioSampleRate')

    @property
    def audioChannels(self):
        return mon_ste(self.__data.get('audioChannels'))

    @property
    def loudnessDb(self):
        return self.__data.get('loudnessDb')

    def download_audio(self, title: str,
                       output_dir: str = 'youtube_analyzer_downloads',
                       overwrite_output: bool = False,
                       logs: bool = None,
                       capture_chunks: Optional[Callable[[int], None]] = None,
                       connections: int = 32):
        """
            Faz o download de um arquivo de áudio utilizando múltiplas conexões simultâneas.

            :param title: Título do arquivo de áudio.
            :param output_dir: Diretório de saída onde o áudio será salvo.
            :param overwrite_output: Se True, sobrescreve o arquivo se ele já existir.
            :param logs:  para exibir o progresso.
            :param capture_chunks: Função de callback para capturar o andamento do download.
            :param connections: Número de conexões simultâneas.
            :return: file_path
            """
        if connections > 120:
            raise Warning("Esse número de conexões extrapolou! Use um valor menor ou igual a 120.")

        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp3")  # Ajustado para extensão de áudio
        if os.path.exists(file_path) and not overwrite_output:
            raise FileExistsError(f"Arquivo já existe: {file_path}")

        # Obter informações do arquivo
        response = requests.head(self.url)
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


class FormatStream:
    def __init__(self, streamingData):
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

    @property
    def __load_videos_streams(self):
        return self.__load_streams_by_mime(['video/mp4', 'video/webm'])

    @property
    def __load_audio_streams(self):
        return self.__load_streams_by_mime(['audio/mp4', 'audio/webm'])

    @property
    def get_resolutions(self) -> list[dict]:
        """
        obter todas resoluções disponíveis,tenha atenção pois como políticas do youtube apenas resolução de até 720p
        tem audio embutido as demais a faixa de áudio é separada.

        :return: uma lista com as resoluçoes e seus mimeType
        """
        resolutions = []
        mimeTypes_add = []
        for uri in self.__videos_streams_data:
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
        filtre e obtenha apenas uma uri da stream:

        :param resolution_filter: EX: 1920x1080
        :param typeuri: EX: video/mp4
        :return: objeto VideoStream
        """
        # Validate and parse the resolution_filter
        try:
            width, height = map(int, resolution_filter.split('x'))
        except ValueError:
            raise YoutubeAnalyzerExceptions("Invalid resolution format. Expected format 'WIDTHxHEIGHT'.")

        # Iterate through the video streams to find a matching one
        for stream_data in self.__videos_streams_data:
            stream_width = int(stream_data.get('width', 0))
            stream_height = int(stream_data.get('height', 0))
            mime_type = stream_data.get('mimeType', None)

            # Check if both resolution and mime type match the criteria
            if stream_width == width and stream_height == height and typeuri in str(mime_type).split(';')[0]:
                return VideoStream(uri=stream_data)

    @property
    def get_all_audios_quality(self) -> list[dict]:
        """obtenha todas qualidades de áudio disponivel na stream"""
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
        filtre e obtenha apenas uma faixa de aúdio especifica da stream,

        :param audio_quality: Ex: 'AUDIO_QUALITY_MEDIUM'
        :param type_audio: Ex: 'audio/mp4'
        :return: Objeto AudioStream
        """
        # Iterate through the video streams to find matching ones
        for stream_data in self.__audios_streams_data:
            audioQuality = stream_data.get('audioQuality', '')
            mime_type = stream_data.get('mimeType', '')
            # Check if both resolution and mime type match the criteria
            if audioQuality == audio_quality and type_audio in str(mime_type).split(';')[0]:
                s = AudioStream(uri=stream_data)
                return s

    @property
    def get_highest_resolution(self) -> VideoStream:
        """
        Encontra a maior resolução a partir de uma lista de resoluções disponíveis no vídeo,elas geralmente
        não terão o áudio embutido
   :return (objeto) VideoStream
        """
        resolutions = self.get_resolutions
        if not resolutions:
            raise YoutubeAnalyzerExceptions("Not resolutions in video...")

        # Encontra a maior resolução
        highest_resolution = max(resolutions,
                                 key=lambda r: (int(r['resolution'].split('x')[0]), int(r['resolution'].split('x')[1])))
        r = self.filter_resolution(resolution_filter=highest_resolution.get('resolution'),
                                   typeuri=highest_resolution.get('typeUri'))
        return r

    @property
    def get_best_audio_quality(self) -> AudioStream:
        """
        Obtém a melhor faixa de áudio

        :return(dict): chaves -> 'audioQuality', 'typeAudio'
        """
        # Definir uma ordem de prioridade para a qualidade do áudio
        quality_order = {
            'AUDIO_QUALITY_LOW': 1,
            'AUDIO_QUALITY_MEDIUM': 2,
            'AUDIO_QUALITY_HIGH': 3
        }
        best_quality = None
        best_audio = None
        audio_list = self.get_all_audios_quality

        for audio in audio_list:
            quality = audio.get('audioQuality')
            if quality and (best_quality is None or quality_order.get(quality, 0) > quality_order.get(best_quality, 0)):
                best_quality = quality
                best_audio = audio
        d = self.filter_audio_quality(audio_quality=best_audio.get('audioQuality'),
                                      type_audio=best_audio.get('typeAudio'))

        return d

    @property
    def get_format_contained_audio(self) -> VideoStream:
        """Objeto VideoStream que contém áudio embutido geralmente terá uma baixa resolução"""
        f = max(self.__formats, key=lambda x: x['width'])
        return VideoStream(f)
