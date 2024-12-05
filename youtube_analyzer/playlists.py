import json
import requests
from bs4 import BeautifulSoup
from .exeptions import YoutubeRequestError, InvalidPlaylistError, YoutubeAnalyzerExceptions


def extract_meta_og_title(playlist_url: str):
    """Extrai o conteúdo da meta tag 'og:title'."""
    response = requests.get(playlist_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    tag = soup.find('meta', property='og:title')
    if tag:
        return tag['content']
    return None


def extract_meta_og_description(playlist_url: str):
    """Extrai o conteúdo da meta tag 'og:description'."""
    response = requests.get(playlist_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    tag = soup.find('meta', property='og:description')
    if tag:
        return tag['content']
    return None


def extract_meta_og_image(playlist_url: str):
    """Extrai o conteúdo da meta tag 'og:image'."""
    response = requests.get(playlist_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    tag = soup.find('meta', property='og:image')
    if tag:
        return tag['content']
    return None


def create_urls(data: dict):
    """
    Cria uma URL de visualização para cada vídeo com base no ID fornecido.

    :param data: Dicionário contendo a lista de vídeos com seus IDs.
    :return: Lista de URLs de visualização dos vídeos.
    """
    url_base = "https://www.youtube.com/watch?v="
    urls = []
    videos = data.get("videos", [])
    for video in videos:
        video_id = video.get('videoId')
        index = video.get("index")
        title = video.get('title')
        thumbnail = video.get('thumbnail')
        if video_id:
            url = f"{url_base}{video_id}"
            d = {"index": index, "title": title, "url": url, 'thumbnail': thumbnail}
            urls.append(d)

    return urls


def metadata(sidebar: dict) -> dict:
    try:
        playlistSidebarRenderer = sidebar['playlistSidebarRenderer']
        items = playlistSidebarRenderer['items']
        primary_info = items[0]
        secondary_info = items[1]
        # Acessa o bloco com as informações do dono do vídeo/canal
        owner_data = secondary_info['playlistSidebarSecondaryInfoRenderer']['videoOwner']['videoOwnerRenderer']

        # Extrai o nome do canal
        channel_name = owner_data['title']['runs'][0]['text']
        description = primary_info['playlistSidebarPrimaryInfoRenderer'].get('description')
        video_count = primary_info['playlistSidebarPrimaryInfoRenderer']['stats'][0]['runs'][0]['text']
        # Extraindo visualizações
        views = primary_info['playlistSidebarPrimaryInfoRenderer']['stats'][1]['simpleText']
        # Extraindo última atualização
        last_updated = primary_info['playlistSidebarPrimaryInfoRenderer']['stats'][2]['runs'][1]['text']
        return {
            'channel_name': channel_name,
            'video_count': video_count,
            'views': views.replace("visualizações", '').strip(),
            'last_updated': last_updated
        }
    except KeyError as e:
        raise KeyError(f"Erro ao processar dados: Chave faltando {e}")
    except TypeError as e:
        raise TypeError(f"Erro ao obter dado da playlist: {e}")


def get_videos_playlist(playlist_url: str):
    """:return ids and indices de videos de uam playlist"""
    data, playlist_title = None, None
    for_ids = []
    total = 0
    dts = {"total": total}
    try:
        response = requests.get(playlist_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        playlist_title = soup.find('title').text
        script = soup.find('script', string=lambda t: t and 'var ytInitialData =' in t)
        if script is None:
            raise ValueError('Não foi possível encontrar os dados no html....atualize o script')
        script_content = script.string
        json_text = script_content.split('var ytInitialData =', 1)[1].split(';</script>', 1)[0].strip().replace(';', '')
        data = json.loads(json_text)
    except Exception as e:
        YoutubeRequestError()
    try:
        sidebar = data['sidebar']
        metadatas = metadata(sidebar=sidebar)
        # Navegue pela estrutura JSON para encontrar a lista de vídeos
        videos = \
            data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
                'sectionListRenderer'][
                'contents'][0]['itemSectionRenderer']['contents']
        if not data:
            raise InvalidPlaylistError()
        # Extraia informações
        for video in videos:
            dados = video['playlistVideoListRenderer']
            contents = dados.get("contents")
            for idx, v in enumerate(contents):
                brute = v['playlistVideoRenderer']
                video_id = brute['videoId']
                title = brute['title']['runs'][0]['text']
                thumbnail = brute['thumbnail']['thumbnails']
                highest_res = max(thumbnail, key=lambda x: x['width'])
                if video_id and title:
                    total += 1
                    dts[f'{idx}'] = video_id
                    for_ids.append({'index': idx, 'videoId': video_id, 'title': title, 'thumbnail': highest_res})

        return {'total': total, 'videos': for_ids, 'playlist_title': playlist_title,
                'views': metadatas.get("views"), 'last_updated': metadatas.get('last_updated'),
                'channel_name': metadatas.get('channel_name')}
    except KeyError as e:
        raise InvalidPlaylistError()

