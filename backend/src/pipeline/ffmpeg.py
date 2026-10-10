"""Localiza ou provisiona o ffmpeg (necessário para mp3/metadados)."""
import shutil


def setup_ffmpeg() -> str | None:
    """Retorna o caminho do ffmpeg, ou None se indisponível."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None
