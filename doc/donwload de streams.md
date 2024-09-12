### Download de Streams de Áudio

```python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''  # Insira a URL do vídeo

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

# Obtendo o stream de áudio com a melhor qualidade
audio_stream = info.uris_stream.get_best_audio_quality  # Objeto AudioStream

# Download do stream de áudio
audio_stream.download_audio(
    title='audio_qualidade_alta',               # Título do arquivo de saída
    output_dir='/caminho/para/salvar',           # Diretório onde o arquivo será salvo
    overwrite_output=True,                      # Sobrescrever o arquivo se já existir
    logs=True                          # exibir o progresso do download
)
```

### Parâmetros de `download_audio`:

- **title**: Título do arquivo de saída. É o nome que o arquivo de áudio baixado terá.
- **output_dir**: Diretório onde o arquivo será salvo. Deve ser o caminho completo para a pasta onde o arquivo será armazenado.
- **overwrite_output** (Opcional): Define se o arquivo deve ser sobrescrito caso já exista. O padrão é `False`, o que significa que o arquivo não será sobrescrito a menos que esta opção seja definida como `True`.
- **logs** (Opcional): Exibe o progresso do download. Recebe um valor que indica o progresso percentual.
- **capture_chunks** (Opcional): Função de callback que captura chunks baixados. Recebe dados de chunks durante o processo de download.

### Uso dos Callbacks

- **capture_chunks**: Permite monitorar e processar partes do arquivo conforme são baixadas. Isso pode ser útil para rastrear o progresso detalhado do download ou para lidar com dados em tempo real.
- **logs**: Fornece atualizações sobre o progresso geral do download, permitindo que você acompanhe a conclusão do processo em termos percentuais.

Certifique-se de substituir `'/caminho/para/salvar'` pelo diretório onde você deseja salvar o arquivo e ajustar o título conforme necessário. O uso dos callbacks é opcional, mas pode fornecer informações úteis durante o download.



---
### Download de Streams de Vídeos
```python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''  # Insira a URL do vídeo

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

# Obtendo o stream de melhor qualidade de vídeo que contenha áudio e vídeo
streams = info.uris_stream.get_format_contained_audio

# Download do stream de vídeo
streams.download_video(
    title='titulo-aqui',                # Título do arquivo de saída
    output_dir='/caminho/para/salvar',  # Diretório onde o arquivo será salvo
    overwrite_output=True,             # Sobrescrever o arquivo se já existir
    logs=True                          # Exibir o progresso do download
)

```

### Parâmetros de `download_video`:

- **title**: Título do arquivo de saída. É o nome que o arquivo de áudio baixado terá.
- **output_dir**: Diretório onde o arquivo será salvo. Deve ser o caminho completo para a pasta onde o arquivo será armazenado.
- **overwrite_output** (Opcional): Define se o arquivo deve ser sobrescrito caso já exista. O padrão é `False`, o que significa que o arquivo não será sobrescrito a menos que esta opção seja definida como `True`.
- **logs** (Opcional): Exibe o progresso do download.
- **capture_chunks** (Opcional): Função de callback que captura chunks baixados. Recebe dados de chunks durante o processo de download.

### Uso dos Callbacks

- **capture_chunks**: Permite monitorar e processar partes do arquivo conforme são baixadas. Isso pode ser útil para rastrear o progresso detalhado do download ou para lidar com dados em tempo real.
- **logs**: Fornece atualizações sobre o progresso geral do download, permitindo que você acompanhe a conclusão do processo em termos percentuais.

Certifique-se de substituir `'/caminho/para/salvar'` pelo diretório onde você deseja salvar o arquivo e ajustar o título conforme necessário. O uso dos callbacks é opcional, mas pode fornecer informações úteis durante o download.

