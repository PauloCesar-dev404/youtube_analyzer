import os
import sys
import time
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
                       capture_chunks: Optional[Callable[[int], None]] = None):
        """
        Faz o download de um vídeo e salva no diretório especificado. Se `logs` for fornecido, exibirá uma barra de
        progresso; caso contrário, retornará os chuncks baixados que deve ser iterado por um loop para baixar :param
        title: Título do vídeo. :param output_dir: Diretório de saída onde o vídeo será salvo. :param
        overwrite_output: Se True, sobrescreve o arquivo se ele já existir. :param logs: Função de callback para
        logs, exibira todo progresso :param capture_chunks: Função de callback para capturar o andamento do download.
        :return:
        """
        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            if logs:
                debug("warn", f"O diretório {output_dir},não existe criando", end=' ')
            os.makedirs(output_dir, exist_ok=True)
            if logs:
                debug('true', '\t Criado!')
        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp4")
        # Verifica se o arquivo já existe
        file_exists = os.path.exists(file_path)
        # Sobrescrever o arquivo se `overwrite_output` for True
        if file_exists and overwrite_output:
            os.remove(file_path)
            file_exists = False

        if file_exists:
            raise FileExistsError(f"Arquivo já existe: {file_path}")
        uri = self.url
        debug('true', msg='Informações Do Vídeo')
        f"""
        {debug('info', 'Fps:', end=' ')}
        {debug('true', self.fps)}
        {debug('info', 'Duração:', end=' ')}
        {debug('true', self.approxDurationMs)}
        {debug('info', 'MimeType:', end=' ')}
        {debug('true', self.mimeType.split(";")[0])}
        {debug('info', 'Data de Modificação:', end=' ')}
        {debug('true', self.lastModified)}
        {debug('info', 'Codecs:', end=' ')}
        {debug('true', self.mimeType.split(";")[1].split("codecs=")[1].replace('"', ''))}
        {debug('info', 'Resolução:', end=' ')}
        {debug('true', f'{self.width}x{self.height}')}
        {debug('info', 'Canais de Áudio:', end=' ')}
        {debug('true', f'{self.audioChannels}')}
        {debug('info', 'Qualidade:', end=' ')}
        {debug('true', f'{self.qualityLabel.lower()}')}
        {debug('info', 'Tamanho do Arquivo:', end=' ')}
        {debug('true', f'{self.contentLength}')}
        """
        time.sleep(3)

        def download_generator():
            """Gerador que baixa o vídeo em pedaços e atualiza o progresso detalhado."""
            try:
                chunk_size = 32768  # 32 KB, padrão do FFmpeg

                response = requests.get(uri, stream=True)
                response.raise_for_status()  # Levanta exceção para códigos de status HTTP de erro

                total_length = int(response.headers.get('content-length', 0))
                with open(file_path, 'wb') as out_file:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            if capture_chunks:
                                capture_chunks(len(chunk))
                            if logs:
                                percentage = (downloaded / total_length) * 100
                                sys.stdout.flush()
                                sys.stdout.write(
                                    f"\rProgresso: {percentage:.1f}%")
                                sys.stdout.flush()
                            yield len(chunk)
                return file_path
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Erro ao baixar o vídeo: {e}")

        if logs:
            for _ in download_generator():
                pass
            if logs:
                debug("true", f"\tDownload completo!")
            return file_path
        else:
            # Retorna o gerador para uso posterior
            return download_generator()


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
                       capture_chunks: Optional[Callable[[int], None]] = None):
        """
        Faz o download de um vídeo e salva no diretório especificado. Se `logs` for fornecido, exibirá uma barra de
        progresso; caso contrário, retornará os chuncks baixados que deve ser iterado por um loop para baixar :param
        title: Título do vídeo. :param output_dir: Diretório de saída onde o vídeo será salvo. :param
        overwrite_output: Se True, sobrescreve o arquivo se ele já existir. :param logs: Função de callback para
        logs, exibira todo progresso :param capture_chunks: Função de callback para capturar o andamento do download.
        :return:
        """
        # Cria o diretório de saída se não existir
        if not os.path.exists(output_dir):
            if logs:
                debug("warn", f"O diretório {output_dir},não existe criando", end=' ')
            os.makedirs(output_dir)
            if logs:
                debug('true', '\t Criado!')
        # Define o caminho completo para salvar o arquivo
        file_path = os.path.join(output_dir, f"{title}.mp4")
        # Verifica se o arquivo já existe
        file_exists = os.path.exists(file_path)
        # Sobrescrever o arquivo se `overwrite_output` for True
        if file_exists and overwrite_output:
            os.remove(file_path)
            file_exists = False

        if file_exists:
            raise FileExistsError(f"Arquivo já existe: {file_path}")
        uri = self.url
        debug('true', msg='Informações Do Áudio')
        f"""
        {debug('info', 'Bitrate (Taxa de Bits):', end=' ')}
        {debug('true', self.bitrate)}
        {debug('info', 'Duração:', end=' ')}
        {debug('true', self.approxDurationMs)}
        {debug('info', 'MimeType:', end=' ')}
        {debug('true', self.mimeType.split(";")[0])}
        {debug('info', 'Data de Modificação:', end=' ')}
        {debug('true', self.lastModified)}
        {debug('info', 'Codecs:', end=' ')}
        {debug('true', self.mimeType.split(";")[1].split("codecs=")[1].replace('"', ''))}
        {debug('info', 'Canais de Áudio:', end=' ')}
        {debug('true', f'{self.audioChannels}')}
        {debug('info', 'Qualidade:', end=' ')}
        {debug('true', f'{self.audioQuality.lower()}')}
        {debug('info', 'Tamanho do Arquivo:', end=' ')}
        {debug('true', f'{self.contentLength}')}
        """
        time.sleep(3)

        def download_generator():
            """Gerador que baixa o vídeo em pedaços e atualiza o progresso detalhado."""
            try:
                chunk_size = 32768  # 32 KB, padrão do FFmpeg

                response = requests.get(uri, stream=True)
                response.raise_for_status()  # Levanta exceção para códigos de status HTTP de erro

                total_length = int(response.headers.get('content-length', 0))
                with open(file_path, 'wb') as out_file:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            if capture_chunks:
                                capture_chunks(len(chunk))
                            if logs:
                                percentage = (downloaded / total_length) * 100
                                sys.stdout.flush()
                                sys.stdout.write(
                                    f"\rProgresso: {percentage:.1f}%")
                                sys.stdout.flush()
                            yield len(chunk)
                return file_path
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Erro ao baixar o vídeo: {e}")

        if logs:
            for _ in download_generator():
                pass
            if logs:
                debug("true", f"\tDownload completo!")
            return file_path
        else:
            # Retorna o gerador para uso posterior
            return download_generator()


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
