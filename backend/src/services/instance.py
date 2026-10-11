"""Instância única da fila, compartilhada pelos handlers."""
from src.config import DOWNLOAD_DIR, MAX_PARALLEL, MAX_RETRIES
from src.services.download_queue import DownloadQueue

queue = DownloadQueue(DOWNLOAD_DIR, MAX_PARALLEL, MAX_RETRIES)
