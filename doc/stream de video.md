# Obtendo Detalhes das Faixas de Streams de Vídeos

Agora vamos aprender como obter as faixas de vídeo (streams) de um vídeo. Isso pode ser feito de maneira simples, acessando o objeto `uris_stream` para extrair as diferentes propriedades de qualidade, áudio, resolução, entre outras.

### Uso:

```python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''  # Insira a URL do vídeo

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

# Obtendo o stream de maior resolução
streams = info.uris_stream.get_highest_resolution  # Objeto VideoStream

# Exibindo os detalhes da faixa de vídeo selecionada
print("MIME Type:", streams.mimeType)
print("FPS:", streams.fps)
print("Última Modificação:", streams.lastModified)
print("Qualidade de Áudio:", streams.audioQuality)
print("Tamanho do Conteúdo (bytes):", streams.contentLength)
print("URL:", streams.url)
print("Qualidade:", streams.quality)
print("Taxa de Bits (bitrate):", streams.bitrate)
print("Canais de Áudio:", streams.audioChannels)
print("Tipo de Projeção:", streams.projectionType)
print("Largura (pixels):", streams.width)
print("Altura (pixels):", streams.height)
print("Duração Aproximada (ms):", streams.approxDurationMs)
```

### Propriedades Extraídas:

- **mimeType**: Tipo MIME do stream (ex.: vídeo/mp4).
- **fps**: Frames por segundo (taxa de quadros).
- **lastModified**: Data da última modificação.
- **audioQuality**: Qualidade do áudio associada ao stream.
- **contentLength**: Tamanho do conteúdo (em bytes).
- **url**: URL para acessar o stream.
- **quality**: Resolução e qualidade do vídeo (ex.: 1080p).
- **bitrate**: Taxa de bits (bitrate) do stream.
- **audioChannels**: Número de canais de áudio (ex.: estéreo).
- **projectionType**: Tipo de projeção do vídeo (ex.: regular ou 360º).
- **width**: Largura do vídeo em pixels.
- **height**: Altura do vídeo em pixels.
- **approxDurationMs**: Duração aproximada do vídeo em milissegundos.
---


# obter resoluções disponíveis de faixas de video:

````python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

### obter resoluções disponiveis

streams = info.uris_stream.get_resolutions  # objeto VideoStream

print(streams)
````
a saida sera algo assim:
````
[{'resolution': '3840x2160', 'typeUri': 'video/webm'}, {'resolution': '3840x2160', 'typeUri': 'video/mp4'}, {'resolution': '2560x1440', 'typeUri': 'video/webm'}, {'resolution': '2560x1440', 'typeUri': 'video/mp4'}, {'resolution': '1920x1080', 'typeUri': 'video/mp4'}, {'resolution': '1920x1080', 'typeUri': 'video/webm'}, {'resolution': '1280x720', 'typeUri': 'video/mp4'}, {'resolution': '1280x720', 'typeUri': 'video/webm'}, {'resolution': '854x480', 'typeUri': 'video/mp4'}, {'resolution': '854x480', 'typeUri': 'video/webm'}, {'resolution': '640x360', 'typeUri': 'video/mp4'}, {'resolution': '640x360', 'typeUri': 'video/webm'}, {'resolution': '426x240', 'typeUri': 'video/mp4'}, {'resolution': '426x240', 'typeUri': 'video/webm'}, {'resolution': '256x144', 'typeUri': 'video/mp4'}, {'resolution': '256x144', 'typeUri': 'video/webm'}]
````

>[!Atenção]
> as resoluções de qualidades altas não contém audio somente vídeo 
> 
# Obter Faixa que contem audio e video
````python
from youtube_analyzer import VideoMetadates
# URL do vídeo do YouTube
url = ''
# Instanciando a classe VideoMetadates
video = VideoMetadates()
# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)
### obter faixa que contem video e audio
streams = info.uris_stream.get_format_contained_audio
````

# filtrar faixas de video e obter a sua stream
````python
from youtube_analyzer import VideoMetadates
# URL do vídeo do YouTube
url = ''
# Instanciando a classe VideoMetadates
video = VideoMetadates()
# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)
### obter resoluções disponiveis
streams = info.uris_stream.get_resolutions
resolution = '1920x1080'
typeUri = 'video/mp4'
# obtendo a faixa da resolucao
filter_streaming =  info.uris_stream.filter_resolution(resolution_filter=resolution,typeuri=typeUri) # -> objeto VideoStream

````
