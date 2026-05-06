# Guia de migracao para FastAPI

## 1. Objetivo da migracao

Reimplementar o backend atual em FastAPI preservando o comportamento funcional relevante e deixando explicito onde existem decisoes de compatibilidade versus melhorias de seguranca/arquitetura.

## 2. Recomendacao de stack no novo projeto

Stack sugerida:

- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PyJWT ou `python-jose`
- Uvicorn
- `passlib[bcrypt]` ou `pwdlib` se houver correcao de senha
- pytest
- httpx para testes de API

Se a meta for paridade simples e rapida:

- manter JWT HMAC com o mesmo `issuer` e claim `user`
- manter SQLite local ou Postgres, mas com schema equivalente

Se a meta for endurecimento minimo:

- externalizar secret JWT
- hashear senha
- adicionar constraint unica em `users.email`
- desligar exposicao excessiva de erro

## 3. Estrutura sugerida do projeto FastAPI

```text
app/
  main.py
  core/
    config.py
    security.py
    exceptions.py
  db/
    base.py
    session.py
    models/
      user.py
      role.py
      user_role.py
  schemas/
    user.py
    role.py
    auth.py
  repositories/
    user_repository.py
    role_repository.py
  services/
    user_service.py
    role_service.py
    auth_service.py
  api/
    deps.py
    routers/
      users.py
      roles.py
  bootstrap/
    seed.py
tests/
```

## 4. Mapeamento Spring -> FastAPI

| Spring/Kotlin | Papel atual | Equivalente sugerido em FastAPI |
| --- | --- | --- |
| `@RestController` | endpoints HTTP | `APIRouter` |
| `Service` | regras de negocio | modulo/classe service |
| `JpaRepository` | persistencia | repository com SQLAlchemy |
| entidades JPA | modelo ORM | modelos SQLAlchemy |
| DTO request/response | contrato HTTP | schemas Pydantic |
| `SecurityFilterChain` | auth global | middleware/dependency-based auth |
| `JwtTokenFilter` | extracao do token | dependency `get_current_user` |
| `Bootstrapper` | seed inicial | startup hook ou comando de seed |
| `@ResponseStatus` | mapeamento de erro | `HTTPException` ou exceptions customizadas com handlers |

## 5. Modelagem de banco sugerida

### 5.1 Tabela `roles`

Campos:

- `id` bigint/integer PK
- `name` string unique not null
- `description` string not null

### 5.2 Tabela `users`

Campos:

- `id` bigint/integer PK
- `email` string not null
- `password` string not null
- `name` string not null

Compatibilidade:

- para reproduzir o estado atual, `email` pode ficar sem unique constraint no banco, mas o service deve continuar impedindo duplicidade

Recomendacao:

- adicionar unique constraint em `email`

### 5.3 Tabela de associacao `user_role`

Campos:

- `id_user` FK -> `users.id`
- `id_role` FK -> `roles.id`

Recomendacao:

- usar chave primaria composta ou unique composto em `(id_user, id_role)`

## 6. Schemas Pydantic necessarios

### Request

- `CreateRoleRequest`
  - `name: str`
  - `description: str`
- `CreateUserRequest`
  - `email: EmailStr`
  - `password: str` com regex atual
  - `name: str`
- `LoginRequest`
  - `email: str`
  - `password: str`
- `UpdateUserRequest`
  - `name: str`

### Response

- `RoleResponse`
  - `name: str`
  - `description: str`
- `UserResponse`
  - `id: int`
  - `email: str`
  - `name: str`
- `LoginResponse`
  - `token: str`
  - `user: UserResponse`
- `UserToken`
  - `id: int`
  - `name: str`
  - `roles: list[str]`

Regex atual da senha:

```python
r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
```

## 7. Regras de negocio que precisam ser implementadas

### 7.1 Users

- criar usuario apenas se o email ainda nao existir
- listar usuarios por `name` asc/desc
- listar usuarios por role quando query param `role` for informado
- `role` no filtro atual e case-sensitive na pratica
- buscar usuario por id ou retornar `404`
- login com comparacao direta de senha
- atualizar apenas o `name`
- retornar `204` no patch se o nome nao mudar
- impedir exclusao do ultimo admin
- adicionar role ao usuario com uppercase do nome informado
- retornar `204` quando a role ja estiver presente

### 7.2 Roles

- criar role com `name.upper()`
- impedir duplicidade
- listar roles ordenadas por nome ascendente

### 7.3 Bootstrap

- garantir roles `ADMIN` e `PREMIUM`
- se nao houver admins, criar admin padrao

## 8. Regras de autenticacao/autorizacao em FastAPI

### 8.1 JWT de compatibilidade

Se a migracao precisar aceitar ou produzir tokens equivalentes:

- algoritmo HMAC SHA-256
- mesmo `issuer`: `PUCPR AuthServer`
- mesmo secret atual, ou um valor configuravel com esse default apenas para desenvolvimento
- mesmo claim `user`
- `sub` com id em string
- `roles` ordenadas
- expiracao:
  - admin: 1 hora
  - demais: 48 horas

### 8.2 Dependencias de seguranca

Criar dependencias como:

- `get_optional_current_user()`
- `get_current_user()`
- `require_admin()`
- `require_self_or_admin(user_id: int)`

Mapeamento sugerido por rota:

- `GET /users`: publica
- `POST /users`: publica
- `POST /users/login`: publica
- `GET /users/{id}`: publica
- `PATCH /users/{id}`: `get_current_user` + `require_self_or_admin`
- `DELETE /users/{id}`: `require_admin`
- `PUT /users/{id}/roles/{role}`: `require_admin`
- `GET /roles`: `require_admin`
- `POST /roles`: `require_admin`

## 9. Decisao importante: paridade vs correcao

O proximo agente precisa escolher explicitamente um dos modos abaixo.

### Modo A: paridade funcional

Objetivo:

- reproduzir o comportamento atual com minima quebra

Implica:

- manter senha em texto puro por enquanto
- manter secret compativel
- manter status codes atuais
- manter bootstrap com admin `admin@authserver.com` / `admin`
- manter `GET /users` e `GET /users/{id}` publicos

Risco:

- carrega fragilidades de seguranca para o novo projeto

### Modo B: migracao com endurecimento minimo

Objetivo:

- corrigir o basico sem descaracterizar o contrato

Implica:

- hashear senha
- mover secret JWT para configuracao
- adicionar unique constraint em `email`
- reduzir detalhes de erro em producao
- talvez manter responses iguais, mas mudar implementacao interna

Risco:

- exige estrategia de compatibilidade para usuarios/token existentes

## 10. Sequencia sugerida de implementacao

1. Criar modelos ORM `User`, `Role` e tabela associativa.
2. Criar schemas Pydantic espelhando os DTOs Kotlin.
3. Implementar repositories com consultas equivalentes a `findByEmail`, `findByRole`, `findByName`.
4. Implementar servicos de role e user com as mesmas regras de negocio.
5. Implementar JWT com o claim `user`.
6. Implementar dependencies de autenticacao e autorizacao.
7. Criar routers `/users` e `/roles` sob prefixo `/api`.
8. Implementar seed inicial no startup ou em comando dedicado.
9. Criar testes de API cobrindo todos os status codes relevantes.
10. Validar o contrato com esta documentacao antes de expandir o dominio.

## 11. Testes minimos que o novo projeto precisa ter

Como o projeto atual nao possui suite util, o novo projeto deveria nascer com pelo menos:

- criacao de usuario com payload valido
- rejeicao de senha invalida
- login bem-sucedido
- login com senha invalida
- patch do proprio usuario
- patch de terceiro por usuario comum -> `403`
- patch sem mudanca -> `204`
- grant de role por admin
- grant repetido -> `204`
- delete de admin unico -> `400`
- listagem publica de usuarios
- acesso de nao-admin em `/roles` -> falha

## 12. Ambiguidades que o proximo agente nao deve ignorar

1. `DELETE /users/{id}` hoje devolve sucesso sem payload; manter `200` ou trocar para `204` e uma decisao de contrato.
2. `GET /roles` parece publico pela regra global de GET, mas nao e por causa do `@PreAuthorize`.
3. `PATCH /users/{id}` parece publico pelo `permitAll()`, mas nao e porque a camada HTTP exige autenticacao.
4. A senha do admin seed nao segue a propria regex da API.
5. `findByRole` exige nome de role exatamente como salvo.

## 13. Entrega esperada do agente de migracao

O proximo agente deve entregar:

- projeto FastAPI funcional
- rotas equivalentes sob `/api`
- seed inicial documentado
- testes cobrindo o contrato atual
- decisao explicita entre paridade e endurecimento minimo
