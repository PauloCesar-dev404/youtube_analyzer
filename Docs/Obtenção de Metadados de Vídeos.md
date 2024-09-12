

# Obtenção de Metadados de Vídeos

Para começar, você deve instanciar a classe `VideoMetadates()`:

```python
from youtube_analyzer import VideoMetadates
info = VideoMetadates()
```

A partir desse ponto, todas as interações serão feitas através do objeto `info`. Agora vamos explorar as informações que podem ser obtidas de um vídeo.

## Legendas

Podemos usar nosso objeto `info` para acessar a propriedade `captions`, que cria um objeto de legendas. Esse objeto tem uma única propriedade chamada `captions_in_video`, que extrai todas as legendas disponíveis de um vídeo e cria um objeto `CaptionsParser`. Através desse objeto, é possível obter todos os idiomas disponíveis e também baixar as legendas.

### Exemplo de Uso:

```python
from youtube_analyzer import VideoMetadates
info = VideoMetadates()

url_do_video = ''  # Insira a URL do vídeo
meta_dates = info.get_video_info(url_video=url_do_video)

# Possíveis informações
print(meta_dates.captions.captions_in_video.get_languages)  
# Exibe as legendas disponíveis no vídeo (se houver)
```

O retorno será uma lista de dicionários contendo as legendas disponíveis no vídeo. Um exemplo de legenda no idioma português seria:

```python
[{'lang': 'Portuguese (auto-generated)', 'code': 'pt', 'url': ''}]
```

Esse formato permite acessar todas as legendas disponíveis em um vídeo.

### Baixando Legendas

Para baixar as legendas, você pode usar o método `download_subtitles`, que permite baixar as legendas de um vídeo. Esse método recebe os seguintes parâmetros:
- `language_code`: O código do idioma (obtido anteriormente).
- `out_dir`: O diretório onde a legenda será salva.
- `logs` (opcional): Um booleano que indica se os detalhes do processo de download devem ser exibidos.

### Exemplo de Uso para Baixar Legendas:

```python
from youtube_analyzer import VideoMetadates
info = VideoMetadates()

url_do_video = ''  # Insira a URL do vídeo
meta_dates = info.get_video_info(url_video=url_do_video)

# Baixando a legenda em português por ex
meta_dates.captions.captions_in_video.download_subtitles(language_code='pt', out_dir='captions', logs=True)
```

### Observações:
- As legendas só serão baixadas se estiverem disponíveis no vídeo.
- Nem todos os vídeos possuem legendas, e nem todos os idiomas desejáveis estarão disponíveis em um vídeo.


Podemos obter várias informações sobre o vídeo, como título, descrição, visualizações, entre outros, usando a classe VideoMetadates.

````python
from youtube_analyzer import VideoMetadates

# URL do vídeo do YouTube
url = ''

# Instanciando a classe VideoMetadates
video = VideoMetadates()

# Obtendo informações sobre o vídeo
info = video.get_video_info(url_video=url)

# Exibindo os metadados obtidos
print("Título:", info.title)
print("Visualizações:", info.viewCount)
print("Descrição:", info.description)
print("É privado:", info.is_private)
print("É live:", info.isLiveContent)
print("Thumbnails:", info.thumbnails)
print("Autor (canal):", info.author)
print("Objeto de streams:", info.uris_stream)  # Veremos mais detalhes sobre isso a seguir
print("Objeto captions:", info.captions)  # Já vimos anteriormente sobre legendas

````

Vamos agora trabalahar com streams de vídeo e de aúdio.

