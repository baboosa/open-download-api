from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from open_download_api.api.download import router as download_router
from open_download_api.api.extract import router as extract_router
from open_download_api.api.health import router as health_router
from open_download_api.api.status import router as status_router
from open_download_api.settings import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(download_router)
app.include_router(health_router)
app.include_router(extract_router)
app.include_router(status_router)