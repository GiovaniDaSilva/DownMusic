# DownMusic

Uma aplicação simples e moderna para baixar o áudio de vídeos e playlists do YouTube. O projeto é executado inteiramente de forma local.

## Tecnologias

- **Backend:** Python, FastAPI, e [yt-dlp](https://github.com/yt-dlp/yt-dlp) (para processamento dos vídeos)
- **Frontend:** React, TypeScript, e Vite

## 🚀 Como instalar e rodar localmente

Se você acabou de clonar este repositório, você vai precisar do **Python**, do **Node.js** e do **FFmpeg** instalados no seu computador.

### 1. Pré-requisito importante: FFmpeg
O `yt-dlp` precisa do FFmpeg instalado para extrair e converter o áudio para MP3 (ou M4A).
- **Windows:** Baixe o FFmpeg, extraia, e adicione a pasta `bin` nas Variáveis de Ambiente (`PATH`), ou use o [Winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/): `winget install ffmpeg`
- **Linux/Mac:** Use seu gerenciador de pacotes (ex: `sudo apt install ffmpeg` ou `brew install ffmpeg`).

---

### 2. Configurando o Backend (Python)

Abra um terminal na pasta `backend/`:

1. Crie o ambiente virtual:
   ```bash
   python -m venv .venv
   ```

2. Ative o ambiente virtual:
   - No Windows: `.\.venv\Scripts\activate`
   - No Linux/Mac: `source .venv/bin/activate`

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie as variáveis de ambiente:
   - Copie o arquivo `.env.example` e cole como `.env`.

5. Rode a API:
   ```bash
   python -m src.main
   ```
   *O backend ficará rodando em `http://localhost:8000`.*

---

### 3. Configurando o Frontend (Node.js)

Abra outro terminal na pasta `frontend/`:

1. Instale as dependências do Node:
   ```bash
   npm install
   ```

2. Rode o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

3. Acesse a aplicação no seu navegador pelo link fornecido no terminal (geralmente `http://localhost:5173`).

---

## Estrutura do Projeto

```text
.
├── backend/
│   ├── src/                 # Código da API e do pipeline de download
│   ├── .env.example         # Exemplo das configurações
│   └── requirements.txt     # Dependências do Python
└── frontend/
    ├── src/                 # Interface em React/TypeScript
    └── package.json         # Dependências do Node
```
