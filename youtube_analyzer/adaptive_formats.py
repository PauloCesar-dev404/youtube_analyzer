import datetime


class VideoStream:
    def __init__(self, uri):
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
        self.__data = {'itag': uri.get('itag', None), 'url': uri.get('url', None),
                       'mimeType': uri.get('mimeType', None), 'bitrate': uri.get('bitrate', None),
                       'width': uri.get('width', None), 'height': uri.get('height', None),
                       'initRange': uri.get('initRange', None), 'indexRange': uri.get('indexRange', None),
                       'lastModified': uri.get('lastModified', None), 'contentLength': uri.get('contentLength', None),
                       'quality': uri.get('quality', None), 'fps': uri.get('fps', None),
                       'qualityLabel': uri.get('qualityLabel', None), 'projectionType': uri.get('projectionType', None),
                       'averageBitrate': uri.get('averageBitrate', None),
                       'approxDurationMs': uri.get('approxDurationMs', None)}
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
        return self.__data.get('bitrate')

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
        return timestamp(int(self.__data.get('lastModified')))

    @property
    def contentLength(self):
        return self.__data.get('contentLength')

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
        return self.__data.get('approxDurationMs')


class AudioStream:
    def __init__(self, uri):
        self.__stream = self.__load_uri(uri=uri)

    def __load_uri(self, uri):
        self.__data = {
            'itag': uri.get('itag', ''),
            'url': uri.get('url', ''),
            'mimeType': uri.get('mimeType', ''),
            'bitrate': uri.get('bitrate', ''),
            'initRange': uri.get('initRange', ''),
            'indexRange': uri.get('indexRange', ''),
            'lastModified': uri.get('lastModified', 0),
            'contentLength': uri.get('contentLength', 0),
            'quality': uri.get('quality', ''),
            'projectionType': uri.get('projectionType', ''),
            'averageBitrate': uri.get('averageBitrate', ''),
            'highReplication': uri.get('highReplication', ''),
            'audioQuality': uri.get('audioQuality', ''),
            'approxDurationMs': uri.get('approxDurationMs', ''),
            'audioSampleRate': uri.get('audioSampleRate', ''),
            'audioChannels': uri.get('audioChannels', ''),
            'loudnessDb': uri.get('loudnessDb', '')
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
        return self.__data.get('bitrate')

    @property
    def initRange(self):
        return self.__data.get('initRange')

    @property
    def indexRange(self):
        return self.__data.get('indexRange')

    @property
    def lastModified(self):
        return timestamp(int(self.__data.get('lastModified')))

    @property
    def contentLength(self):
        return self.__data.get('contentLength')

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
        return self.__data.get('approxDurationMs')

    @property
    def audioSampleRate(self):
        return self.__data.get('audioSampleRate')

    @property
    def audioChannels(self):
        return self.__data.get('audioChannels')

    @property
    def loudnessDb(self):
        return self.__data.get('loudnessDb')


class FormatStream:
    def __init__(self, streamingData):
        self.__data = streamingData
        self.__adaptiveFormats = self.__data.get('adaptiveFormats', [])
        self.__formats = self.__data.get('formats', [])

        self.__videos_streams_data = self.__load_videos_streams
        self.__audios_streams_data = self.__load_audio_streams

        if not self.__adaptiveFormats:
            raise

    @property
    def __load_videos_streams(self):
        formats = []
        add = []
        for i in self.__adaptiveFormats:
            mimeType = i.get("mimeType", None)
            if 'video/mp4' in mimeType or 'video/webm' in mimeType:
                if not i in add:
                    formats.append(i)
                    add.append(i)
        for i in self.__formats:
            mimeType = i.get("mimeType", None)
            if 'video/mp4' in mimeType or 'video/webm' in mimeType:
                if not i in add:
                    formats.append(i)
                    add.append(i)
        return formats

    @property
    def __load_audio_streams(self):
        formats = []
        for i in self.__adaptiveFormats:
            mimeType = i.get("mimeType", None)
            if 'audio/mp4' in mimeType or 'audio/webm' in mimeType:
                formats.append(i)
        for i in self.__formats:
            mimeType = i.get("mimeType", None)
            if 'audio/mp4' in mimeType or 'audio/webm' in mimeType:
                formats.append(i)
        return formats

    @property
    def get_resolutions(self):
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
                url = uri.get("url", None)
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
        :return: objeto VideoStream correspondente ou None se não encontrar
        """
        # Validate and parse the resolution_filter
        try:
            width, height = map(int, resolution_filter.split('x'))
        except ValueError:
            raise ValueError("Invalid resolution format. Expected format 'WIDTHxHEIGHT'.")

        # Iterate through the video streams to find a matching one
        for stream_data in self.__videos_streams_data:
            stream_width = int(stream_data.get('width', 0))
            stream_height = int(stream_data.get('height', 0))
            mime_type = stream_data.get('mimeType', None)

            # Check if both resolution and mime type match the criteria
            if stream_width == width and stream_height == height and typeuri in str(mime_type).split(';')[0]:
                return VideoStream(uri=stream_data)

    @property
    def get_all_audios_quality(self):
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
        filtre e obtenha apenas uma faixa de aúdeio especifica da stream,
        as qualiadades podem ser obtidas com metodo get_audio_resolution(),e passados a este método.

        :param audio_quality: Ex: 'AUDIO_QUALITY_MEDIUM'
        :param type_audio: Ex: 'audio/mp4'
        :return:
        """
        # Iterate through the video streams to find matching ones
        for stream_data in self.__audios_streams_data:
            audioQuality = stream_data.get('audioQuality', '')
            mime_type = stream_data.get('mimeType', '')
            # Check if both resolution and mime type match the criteria
            if audioQuality == audio_quality and type_audio in str(mime_type).split(';')[0]:
                s = AudioStream(uri=stream_data)
                return s


def timestamp(timestamp: int):
    """

    :type timestamp: numero
    """
    try:
        seconds = timestamp / 1_000_000
        # Converta para datetime
        dt = datetime.datetime.fromtimestamp(seconds)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return timestamp
