import datetime
import os
import re
from decimal import Decimal
from urllib.parse import urlparse

import colorama

colorama.init(autoreset=True)
YOUTUBE_PLAYER_ENDPOINT = "https://www.youtube.com/youtubei/v1/player"
YOUTUBE_PLAYER_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
YOUTUBE_CLIENT_VERSION = "17.43.36"
YOUTUBE_CLIENT_USER_AGENT = f"com.google.android.youtube/{YOUTUBE_CLIENT_VERSION} (Linux; U; Android 13)"
YOUTUBE_PLAYER_HEADERS = {
    "X-Youtube-Client-Name": "3",
    "X-Youtube-Client-Version": YOUTUBE_CLIENT_VERSION,
    "Origin": "https://www.youtube.com",
    "Content-Type": "application/json",
    "User-Agent": YOUTUBE_CLIENT_USER_AGENT
}


def is_valid(url: str) -> bool:
    """
    Verifica se a URL fornecida é válida e pertence ao YouTube (vídeo ou playlist).

    Args:
        url (str): A URL a ser verificada.

    Returns:
        bool: True se a URL for válida e pertencer ao YouTube, False caso contrário.
    """
    if not url.startswith("https://"):
        return False

    # Verifica se o domínio é do YouTube
    parsed_url = urlparse(url)
    if parsed_url.netloc not in ["www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be"]:
        return False

    # Expressão regular para verificar IDs de vídeos e playlists
    regex = (
        r'(?:youtube\.com\/(?:.*?\/)?(?:playlist\?list=|watch\?v=|e(?:mbed)?\/|shorts\/|live\/)?|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'  # ID de vídeo
        r'|playlist\?list=([a-zA-Z0-9_-]+)'  # ID de playlist
    )

    return bool(re.search(regex, url))


def get_id(url: str) -> str:
    """
    Obtém o ID do vídeo do YouTube a partir de uma URL.

    :param url: URL do vídeo do YouTube.
    :return: ID do vídeo do YouTube, ou None se não for possível extrair o ID.
    """
    regex = (
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|live\/|shorts\/)?|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    match = re.search(regex, url)
    if match:
        video_id = match.group(1)
        if 'live/' in url:
            return f"https://www.youtube.com/live/{video_id}"
        elif 'shorts/' in url:
            return f"https://www.youtube.com/shorts/{video_id}"
        else:
            return f"https://www.youtube.com/embed/{video_id}"
    return ''


def debug(type_d: str, msg, end='\n'):
    """Exibe mensagens de depuração com cores baseadas no tipo.

    Args:
        type_d (str): Tipo da mensagem (erro, info, warn).
        msg : Mensagem a ser exibida.
        end (str, optional): String a ser impressa após a mensagem. Padrão é '\n'.
    """
    colors = {
        'erro': colorama.Fore.LIGHTRED_EX,
        'info': colorama.Fore.LIGHTCYAN_EX,
        'warn': colorama.Fore.LIGHTYELLOW_EX,
        'true': colorama.Fore.LIGHTGREEN_EX
    }

    # Obter a cor com base no tipo
    color = colors.get(type_d, colorama.Fore.RESET)

    # Imprimir a mensagem com a cor especificada
    print(f'{color} {msg}', end=end)


def format_bytes(size):
    """Formata bytes em KB, MB, GB, etc."""
    try:
        size = int(size)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if int(size) < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{int(size):.2f} PB"
    except Exception:
        return size


def timestamp(timestamps):
    """

    :type timestamps: numero
    """
    try:
        seconds = int(timestamps) / 1_000_000
        # Converta para datetime
        dt = datetime.datetime.fromtimestamp(seconds)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return timestamps


def ms_convert(ms):
    try:
        # Converte milissegundos para segundos
        segundos = int(ms) // 1000
        # Calcula horas, minutos e segundos
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60

        # Retorna a string formatada
        return f'{horas:02}:{minutos:02}:{segundos_restantes:02}'
    except Exception:
        return ms


def mon_ste(can: int):
    if can == 1:
        return "Mono"
    elif can == 2:
        return "Stéreo"
    elif can is None:
        return "Not audio"
    else:
        return can


def convert_bitrate_precise(bitrate_bps):
    """
    Converte a taxa de bits de bits por segundo (bps) para Kbps e Mbps usando precisão exata com Decimal.

    :param bitrate_bps: Taxa de bits em bps (bits por segundo).
    """
    try:
        # Usando Decimal para maior precisão
        bitrate_kbps = Decimal(int(bitrate_bps)) / Decimal(1000)
        return f"{bitrate_kbps}kbps"
    except Exception:
        return bitrate_bps




