# DownMusic

Baixa o áudio de vídeos do YouTube a partir de uma lista de URLs. Roda **somente local**.

| Parte | Tecnologia | Descrição |
|---|---|---|
| `backend/` | Python + FastAPI + yt-dlp | API local: fila de downloads (pipeline baseada no satellite-v2 do UpLyric) |
| `frontend/` | React + Vite | Tela para colar as URLs e acompanhar a fila |

## Estrutura
```text
.
├── backend/
│   ├── src/
│   │   ├── handlers/        # Um handler por recurso HTTP (jobs, events, system)
│   │   ├── pipeline/        # download.py (yt-dlp), ffmpeg.py
│   │   ├── services/        # Fila de downloads
│   │   ├── config.py
│   │   └── main.py          # Entry point
│   ├── test/
│   └── downloads/           # Músicas baixadas
└── frontend/
    └── src/
        ├── views/           # DownloadPage
        ├── components/      # UrlInput, QueueList, JobCard
        └── hooks/           # useDownloadQueue (SSE)
```

## Primeira vez
```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Frontend
cd ..\frontend
npm install
```

## Rodar (dois terminais)
```powershell
# Terminal 1 — backend (http://127.0.0.1:8000)
cd backend; .\.venv\Scripts\python.exe -m src.main

# Terminal 2 — frontend (http://localhost:5173)
cd frontend; npm run dev
```

## Testes
```powershell
cd backend; .\.venv\Scripts\python.exe -m pytest test
```

> Erro 403? Atualize: `.\.venv\Scripts\python.exe -m pip install -U yt-dlp`
