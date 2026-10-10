"""Recurso /api/jobs."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import AUDIO_FORMAT
from src.services.instance import queue

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobsIn(BaseModel):
    urls: list[str]
    format: str | None = None


@router.get("")
def list_jobs():
    return queue.list()


@router.post("")
def create_jobs(body: JobsIn):
    fmt = body.format if body.format in ("m4a", "mp3") else AUDIO_FORMAT
    return {"created": len(queue.add(body.urls, fmt))}


@router.post("/{job_id}/retry")
def retry_job(job_id: str):
    if not queue.retry(job_id):
        raise HTTPException(404, "Job não encontrado")
    return {"ok": True}


@router.delete("/finished")
def clear_finished():
    queue.clear_finished()
    return {"ok": True}
