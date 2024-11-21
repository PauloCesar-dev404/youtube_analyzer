import json
import requests
from bs4 import BeautifulSoup


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


def extract_meta_og_image_width(playlist_url: str):
    """Extrai o conteúdo da meta tag 'og:image:width'."""
    response = requests.get(playlist_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    tag = soup.find('meta', property='og:image:width')
    if tag:
        return tag['content']
    return None


def extract_meta_og_image_height(playlist_url: str):
    """Extrai o conteúdo da meta tag 'og:image:height'."""
    response = requests.get(playlist_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tag = soup.find('meta', property='og:image:height')
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


def get_videos_playlist(playlist_url: str):
    """:return ids and indices de videos de uam playlist"""
    for_ids = []
    total = 0
    dts = {"total": total}
    response = requests.get(playlist_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    playlist_title = soup.find('title').text
    script = soup.find('script', string=lambda t: t and 'var ytInitialData =' in t)
    if script is None:
        raise ValueError('Não foi possível encontrar os dados no html....atualize o script')
    script_content = script.string
    json_text = script_content.split('var ytInitialData =', 1)[1].split(';</script>', 1)[0].strip().replace(';', '')
    data = json.loads(json_text)
    try:
        # Navegue pela estrutura JSON para encontrar a lista de vídeos
        videos = \
            data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
                'sectionListRenderer'][
                'contents'][0]['itemSectionRenderer']['contents']
        if not data:
            raise ValueError("playlist privada ou inválida!")
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

        return {'total': total, 'videos': for_ids, 'playlist_title': playlist_title}
    except KeyError:
        return None


