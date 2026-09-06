**English** | [Português](README.pt-BR.md)

# Open Download API

A REST API for extracting metadata and downloading videos/audio from YouTube (including YouTube Music), with playlist support (limited to 15 items).

⚠️ **Disclaimer**: users are responsible for only downloading content they have the right to download.

## Stack

- **Python 3.12** with [uv](https://docs.astral.sh/uv/) for dependency management
- **FastAPI** — web framework
- **yt-dlp** — media extraction/download
- **ffmpeg** — audio conversion / video muxing (invoked internally by yt-dlp)
- **Redis** — job state storage + Celery broker
- **Celery** — async task queue for downloads
- **Pydantic** — validation and schemas
- **pytest** — automated tests

## Architecture

- **Strategy pattern** (`core/downloader.py`, `core/youtube_downloader.py`) — each supported platform implements the `Downloader` interface. Currently only `YoutubeDownloader` exists, covering `youtube.com`, `music.youtube.com`, and `youtu.be`.
- **PlatformDetector** (`core/platform_detector.py`) — selects the right strategy based on the URL.
- **Mapper** (`mappers/`) — normalizes yt-dlp's raw response into domain models (`VideoInfo`, `DownloadResult`).
- **JobStore** (`jobs/`) — an interface with two implementations: `InMemoryJobStore` (simple, non-persistent) and `RedisJobStore` (used at runtime).
- **Queue** (`tasks/`) — the actual download runs in a Celery task, decoupled from the API.

## System requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker (to run Redis) — or a local Redis instance
- **ffmpeg** installed and on the PATH:
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

## Setup

```bash
uv sync
cp .env.example .env  # adjust if needed
```

Start Redis (if you don't already have one running):

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
# next time, just: docker start redis-dev
```

## Running locally (2 processes)

**Terminal 1 — API:**
```bash
uv run uvicorn open_download_api.main:app --reload
```

**Terminal 2 — Celery worker** (processes downloads in the background):
```bash
uv run celery -A open_download_api.tasks.celery_app worker --loglevel=info
```

Once running:
- Interactive docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Environment variables

See `.env.example`. Configurable via `settings.py`:

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `JOB_STORE_REDIS_DB` | `1` | Redis database used to store job state |
| `CELERY_BROKER_DB` | `0` | Redis database used as the Celery broker |

## Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/extract-info` | Extracts metadata from a video/playlist (no download) |
| POST | `/download` | Queues a download, returns a `job_id` |
| GET | `/status/{job_id}` | Checks a job's status/progress |
| GET | `/download/{job_id}/file` | Downloads the result (`.zip`) of a finished job |

Full request/response schemas are available at `/docs` while the server is running.
