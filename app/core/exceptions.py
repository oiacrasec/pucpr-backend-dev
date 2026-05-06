from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@dataclass
class ApplicationError(Exception):
    """Excecao base para falhas HTTP controladas da aplicacao."""

    message: str
    status_code: int
    code: str
    details: list[dict[str, str]] = field(default_factory=list)


class BadRequestError(ApplicationError):
    """Representa um erro do cliente causado por entrada invalida de negocio."""

    def __init__(self, message: str, details: Optional[list[dict[str, str]]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="bad_request",
            details=details or [],
        )


class UnauthorizedError(ApplicationError):
    """Representa uma falha de autenticacao."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="unauthorized",
        )


class ForbiddenError(ApplicationError):
    """Representa uma falha de autorizacao."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="forbidden",
        )


class NotFoundError(ApplicationError):
    """Representa a ausencia de um recurso de dominio."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
        )


async def application_error_handler(_: Request, exc: ApplicationError) -> JSONResponse:
    """Traduz excecoes controladas para o payload publico de erro."""
    payload: dict[str, object] = {
        "message": exc.message,
        "code": exc.code,
    }
    if exc.details:
        payload["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Converte erros de validacao do FastAPI para o contrato de erro do projeto."""
    details = [
        {
            "field": ".".join(str(item) for item in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "Validation failed",
            "code": "validation_error",
            "details": details,
        },
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Esconde erros inesperados atras de uma resposta 500 estavel."""
    settings = getattr(request.app.state, "settings", None)
    details = []
    if settings is not None and settings.environment != "production":
        details = [{"field": "internal", "message": str(exc)}]

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "code": "internal_server_error",
            "details": details,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os handlers globais de excecao usados pela API."""
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
