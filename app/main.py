"""FastAPI application entrypoint for Online Lerncampus."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import MutableHeaders

from app.api.platform_routes import platform_router
from app.api.routes import api_router, bootstrap_content_store
from app.core.config import SESSION_COOKIE_NAME, get_settings
from app.web.pages import allowed_frontend_pages

CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data:",
        "connect-src 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    )
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize optional database-backed content on startup."""
    bootstrap_content_store()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    settings.assert_production_safety()
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

    @app.middleware("http")
    async def session_cookie_auth(request: Request, call_next):
        """Authenticate browser requests via the HttpOnly session cookie.

        The Authorization header keeps working for API clients; the cookie is
        only promoted to a bearer header when no header is present.
        """
        if "authorization" not in request.headers:
            token = request.cookies.get(SESSION_COOKIE_NAME)
            if token:
                MutableHeaders(scope=request.scope)["Authorization"] = (
                    f"Bearer {token}"
                )
        return await call_next(request)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        """Attach browser security headers to every response."""
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        if settings.is_production_like:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response

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
