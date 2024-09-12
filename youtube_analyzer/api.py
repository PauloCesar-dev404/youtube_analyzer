import datetime
import os
import re
from decimal import Decimal
from urllib.parse import urlparse
import colorama
import xml.etree.ElementTree as et
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


def clear():
    if os.name == 'nt':  # Para Windows
        os.system('cls')
    else:  # Para Unix/Linux/Mac
        os.system('clear')


def convert_xml_to_srt(xml_input_file, srt_file_name):
    tree = et.parse(xml_input_file)
    root = tree.getroot()

    with open(srt_file_name, 'w', encoding='utf-8') as srt_file:
        counter = 1
        for p in root.findall('.//p'):
            start_time = int(p.attrib['t'])
            duration = int(p.attrib.get('d', 0))
            end_time = start_time + duration

            # Formatar o tempo no formato SRT (horas:minutos:segundos,milissegundos)
            start_time_srt = format_time1(start_time)
            end_time_srt = format_time1(end_time)

            # Se p.text for None, tentamos pegar o texto das subtags <s>
            if p.text is not None:
                text = re.sub(r'<.*?>', '', p.text).replace("\n", " ")  # Remover tags e substituir quebras de linha
            else:
                # Caso o texto esteja nas subtags <s>, concatenamos o texto de cada subtag
                text = ''.join([s.text if s.text is not None else '' for s in p.findall('.//s')])

            # Formatar o conteúdo como uma legenda SRT
            srt_file.write(f"{counter}\n")
            srt_file.write(f"{start_time_srt} --> {end_time_srt}\n")
            srt_file.write(f"{text.strip()}\n\n")
            counter += 1


def format_time1(time_ms):
    """Converte o tempo de milissegundos para o formato SRT"""
    hours = time_ms // (1000 * 60 * 60)
    minutes = (time_ms // (1000 * 60)) % 60
    seconds = (time_ms // 1000) % 60
    milliseconds = time_ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def format_time(seconds):
    """Função para formatar o tempo em horas, minutos e segundos corretamente."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


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


def get_id_playlists(url: str) -> str:
    """
    :param url: url da playlist
    :return: id
    """
    regex = r'[?&]list=([a-zA-Z0-9_-]+)'
    match = re.search(regex, url)
    if match:
        return match.group(1)
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

