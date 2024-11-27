import os.path

from youtube_analyzer import VideoMetadates

yt = VideoMetadates()


url_video = ''

video_info = yt.get_video_info(url_video=url_video)


highest_res_video = video_info.uris_stream.get_highest_resolution
print("Video Resolution:", highest_res_video.width, "x", highest_res_video.height)
print("Stream URI:", highest_res_video.url)
print("------------------------")

audio_info = yt.get_video_info(url_video=url_video)

best_audio_quality = video_info.uris_stream.get_best_audio_quality
print("Audio Quality Label:", best_audio_quality.audioQuality)
print("Stream URI:", best_audio_quality.url)

# Baixando as streams de vídeo e áudio
try:
    # Baixando a stream de vídeo
    video_path = highest_res_video.download_video(
        title='video_',
        output_dir='.',  # Caminho onde o vídeo será salvo
        logs=True,
        overwrite_output=True,
        connections=100  # Número de conexões para download simultâneo
    )
    if os.path.exists(video_path):
        print(f"Video salvo em: {video_path}")

    # Baixando a stream de áudio
    audio_path = best_audio_quality.download_audio(
        title='audio_',
        output_dir='.',  # Caminho onde o áudio será salvo
        logs=True,
        overwrite_output=True,
        connections=100  # Número de conexões para download simultâneo
    )
    if os.path.exists(audio_path):
        print(f"Áudio salvo em: {audio_path}")

except Exception as e:
    print(f"Erro ao baixar o vídeo ou áudio: {e}")
