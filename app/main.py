from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.security import PasswordHasher
from app.db.session import SessionManager
from app.modules.identity_access_management.api.auth_router import router as auth_router
from app.modules.identity_access_management.api.roles_router import router as roles_router
from app.modules.identity_access_management.api.users_router import router as users_router
from app.modules.identity_access_management.bootstrap.seed import seed_identity_access_data


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Cria e configura a aplicacao FastAPI."""
    app_settings = settings or get_settings()
    configure_logging(app_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Inicializa infraestrutura compartilhada e executa o seed inicial."""
        session_manager = SessionManager(
            database_url=app_settings.database_url,
            echo=app_settings.database_echo,
        )
        app.state.settings = app_settings
        app.state.session_manager = session_manager

        if app_settings.auto_create_schema:
            session_manager.create_schema()

        if app_settings.seed_data:
            with session_manager.session() as session:
                seed_identity_access_data(
                    session=session,
                    settings=app_settings,
                    password_hasher=PasswordHasher(),
                )

        yield

        session_manager.dispose()

    app = FastAPI(
        title=app_settings.app_name,
        lifespan=lifespan,
        docs_url="/",
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(app_settings.cors_allowed_origins),
        allow_methods=list(app_settings.cors_allowed_methods),
        allow_headers=list(app_settings.cors_allowed_headers),
    )

    register_exception_handlers(app)

    app.include_router(auth_router, prefix=app_settings.api_prefix)
    app.include_router(users_router, prefix=app_settings.api_prefix)
    app.include_router(roles_router, prefix=app_settings.api_prefix)

    @app.get("/health", include_in_schema=False)
    def healthcheck() -> dict[str, str]:
        """Retorna um sinal simples de vida para verificacoes de infraestrutura."""
        return {"status": "ok"}

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        """Evita ruido de 404 do navegador ao requisitar o favicon padrao."""
        return Response(status_code=204)

    return app


app = create_app()
