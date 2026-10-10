"""Configuração do backend DownMusic (lida do .env)."""
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", BACKEND_DIR / "downloads")).resolve()
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "mp3").lower()
if AUDIO_FORMAT not in ("m4a", "mp3"):
    AUDIO_FORMAT = "mp3"
MAX_PARALLEL = max(1, int(os.getenv("MAX_PARALLEL", "1")))
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = [o.strip() for o in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
