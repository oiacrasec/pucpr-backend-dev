from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import SessionManager


def get_settings(request: Request) -> Settings:
    """Expoe as configuracoes armazenadas no estado da aplicacao FastAPI."""
    return request.app.state.settings


def get_session_manager(request: Request) -> SessionManager:
    """Expoe o gerenciador de sessoes compartilhado no estado da aplicacao."""
    return request.app.state.session_manager


def get_db_session(request: Request) -> Iterator[Session]:
    """Fornece uma sessao SQLAlchemy no escopo da requisicao."""
    manager = get_session_manager(request)
    with manager.session() as session:
        yield session
