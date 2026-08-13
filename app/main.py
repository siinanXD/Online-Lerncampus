"""FastAPI application entrypoint for Online Lerncampus."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.platform_routes import platform_router
from app.api.routes import api_router, bootstrap_content_store
from app.core.config import get_settings
from app.web.pages import allowed_frontend_pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize optional database-backed content on startup."""
    bootstrap_content_store()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        description="Lernplattform fuer technische Ausbildungsberufe.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api")
    app.include_router(platform_router, prefix="/api")
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

    @app.get(
        "/{page:path}",
        include_in_schema=False,
    )
    def index(page: str = "") -> FileResponse:
        """Serve the routed web app for all frontend page routes."""
        if page in allowed_frontend_pages():
            return FileResponse("app/web/index.html")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found.",
        )

    return app


app = create_app()
