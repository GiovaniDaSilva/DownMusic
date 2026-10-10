"""Instância única da fila, compartilhada pelos handlers."""
from src.config import DOWNLOAD_DIR, MAX_PARALLEL
from src.services.download_queue import DownloadQueue

queue = DownloadQueue(DOWNLOAD_DIR, MAX_PARALLEL)
