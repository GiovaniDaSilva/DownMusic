import time
from pathlib import Path
from unittest.mock import patch

from src.services.download_queue import DownloadQueue, Job


def test_auto_retry_success(tmp_path: Path):
    queue = DownloadQueue(tmp_path, workers=1, max_retries=1)

    attempts = 0

    def mock_download(url, out_dir, fmt, on_progress=None):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("Transient network error")
        return {"title": "Test Title", "file": "test.mp3"}

    with patch("src.services.download_queue.download_audio", side_effect=mock_download):
        with patch.object(queue.stopping, "wait", return_value=False):
            job = Job(url="https://www.youtube.com/watch?v=12345678901", video_id="12345678901", fmt="mp3")
            queue.jobs[job.id] = job
            queue._run(job)

    assert attempts == 2
    assert job.status == "done"
    assert job.retries == 1
    assert job.error is None
    assert job.file == "test.mp3"
    queue.stop()


def test_auto_retry_fails_and_proceeds(tmp_path: Path):
    queue = DownloadQueue(tmp_path, workers=1, max_retries=1)

    calls = []

    def mock_download(url, out_dir, fmt, on_progress=None):
        calls.append(url)
        if "bad" in url:
            raise RuntimeError("Persistent error")
        return {"title": "Good Song", "file": "good.mp3"}

    with patch("src.services.download_queue.download_audio", side_effect=mock_download):
        with patch.object(queue.stopping, "wait", return_value=False):
            # Job 1 falha em todas as tentativas
            job1 = Job(url="https://www.youtube.com/watch?v=bad12345678", video_id="bad12345678", fmt="mp3")
            queue.jobs[job1.id] = job1
            queue._run(job1)

            # Job 2 (o próximo da fila) é executado e tem sucesso
            job2 = Job(url="https://www.youtube.com/watch?v=good1234567", video_id="good1234567", fmt="mp3")
            queue.jobs[job2.id] = job2
            queue._run(job2)

    # Job 1 tentou 2 vezes (1 normal + 1 retry), deu erro e seguiu
    assert calls.count("https://www.youtube.com/watch?v=bad12345678") == 2
    assert job1.status == "error"
    assert job1.retries == 1
    assert "Persistent error" in (job1.error or "")

    # Job 2 executou com sucesso em seguida
    assert job2.status == "done"
    assert job2.retries == 0
    assert job2.file == "good.mp3"
    queue.stop()


def test_manual_retry_resets_retries_counter(tmp_path: Path):
    queue = DownloadQueue(tmp_path, workers=1, max_retries=1)
    job = Job(url="https://www.youtube.com/watch?v=12345678901", video_id="12345678901", fmt="mp3")
    job.status = "error"
    job.retries = 1
    job.error = "Failed before"
    queue.jobs[job.id] = job

    with patch.object(queue.pool, "submit"):
        retried = queue.retry(job.id)

    assert retried is not None
    assert retried.status == "pending"
    assert retried.retries == 0
    assert retried.error is None
    queue.stop()
