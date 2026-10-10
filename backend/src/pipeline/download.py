"""Download de áudio do YouTube via yt-dlp."""
import re
from pathlib import Path
from typing import Callable

import yt_dlp

from src.pipeline.ffmpeg import setup_ffmpeg

_ID_PATTERNS = [
    r"(?:v=|/v/)([A-Za-z0-9_-]{11})",
    r"youtu\.be/([A-Za-z0-9_-]{11})",
    r"/shorts/([A-Za-z0-9_-]{11})",
    r"/embed/([A-Za-z0-9_-]{11})",
]

ProgressFn = Callable[[dict], None]


def extract_video_id(url: str) -> str | None:
    for pat in _ID_PATTERNS:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def extract_playlist_id(url: str) -> str | None:
    m = re.search(r"[?&]list=([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def expand_playlist(url: str) -> tuple[str, list[str]]:
    """Lista os vídeos de uma playlist sem baixar. Retorna (título, urls)."""
    opts = {"extract_flat": "in_playlist", "quiet": True, "no_warnings": True, "no_color": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise RuntimeError(_ANSI_RE.sub("", str(exc)).replace("ERROR: ", "").strip()) from exc
    urls = [f"https://www.youtube.com/watch?v={e['id']}"
            for e in info.get("entries") or [] if e and e.get("id")]
    return info.get("title") or "sem título", urls


def find_existing(out_dir: Path, video_id: str) -> Path | None:
    for f in out_dir.glob(f"*[[]{video_id}[]].*"):
        if f.suffix.lower() in (".m4a", ".mp3", ".webm", ".opus"):
            return f
    return None


def download_audio(url: str, out_dir: Path, fmt: str = "m4a",
                   on_progress: ProgressFn | None = None) -> dict:
    """Baixa o áudio e retorna {'title', 'file'}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = setup_ffmpeg()

    def hook(d: dict) -> None:
        if not on_progress:
            return
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            on_progress({
                "progress": round(done * 100 / total, 1) if total else 0,
                "speed": d.get("speed"),
                "eta": d.get("eta"),
            })
        elif d["status"] == "finished":
            on_progress({"progress": 100, "speed": None, "eta": 0})

    opts: dict = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": str(out_dir / "%(title)s [%(id)s].%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "noprogress": True,
        "windowsfilenames": True,
        "retries": 5,
        "fragment_retries": 5,
        "progress_hooks": [hook],
    }
    if ffmpeg:
        opts["ffmpeg_location"] = ffmpeg
    if fmt == "mp3":
        if not ffmpeg:
            raise RuntimeError("ffmpeg não encontrado — necessário para mp3.")
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            {"key": "FFmpegMetadata"},
        ]

    last_error = ""
    for attempt, clients in enumerate(_CLIENT_FALLBACKS, start=1):
        attempt_opts = dict(opts)
        if clients:
            attempt_opts["extractor_args"] = {"youtube": {"player_client": clients}}
        try:
            with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                if attempt > 1:
                    ydl.cache.remove()
                info = ydl.extract_info(url, download=True)
            file = find_existing(out_dir, info["id"])
            return {"title": info.get("title"), "file": file.name if file else None}
        except Exception as exc:
            last_error = _ANSI_RE.sub("", str(exc)).replace("ERROR: ", "").strip()
            if "403" not in last_error:
                break  # erro não relacionado a bloqueio — não adianta repetir

    if "403" in last_error:
        last_error += (f" (após {len(_CLIENT_FALLBACKS)} tentativas) — DICA: tente novamente em alguns minutos "
                       "ou atualize o yt-dlp: .\\.venv\\Scripts\\python.exe -m pip install -U yt-dlp")
    raise RuntimeError(last_error)


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m|\[0;?\d*m")
# None = cliente padrão do yt-dlp; os demais são alternativas quando o YouTube devolve 403.
_CLIENT_FALLBACKS: list[list[str] | None] = [None, ["web_safari"], ["tv"], ["mweb"]]

