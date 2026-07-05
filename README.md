# PUCPR Backend FastAPI

Migração da funcionalidade de Avatar para FastAPI do trabalho final da disciplina de Serviços Mobile em Cloud AWS - PUCPR.

> Branch: 05-entrega-final

## Integrantes

- Caio César Lima Borges
- Myrelle Silva Lopes

## Link apresentação

- https://youtu.be/P5JAaD3lFAM

## + DOCUMENTAÇÃO
 O arquivo `1 - Funcionalidade avatar.md` contém documentado um passo a passo de criação/config/testes.

## Decisoes principais

- arquitetura: monolito modular
- modulo de negocio: `identity_access_management`
- persistencia: PostgreSQL (`pucbr_backend`, schema `public`)
- seguranca: JWT HMAC com secret externalizado
- senha: hash PBKDF2 com fallback de verificacao para texto puro legado
- contrato preservado nas rotas e nos status codes relevantes do sistema anterior

## Estrutura

```text
app/
  core/
  db/
  modules/
    identity_access_management/
alembic/
tests/
```

## Requisitos

- Python 3.14+
- PostgreSQL acessivel localmente

## Configuracao

1. Crie o banco `pucbr_backend` no PostgreSQL.
2. Use o schema `public`.
3. Copie `.env.example` para `.env` e ajuste credenciais e secret.

Exemplo de URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:sua-senha@localhost:5432/pucbr_backend
```

## Instalacao

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .[dev]
```

## Migracoes

Aplicar a migration inicial:

```powershell
python -m alembic upgrade head
```

## Executar a API

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interface principal:

- Swagger UI na raiz: `http://127.0.0.1:8000/`
- healthcheck: `http://127.0.0.1:8000/health`

## Testes

```powershell
python -m pytest
```

## Endpoints principais

- `POST /api/users`
- `GET /api/users`
- `GET /api/users/{id}`
- `PATCH /api/users/{id}`
- `DELETE /api/users/{id}`
- `PUT /api/users/{id}/roles/{role_name}`
- `POST /api/users/login`
- `GET /api/roles`
- `POST /api/roles`
