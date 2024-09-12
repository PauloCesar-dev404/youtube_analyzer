# Obtendo Detalhes das Faixas de Streams de Áudios

Agora vamos aprender como obter as faixas de audio (streams) de um vídeo.
### Uso:

```python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''  # Insira a URL do vídeo

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

# Obtendo o stream de melhor qualidade de áudio
streams = info.uris_stream.get_best_audio_quality  # Objeto AudioStream

# Exibindo os detalhes da faixa de áudio selecionada
print("MIME Type:", streams.mimeType)
print("Última Modificação:", streams.lastModified)
print("Qualidade de Áudio:", streams.audioQuality)
print("Tamanho do Conteúdo (bytes):", streams.contentLength)
print("URL:", streams.url)
print("Qualidade:", streams.quality)
print("Taxa de Bits (bitrate):", streams.bitrate)
print("Canais de Áudio:", streams.audioChannels)
print("Tipo de Projeção:", streams.projectionType)  # Pode não se aplicar a áudio
print("Duração Aproximada (ms):", streams.approxDurationMs)
print("Loudness (dB):", streams.loudnessDb)  # Se disponível
print("Bitrate Médio (bitrate):", streams.averageBitrate)  # Se disponível
print("Alta Replicação:", streams.highReplication)  # Se disponível
print("Taxa de Amostragem do Áudio (Hz):", streams.audioSampleRate)  # Se disponível

```

### Propriedades Extraídas:
Aqui está uma descrição detalhada das propriedades extraídas para streams de áudio, como apresentado no código:

### Propriedades Extraídas:

- **MIME Type**: O tipo MIME do stream de áudio (ex.: `audio/mp4`). Indica o formato do arquivo de áudio.
- **Última Modificação**: A data e hora da última modificação do stream. Pode ser útil para verificar a atualidade do conteúdo.
- **Qualidade de Áudio**: A qualidade do áudio, geralmente indicada por uma descrição como `AUDIO_QUALITY_LOW`, `AUDIO_QUALITY_MEDIUM`, ou `AUDIO_QUALITY_HIGH`. Reflete a qualidade percebida do áudio.
- **Tamanho do Conteúdo (bytes)**: O tamanho total do stream de áudio em bytes. Permite avaliar o espaço necessário para armazenar o arquivo.
- **URL**: A URL direta para acessar o stream de áudio. É o link que pode ser usado para reproduzir ou baixar o áudio.
- **Qualidade**: A qualidade do áudio em termos de taxa de bits, geralmente expressa em kbps (kilobits por segundo). Por exemplo, `192 kbps`.
- **Taxa de Bits (bitrate)**: A taxa de bits do stream de áudio, em bps (bits por segundo). A taxa de bits é uma medida direta da qualidade e do tamanho do arquivo.
- **Canais de Áudio**: O número de canais de áudio no stream, como estéreo (2 canais) ou mono (1 canal).
- **Tipo de Projeção**: Esse campo é mais relevante para vídeos, mas pode aparecer como `N/A` para streams de áudio, pois não se aplica.
- **Duração Aproximada (ms)**: A duração aproximada do stream de áudio em milissegundos. Ajuda a saber o tempo total de reprodução.
- **Loudness (dB)**: O nível de loudness do áudio em decibéis (dB). É uma medida do volume médio do áudio.
- **Bitrate Médio (bitrate)**: A taxa de bits média do stream, que pode fornecer uma ideia mais geral da qualidade do áudio ao longo do tempo.
- **Alta Replicação**: Indica se o stream tem alta replicação, o que pode sugerir a disponibilidade e a qualidade em diferentes regiões ou servidores.
- **Taxa de Amostragem do Áudio (Hz)**: A taxa de amostragem do áudio em Hertz (Hz). Comum em 44100 Hz para áudio de CD e 48000 Hz para áudio de vídeo. Reflete a qualidade do áudio em termos de fidelidade à gravação original.

Essas propriedades fornecem uma visão abrangente sobre o stream de áudio, incluindo detalhes técnicos e informações de qualidade.
---

# obter resoluções disponíveis de faixas de audio:

````python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

### obter resoluções disponiveis

streams = info.uris_stream.get_all_audios_quality  # objeto AudioStream

print(streams)
````
a saida sera algo assim:
````
[{'audioQuality': 'AUDIO_QUALITY_LOW', 'typeAudio': 'audio/mp4'}, {'audioQuality': 'AUDIO_QUALITY_MEDIUM', 'typeAudio': 'audio/mp4'}, {'audioQuality': 'AUDIO_QUALITY_LOW', 'typeAudio': 'audio/webm'}, {'audioQuality': 'AUDIO_QUALITY_MEDIUM', 'typeAudio': 'audio/webm'}, {'audioQuality': 'AUDIO_QUALITY_ULTRALOW', 'typeAudio': 'audio/mp4'}, {'audioQuality': 'AUDIO_QUALITY_ULTRALOW', 'typeAudio': 'audio/webm'}]
````

# filtrar faixa de audio e obter sua stream

`````python
from youtube_analyzer import VideoMetadates
# URL do vídeo do YouTube
url = ''
# Instanciando a classe VideoMetadates
video = VideoMetadates()
# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)
### obter resoluções disponiveis
streams = info.uris_stream.get_all_audios_quality
audioQuality = 'AUDIO_QUALITY_MEDIUM'
typeAudio = 'audio/mp4'
# obtendo a stream da faixa
filter_streaming = info.uris_stream.filter_audio_quality(audio_quality=audioQuality,type_audio=typeAudio) # -> objeto AudioStream

````` 

# Obter as stream da melhor faixa de audio

```python
from youtube_analyzer import VideoMetadates
# URL do vídeo do YouTube
url = ''
# Instanciando a classe VideoMetadates
video = VideoMetadates()
# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)


audio_stream = info.uris_stream.get_best_audio_quality # objeto AudioStream

```