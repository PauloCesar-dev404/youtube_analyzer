
<div align="center">
        <h1>youtube-analyzer</h1>


![Versão](https://img.shields.io/badge/version-0.1-orange)
![Licença](https://img.shields.io/badge/license-MIT-orange)
[![Sponsor](https://img.shields.io/badge/💲Donate-yellow)](https://apoia.se/paulocesar-dev404)

</div>

Obtenha detalhes de vídeos do youtube usando esta lib
---
- [x] Obter detalhes de um vídeo
```python

from youtube_analyzer import VideoMetadates, Captions

# Crie uma instância da classe VideoMetadates
yt = VideoMetadates()

# Substitua 'url-video' pelo URL do vídeo que você deseja analisar
url_video = ''
video = yt.get_video_info(url_video=url_video)

# Imprima as informações do vídeo
print("Título do vídeo:", video.title)
print("Descrição do vídeo:", video.description)
print("Thumbnails do vídeo:", video.thumbnails)
print("Autor do vídeo:", video.author)
print("Número de visualizações:", video.viewCount)
print("É privado:", video.is_private)
print("É um vídeo ao vivo:", video.isLiveContent)

```
- [x] obter legendas

```python
import os
from youtube_analyzer import Captions

# Substitua 'url-video' pelo URL do vídeo que você deseja analisar
url_video = ''
lg = Captions(url_video=url_video)

# Diretório onde as legendas serão salvas
out = 'captions_dir'
os.makedirs(out, exist_ok=True)

# Obter legendas disponíveis no vídeo
captions = lg.captions_in_video
captions_disponiveis = captions.get_languages()  # Lista de idiomas disponíveis
print("Legendas disponíveis:", captions_disponiveis)

# Baixar legendas em português
# Substitua 'pt' pelo código de idioma desejado se necessário
captions.download_subtitles(language_code='pt', logs=True, out_dir=out)
```
- [x] Analizar playlists
```python
from youtube_analyzer import PlaylistMetadates

# Substitua 'url-playlist' pelo URL da playlist que você deseja analisar
url_playlist = ''
pl = PlaylistMetadates()

# Obter informações da playlist
playlist = pl.get_playlist_info(playlist_url=url_playlist)

# Exibir informações da playlist
print("Privada:", playlist.is_private)  # Verificar se a playlist é privada
print("Quantidade de vídeos:", playlist.count)  # Quantidade de vídeos na playlist
print("Título da playlist:", playlist.playlist_name)  # Título da playlist
print("Imagem da playlist:", playlist.image)  # Imagem da playlist
print("Descrição da playlist:", playlist.description)  # Descrição da playlist

if not playlist.is_private:
    # Obter e exibir todos os vídeos da playlist
    videos = playlist.get_all_videos  # Lista de dicionários contendo informações dos vídeos
    for video in videos:
        print("Título do vídeo:", video.get('title'))
        print("URL do vídeo:", video.get('url'))
        print("Descrição do vídeo:", video.get('description'))
        print("Duração do vídeo:", video.get('duration'))
        print()  # Linha em branco para separar vídeos
```

- [x] Obter detalhes de uris de Vídeos
```python
from youtube_analyzer import VideoMetadates

# Substitua 'url-video' pelo URL do vídeo que você deseja analisar
url_video = ''
yt = VideoMetadates()

# Obtém as informações do vídeo
v = yt.get_video_info(url_video=url_video)

# Obtém todas as resoluções disponíveis para o vídeo com  a propiedade get_resolutions
uris = v.uris_stream.get_resolutions
print("Resoluções disponíveis:")
print(uris)

# Define o filtro para a resolução e tipo de URI desejados
resolution_filter = '1280x720'
typeuri = 'video/mp4'

# Filtra e obtém os dados da resolução desejada
uri_filter = v.uris_stream.filter_resolution(resolution_filter=resolution_filter, typeuri=typeuri)

# Exibe as informações do URI filtrado
print("URL temporária de download:", uri_filter.url)
print("Qualidade:", uri_filter.quality)
print("FPS:", uri_filter.fps)
print("iTag:", uri_filter.itag)
print("Largura:", uri_filter.width)
print("Altura:", uri_filter.height)
print("Bitrate:", uri_filter.bitrate)
print("Rótulo de qualidade:", uri_filter.qualityLabel)
print("Tipo de projeção:", uri_filter.projectionType)
print("Faixa de inicialização:", uri_filter.initRange)
print("Duração aproximada (ms):", uri_filter.approxDurationMs)
print("Última modificação:", uri_filter.lastModified)
print("MimeType:", uri_filter.mimeType)
print("Bitrate médio:", uri_filter.averageBitrate)
print("Faixa de índice:", uri_filter.indexRange)

```

- [x] Donwload de vídeos
```python
import os
from youtube_analyzer import VideoMetadates, download_video

# Substitua 'url-video' pelo URL do vídeo que você deseja analisar
url_video = 'URL_DO_VÍDEO_AQUI'
yt = VideoMetadates()

# Obtém as informações do vídeo
v = yt.get_video_info(url_video=url_video)

# Obtém todas as resoluções disponíveis para o vídeo
uris = v.uris_stream.get_resolutions
print("Resoluções disponíveis:")
print(uris)

# Define o filtro para a resolução e tipo de URI desejados
resolution_filter = '1280x720'
typeuri = 'video/mp4'

# Filtra e obtém os dados da resolução desejada
uri_filter = v.uris_stream.filter_resolution(resolution_filter=resolution_filter, typeuri=typeuri)
if uri_filter:
    out = 'Videos'
    os.makedirs(out, exist_ok=True)
    title = v.title
    uri = uri_filter.url

    # Baixa o vídeo
    download_video(title=title, uri=uri, output_dir=out, overwrite_output=True, logs=True)
else:
    print("Nenhuma resolução correspondente encontrada.")
```