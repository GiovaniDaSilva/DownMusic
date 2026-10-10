"""Fila de downloads em background com eventos para SSE."""
import asyncio
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict, field
from pathlib import Path

from src.pipeline.download import (download_audio, expand_playlist, extract_playlist_id,
                                   extract_video_id, find_existing)


@dataclass
class Job:
    url: str
    video_id: str | None
    fmt: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    kind: str = "video"  # video | playlist
    # video:    pending | downloading | done | skipped | error
    # playlist: expanding | expanded | error
    status: str = "pending"
    progress: float = 0
    speed: float | None = None
    eta: int | None = None
    title: str | None = None
    file: str | None = None
    error: str | None = None


class DownloadQueue:
    def __init__(self, out_dir: Path, workers: int = 1):
        self.out_dir = out_dir
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.subscribers: set[asyncio.Queue] = set()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.stopping = threading.Event()

    def stop(self) -> None:
        """Cancela a fila e interrompe downloads em andamento (usado no Ctrl+C)."""
        self.stopping.set()
        self.pool.shutdown(wait=False, cancel_futures=True)

    # ---- eventos ----
    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self.subscribers.discard(q)

    def _emit(self, job: Job) -> None:
        if not self.loop or self.loop.is_closed():
            return
        data = asdict(job)
        for q in list(self.subscribers):
            try:
                self.loop.call_soon_threadsafe(q.put_nowait, data)
            except RuntimeError:
                return

    def close_streams(self) -> None:
        """Envia sentinela para encerrar todas as conexões SSE."""
        if not self.loop or self.loop.is_closed():
            return
        for q in list(self.subscribers):
            self.loop.call_soon_threadsafe(q.put_nowait, None)

    # ---- operações ----
    def add(self, urls: list[str], fmt: str) -> list[Job]:
        created: list[Job] = []
        playlists: list[Job] = []
        with self.lock:
            active = {j.video_id for j in self.jobs.values()
                      if j.status in ("pending", "downloading")}
            for raw in urls:
                url = raw.strip()
                if not url:
                    continue
                vid = extract_video_id(url)
                # watch?v=X&list=Y baixa só o vídeo; /playlist?list=Y baixa a lista inteira
                if not vid and extract_playlist_id(url):
                    pl = Job(url=url, video_id=None, fmt=fmt, kind="playlist",
                             status="expanding", title="Lendo playlist…")
                    self.jobs[pl.id] = pl
                    playlists.append(pl)
                    continue
                if vid and vid in active:
                    continue
                job = Job(url=url, video_id=vid, fmt=fmt)
                self.jobs[job.id] = job
                created.append(job)
                if vid:
                    active.add(vid)
        for job in created:
            if not job.video_id:
                job.status, job.error = "error", "URL do YouTube inválida."
                self._emit(job)
            else:
                self._emit(job)
                self.pool.submit(self._run, job)
        for pl in playlists:
            self._emit(pl)
            threading.Thread(target=self._expand, args=(pl,), daemon=True).start()
        return created + playlists

    def _expand(self, pl: Job) -> None:
        try:
            title, video_urls = expand_playlist(pl.url)
        except Exception as exc:
            pl.status, pl.error = "error", str(exc)
            self._emit(pl)
            return
        if not video_urls:
            pl.status, pl.error = "error", "Playlist vazia ou privada."
            self._emit(pl)
            return
        added = self.add(video_urls, pl.fmt)
        pl.status, pl.progress, pl.title = "expanded", 100, f"Playlist: {title}"
        pl.file = f"{len(video_urls)} vídeos · {len(added)} adicionados à fila"
        self._emit(pl)

    def retry(self, job_id: str) -> Job | None:
        job = self.jobs.get(job_id)
        if not job or job.status != "error":
            return job
        if job.kind == "playlist":
            job.status, job.error, job.title = "expanding", None, "Lendo playlist…"
            self._emit(job)
            threading.Thread(target=self._expand, args=(job,), daemon=True).start()
            return job
        if not job.video_id:
            return job
        job.status, job.error, job.progress = "pending", None, 0
        self._emit(job)
        self.pool.submit(self._run, job)
        return job

    def clear_finished(self) -> None:
        with self.lock:
            for jid in [k for k, j in self.jobs.items() if j.status in ("done", "skipped", "expanded")]:
                del self.jobs[jid]

    def list(self) -> list[dict]:
        return [asdict(j) for j in self.jobs.values()]

    # ---- worker ----
    def _run(self, job: Job) -> None:
        existing = find_existing(self.out_dir, job.video_id)
        if existing:
            job.status, job.progress, job.file = "skipped", 100, existing.name
            job.title = existing.stem.rsplit(" [", 1)[0]
            self._emit(job)
            return

        job.status = "downloading"
        self._emit(job)

        def on_progress(p: dict) -> None:
            if self.stopping.is_set():
                raise KeyboardInterrupt("Servidor encerrando")
            job.progress, job.speed, job.eta = p["progress"], p["speed"], p["eta"]
            self._emit(job)

        try:
            result = download_audio(job.url, self.out_dir, job.fmt, on_progress)
            job.title, job.file = result["title"], result["file"]
            job.status, job.progress = "done", 100
        except Exception as exc:
            job.status, job.error = "error", str(exc)
        job.speed = job.eta = None
        self._emit(job)
