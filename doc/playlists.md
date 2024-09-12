# Obtendo Dados de Playlists

Com a biblioteca `youtube_analyzer`, você pode extrair informações detalhadas sobre uma playlist no YouTube, como título, descrição, tipo de playlist (pública ou privada) e os vídeos contidos nela.

### Exemplo de Uso:

```python
from youtube_analyzer import PlaylistMetadates

# URL da playlist no YouTube
url = ''

# Instanciando a classe PlaylistMetadates
parser = PlaylistMetadates()

# Obtendo informações sobre a playlist
pl = parser.get_playlist_info(playlist_url=url)

# Exibindo os detalhes da playlist
print("Privada:", pl.is_private)  # Tipo (privada ou pública)
print("Descrição:", pl.description)  # Descrição da playlist
print("Título:", pl.playlist_name)  # Título da playlist
print("Imagem:", pl.image)  # Thumbnail da playlist
print("Quantidade de vídeos:", pl.count)  # Quantidade de vídeos na playlist

# Obtendo a lista de vídeos
videos = pl.get_all_videos  # Retorna uma lista de dicionários com informações dos vídeos

# Exibindo a lista de vídeos
for video in videos:
    print(f"Título: {video['title']}, URL: {video['url']}")
```

### Propriedades Extraídas:

- **is_private**: Indica se a playlist é privada (`True`) ou pública (`None`).
- **description**: Descrição fornecida para a playlist.
- **playlist_name**: Nome ou título da playlist.
- **image**: URL da imagem de miniatura (thumbnail) da playlist.
- **count**: Quantidade total de vídeos na playlist.
- **get_all_videos**: Retorna uma lista de dicionários, onde cada dicionário contém informações sobre um vídeo, como título e URL.

### Exemplo de Retorno da Lista de Vídeos:

```python
[{'title': '', 'url_watch': ''},{'title': '', 'url_watch': ''}]
```

---

Essa funcionalidade permite extrair de forma eficiente os principais dados de uma playlist no YouTube, incluindo os vídeos que ela contém, facilitando a análise e o gerenciamento dessas informações.