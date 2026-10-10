"""Recurso /api/config e /api/open-folder."""
import os

from fastapi import APIRouter

from src.config import AUDIO_FORMAT, DOWNLOAD_DIR

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/config")
def get_config():
    return {"format": AUDIO_FORMAT, "download_dir": str(DOWNLOAD_DIR)}


@router.post("/open-folder")
def open_folder():
    if hasattr(os, "startfile"):
        os.startfile(DOWNLOAD_DIR)  # type: ignore[attr-defined]
    return {"ok": True}
