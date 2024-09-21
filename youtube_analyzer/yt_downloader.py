import os
import re
import subprocess
import sys
import tempfile
import time
import argparse
from youtube_analyzer import VideoMetadates, PlaylistMetadates
from youtube_analyzer.api import clear

try:
    from ffmpeg_for_python import FFmpeg
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg_for_python"])
    from ffmpeg_for_python import FFmpeg
try:
    import emoji
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "emoji"])
    import emoji
clear()
time.sleep(2)


class Playlists:

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        r"""Remove caracteres inválidos no Windows: \ / : * ? " < > | e emojis"""
        sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
        sanitized = emoji.replace_emoji(sanitized, replace='')  # Remove qualquer emoji
        return sanitized

    @staticmethod
    def get_info_video(url_video):
        try:
            v = VideoMetadates()
            video_info = v.get_video_info(url_video=url_video)
            resolution = video_info.uris_stream.get_highest_resolution

            return resolution
        except Exception as e:
            print(f"Erro ao obter informações de vídeo: {e}")

    @staticmethod
    def get_info_audio(url_video):
        try:
            v = VideoMetadates()
            audio_info = v.get_video_info(url_video=url_video)
            audioQuality = audio_info.uris_stream.get_best_audio_quality
            return audioQuality
        except Exception as e:
            print(f"Erro ao obter informações de audio: {e}")

    @staticmethod
    def remux(a_path, v_path, out):
        try:
            ffmpeg = FFmpeg()
            # Executa o comando de remux do ffmpeg
            process = (ffmpeg
                       .overwrite_output
                       .input(a_path)
                       .input(v_path)
                       .output(out)
                       .copy_codecs
                       .run())

            # Regex para capturar as informações desejadas (progresso)
            pattern = re.compile(
                r'frame=\s*(\d+)\s*fps=\s*(\d+)\s*q=\s*(-?\d+\.\d+)\s*size=\s*(\d+.*)\s*time=\s*(\d+:\d+:\d+.\d+)\s*bitrate=\s*(\d+.*)\s*speed=\s*(\d+.*)')

            # Captura a saída do ffmpeg em tempo real
            for line in process:
                match = pattern.search(line)
                if match:
                    frame, fps, quality, size, time, bitrate, speed = match.groups()
                    # Gera a saída formatada
                    sys.stdout.write(
                        f"\rFrame: {frame} | FPS: {fps} | Qualidade: {quality} | Tamanho: {size} | Tempo: {time} | Bitrate: {bitrate} | Velocidade: {speed}")
                    sys.stdout.flush()
            sys.stdout.write(f"\nArquivo salvo em: {out}")
        except Exception as e:
            raise f"Erro ao remuxar: {e}"

    def download_playlist_videos(self, playlist_url, output_dir, audio=None,skip=None):
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp('downloads_yt_')
        pl = PlaylistMetadates()
        playlist_info = pl.get_playlist_info(playlist_url=playlist_url)

        if playlist_info.is_private:
            print("A playlist é privada. Não é possível baixar vídeos.")
            return
        videos = playlist_info.get_all_videos
        print(f"Encontrados {len(videos)} vídeos na playlist.")

        for video in videos:
            video_url = video.get('url_watch')
            video_title = video.get('title')
            if audio:
                uri_a = self.get_info_audio(url_video=video_url)
                title_a = self.sanitize_filename(f"AUDIO_{video_title}")
                print(f"Baixando Audio: {video_title}")
                if os.path.exists(os.path.join(output_dir,f'{title_a}.mp4')):
                    if skip:
                        return
                uri_a.download_audio(title=title_a, output_dir=temp_dir, overwrite_output=True, logs=True)
            print(f"Baixando Vídeo: {video_title}")
            uri = self.get_info_video(video_url)
            title_v = self.sanitize_filename(video_title)
            out = os.path.join(output_dir, f"{title_v}.mp4")
            if os.path.exists(os.path.join(out)):
                if skip:
                    return
            v_path = uri.download_video(title=title_v, overwrite_output=True, output_dir=temp_dir, logs=True)
            uri_a = self.get_info_audio(url_video=video_url)
            title_a = self.sanitize_filename(f"AUDIO_{video_title}")
            print(f"Baixando Audio: {video_title}")
            if os.path.exists(os.path.join(out)):
                if skip:
                    return
            a_path = uri_a.download_audio(title=title_a, output_dir=temp_dir, overwrite_output=True, logs=True)
            print("Remuxando.........")
            time.sleep(2)
            self.remux(a_path=a_path, v_path=v_path, out=out)
            os.remove(a_path)
            os.remove(v_path)

    def download_video(self, video_url, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp('downloads_yt_')
        yt = VideoMetadates()
        video_info = yt.get_video_info(url_video=video_url)

        if video_info.is_private:
            print("O vídeo é privada. Não é possível baixar vídeos privados")
            return
        video_title = video_info.title
        print(f"Baixando Vídeo: {video_title}")
        uri = self.get_info_video(video_url)
        title_v = self.sanitize_filename(video_title)
        out = os.path.join(output_dir, f"{title_v}.mp4")
        v_path = uri.download_video(title=title_v, overwrite_output=True, output_dir=temp_dir, logs=True)
        uri_a = self.get_info_audio(url_video=video_url)
        title_a = self.sanitize_filename(f"AUDIO_{video_title}")
        print(f"Baixando Audio: {video_title}")
        a_path = uri_a.download_audio(title=title_a, output_dir=temp_dir, overwrite_output=True, logs=True)
        print("Remuxando.........")
        time.sleep(2)
        self.remux(a_path=a_path, v_path=v_path, out=out)
        os.remove(a_path)
        os.remove(v_path)

    def download_video_audio(self, video_url, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        yt = VideoMetadates()
        video_info = yt.get_video_info(url_video=video_url)
        if video_info.is_private:
            print("O vídeo é privada. Não é possível baixar vídeos privados")
            return
        video_title = video_info.title
        uri_a = self.get_info_audio(url_video=video_url)
        title_a = self.sanitize_filename(f"{video_title}")
        print(f"Baixando Audio: {video_title}")
        uri_a.download_audio(title=title_a, output_dir=output_dir, overwrite_output=True, logs=True)


def verific(url: str) -> bool:
    """
    Verifica se a URL é de uma playlist do YouTube.
    """
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.*[?&]list=([a-zA-Z0-9_-]+)"
    return re.match(pattern, url) is not None


def print_help():
    help_text = """
    yt-downloader vBETA
    ---------------------

    Comandos disponíveis:

    -p, --playlist    URL da playlist do YouTube
    -v, --video       URL do vídeo individual do YouTube
    -a, --audio       Baixar apenas o áudio
    -o, --output      Diretório de saída para os vídeos/áudios baixados (padrão: 'downloads')

    Exemplos:

    1. Baixar todos os vídeos de uma playlist:
       python yt-downloader -p https://www.youtube.com/playlist?list=PLxxxxxx

    2. Baixar um vídeo específico:
       python yt-downloader -v https://www.youtube.com/watch?v=xxxxxx

    3. Baixar apenas o áudio de um vídeo:
       python yt-downloader -v https://www.youtube.com/watch?v=xxxxxx -a

    4. Baixar apenas o áudio de vídeos de uma playlist:
       python yt-downloader -p https://www.youtube.com/playlist?list=PLxxxxxx -a

    5. Especificar um diretório de saída:
       python yt-downloader -v https://www.youtube.com/watch?v=xxxxxx -o meu_diretorio

    """
    print(help_text)


def main():
    # Configurando o argparse para os argumentos fornecidos
    parser = argparse.ArgumentParser(description="Download de vídeos ou playlists do YouTube", add_help=False)

    # Adiciona os argumentos esperados
    parser.add_argument('-h', '--help', action='store_true', help='Mostrar esta mensagem de ajuda')
    parser.add_argument('-p', '--playlist', type=str, help='URL da playlist do YouTube')
    parser.add_argument('-v', '--video', type=str, help='URL do vídeo individual do YouTube')
    parser.add_argument('-a', '--audio', action='store_true', help='Baixar apenas o áudio')
    parser.add_argument('-o', '--output', type=str, default='downloads',
                        help='Diretório de saída para os vídeos/áudios baixados')
    parser.add_argument('--overwrite', help='sobrescrever arquivos existente')
    parser.add_argument('--skip',help='pula arquivos existentes')

    # Parseia os argumentos da linha de comando
    args = parser.parse_args()
    p = Playlists()

    if args.help:
        print_help()
        sys.exit(0)
    if args.playlist:
        # Chamar a função para download da playlist
        if args.audio:
            if args.skip:
                print(f"Baixando apenas os áudios dos vídeos da playlist: {args.playlist}")
                p.download_playlist_videos(args.playlist, args.output, True)
        else:
            p.download_playlist_videos(args.playlist, args.output)
    elif args.video:
        if args.audio:
            print(f"Baixando apenas o áudio do vídeo: {args.video}")
            # Chamar a função para download do áudio do vídeo
            p.download_video_audio(args.video, args.output)
        else:
            print(f"Baixando o vídeo: {args.video}")
            # Chamar a função para download do vídeo
            p.download_video(args.video, args.output)

    else:
        print("Por favor, forneça uma URL de vídeo (-v) ou de playlist (-p) para baixar.")


if __name__ == "__main__":
    max_t = 4
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("interrompido!")
        except Exception as e:
            if max_t <= 4:
                print(f"ERRO: {e} -> tentando novamente.....")
                max_t += 1
                time.sleep(3)
                continue
            else:
                exit(1)
