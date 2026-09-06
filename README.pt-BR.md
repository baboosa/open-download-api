[English](README.md) | **Português**

# Open Download API

Uma API REST para extrair metadados e baixar vídeos/áudios do YouTube (incluindo YouTube Music), com suporte a playlists (limitadas a 15 itens).

⚠️ **Aviso**: os usuários são responsáveis por só baixar conteúdo que tenham o direito de baixar.

## Stack

- **Python 3.12** com [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências
- **FastAPI** — framework web
- **yt-dlp** — extração/download de mídia
- **ffmpeg** — conversão de áudio/mesclagem de vídeo (chamado internamente pelo yt-dlp)
- **Redis** — armazenamento de estado dos jobs + broker do Celery
- **Celery** — fila de processamento assíncrono dos downloads
- **Pydantic** — validação e schemas
- **pytest** — testes automatizados

## Arquitetura

- **Strategy pattern** (`core/downloader.py`, `core/youtube_downloader.py`) — cada plataforma suportada implementa a interface `Downloader`. Hoje só existe `YoutubeDownloader`, cobrindo `youtube.com`, `music.youtube.com` e `youtu.be`.
- **PlatformDetector** (`core/platform_detector.py`) — escolhe a strategy correta a partir da URL.
- **Mapper** (`mappers/`) — normaliza a resposta crua do yt-dlp em modelos de domínio (`VideoInfo`, `DownloadResult`).
- **JobStore** (`jobs/`) — uma interface com duas implementações: `InMemoryJobStore` (simples, não persiste) e `RedisJobStore` (usada em runtime).
- **Fila** (`tasks/`) — o download real roda numa task Celery, desacoplada da API.

## Pré-requisitos de sistema

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker (para rodar o Redis) — ou um Redis já instalado localmente
- **ffmpeg** instalado e no PATH:
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

## Setup

```bash
uv sync
cp .env.example .env  # ajuste se necessário
```

Subir o Redis (se ainda não tiver um rodando):

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
# nas próximas vezes, só: docker start redis-dev
```

## Rodando localmente (2 processos)

**Terminal 1 — API:**
```bash
uv run uvicorn open_download_api.main:app --reload
```

**Terminal 2 — Worker Celery** (processa os downloads em background):
```bash
uv run celery -A open_download_api.tasks.celery_app worker --loglevel=info
```

Depois disso:
- Docs interativas (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Variáveis de ambiente

Ver `.env.example`. Configuráveis via `settings.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `REDIS_HOST` | `localhost` | Host do Redis |
| `REDIS_PORT` | `6379` | Porta do Redis |
| `JOB_STORE_REDIS_DB` | `1` | Banco Redis usado para guardar estado dos jobs |
| `CELERY_BROKER_DB` | `0` | Banco Redis usado como fila do Celery |

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/extract-info` | Extrai metadados de um vídeo/playlist (sem baixar) |
| POST | `/download` | Enfileira um download, retorna `job_id` |
| GET | `/status/{job_id}` | Consulta status/progresso do job |
| GET | `/download/{job_id}/file` | Baixa o resultado (`.zip`) de um job finalizado |

Contrato completo (schemas de request/response) disponível em `/docs` com o servidor rodando.
