@echo off
echo Iniciando o DownMusic...

echo Iniciando o Backend...
start "DownMusic Backend" cmd /k "cd backend && call .\.venv\Scripts\activate && python -m src.main"

echo Iniciando o Frontend...
start "DownMusic Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Tudo certo! As janelas do backend e frontend foram abertas.
echo Backend deve rodar na porta 8000 e o Frontend na porta 5173.
echo.
