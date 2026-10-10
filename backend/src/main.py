"""App FastAPI do DownMusic."""
# load_dotenv deve rodar antes de qualquer import que leia os.getenv
from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import CORS_ORIGINS, PORT
from src.handlers import events, jobs, system
from src.services.instance import queue


@asynccontextmanager
async def lifespan(_app: FastAPI):
    queue.loop = asyncio.get_running_loop()
    yield
    print("\nEncerrando: cancelando fila e fechando conexões...")
    queue.close_streams()
    queue.stop()
    
    # Força a parada do processo se demorar muito (para não ficar preso esperando downloads)
    def _force_exit():
        import time, os
        time.sleep(2)
        os._exit(0)
    import threading
    threading.Thread(target=_force_exit, daemon=True).start()


app = FastAPI(title="DownMusic API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(jobs.router)
app.include_router(events.router)
app.include_router(system.router)


if __name__ == "__main__":
    import os
    print(f"\n=== DownMusic API === http://127.0.0.1:{PORT}  (Ctrl+C para parar)\n")
    uvicorn.run("src.main:app", host="127.0.0.1", port=PORT,
                reload=os.getenv("RELOAD") == "1", timeout_graceful_shutdown=3)
