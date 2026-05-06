from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base


class SessionManager:
    """Mantem o engine do SQLAlchemy e fornece sessoes de curta duracao."""

    def __init__(self, database_url: str, echo: bool = False) -> None:
        engine_options: dict[str, object] = {"echo": echo, "future": True}
        if database_url.startswith("sqlite"):
            engine_options["connect_args"] = {"check_same_thread": False}

        self._engine: Engine = create_engine(database_url, **engine_options)
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
            class_=Session,
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Entrega uma sessao de banco e garante o fechamento ao final."""
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_schema(self) -> None:
        """Cria as tabelas mapeadas diretamente a partir do metadata."""
        Base.metadata.create_all(bind=self._engine)

    def dispose(self) -> None:
        """Descarta o engine do SQLAlchemy e suas conexoes em pool."""
        self._engine.dispose()
