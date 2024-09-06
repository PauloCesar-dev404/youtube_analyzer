import os
import re
import sys
from typing import Optional, Callable
import emoji
import requests
from .utils import debug


def sanitize_filename(filename: str) -> str:
    r"""Remove caracteres inválidos no Windows: \ / : * ? " < > | e emojis"""
    # Remove caracteres inválidos
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Remove emojis usando a biblioteca emoji
    sanitized = emoji.replace_emoji(sanitized, replace='')  # Remove qualquer emoji

    return sanitized


def format_bytes(size: int) -> str:
    """Formata bytes em KB, MB, GB, etc."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


downloads_dir = os.path.join('youtube_parser_downloads')
os.makedirs(downloads_dir, exist_ok=True)


def download_video(title: str,
                   uri: str,
                   file_extension: str = 'mp4',
                   output_dir: str = 'downloads',
                   overwrite_output: bool = False,
                   logs: bool = None,
                   capture_chunks: Optional[Callable[[int], None]] = None):
    """
    Faz o download de um vídeo e salva no diretório especificado.

    Se `logs` for fornecido, exibirá uma barra de progresso; caso contrário, retornará um gerador.

    :param title: Título do vídeo.
    :param uri: URL do vídeo para download.
    :param file_extension: Extensão do arquivo (padrão é 'mp4').
    :param output_dir: Diretório de saída onde o vídeo será salvo.
    :param overwrite_output: Se True, sobrescreve o arquivo se ele já existir.
    :param logs: Função de callback para logs, exibira todo progresso
    :param capture_chunks: Função de callback para capturar o andamento do download.
    :return:.
    """
    # Cria o diretório de saída se não existir
    if not os.path.exists(output_dir):
        if logs:
            debug("warn", f"o dir {output_dir},não existe criando........", end=' ')
        os.makedirs(output_dir)
        if logs:
            debug('info', ' criado!')
    # Define o caminho completo para salvar o arquivo
    file_path = os.path.join(output_dir, f"{sanitize_filename(title)}.{file_extension}")
    # Verifica se o arquivo já existe
    file_exists = os.path.exists(file_path)
    # Sobrescrever o arquivo se `overwrite_output` for True
    if file_exists and overwrite_output:
        if logs:
            debug('info', f'sobrescrevendo aquivo!')
        os.remove(file_path)
        file_exists = False

    if file_exists:
        raise FileExistsError(f"Arquivo já existe: {file_path}")

    def download_generator():
        """Gerador que baixa o vídeo em pedaços e atualiza o progresso se necessário."""
        try:
            chunk_size = 8192
            response = requests.get(uri, stream=True)
            response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP de erro

            total_length = int(response.headers.get('content-length', 0))

            with open(file_path, 'wb') as out_file:
                downloaded = 0  # Inicializa o total de bytes baixados
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        out_file.write(chunk)
                        chunk_size = len(chunk)
                        downloaded += chunk_size
                        if capture_chunks:
                            capture_chunks(chunk_size)
                        if logs:
                            # Calcula a porcentagem de progresso
                            percentage = (downloaded / total_length) * 100
                            # Atualiza a linha de progresso
                            sys.stdout.write(
                                f'\rProgresso: {format_bytes(downloaded)}/{format_bytes(total_length)}'
                                f' ({percentage:.2f}%)')
                            sys.stdout.flush()
                        yield chunk_size
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro ao baixar o vídeo: {e}")

    if logs:
        for _ in download_generator():
            pass
        if logs:
            debug("info", f"\tDownload completo!")
        return file_path
    else:
        # Retorna o gerador para uso posterior
        return download_generator()
