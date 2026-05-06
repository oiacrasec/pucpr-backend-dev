# Contrato HTTP atual

Base path global: `/api`

## Convencoes gerais

- Corpo JSON em requests e responses.
- Autenticacao via header `Authorization: Bearer <jwt>`.
- Para endpoints protegidos, o token precisa carregar o claim `user`.
- Respostas de erro usam os status HTTP definidos pelas excecoes ou pela validacao do Spring.

## 1. Roles

### POST `/api/roles`

Autenticacao:

- obrigatoria
- requer role `ADMIN`

Request body:

```json
{
  "name": "premium",
  "description": "Premium user"
}
```

Validacoes:

- `name` obrigatorio
- `description` obrigatorio

Regras:

- `name` e convertido para uppercase antes de persistir.
- se a role ja existir, retorna `400`.

Response `201 Created`:

```json
{
  "name": "PREMIUM",
  "description": "Premium user"
}
```

Erros esperados:

- `400` role duplicada
- `403` sem permissao
- `401/403` sem token valido, dependendo de como a stack trata a falta de autenticacao

### GET `/api/roles`

Autenticacao:

- efetivamente obrigatoria
- requer role `ADMIN`

Observacao:

- O HTTP security libera `GET`, mas o controller esta protegido com `@PreAuthorize("hasRole('ADMIN')")`.

Response `200 OK`:

```json
[
  {
    "name": "ADMIN",
    "description": "System Administrator"
  },
  {
    "name": "PREMIUM",
    "description": "Premium user"
  }
]
```

Ordenacao:

- por `name`, ascendente

## 2. Users

### GET `/api/users`

Autenticacao:

- nao obrigatoria

Query params:

- `sortDir`: `ASC` ou `DESC`, opcional, default `ASC`
- `role`: opcional

Regras:

- se `role` for informado, a busca por role e usada e `sortDir` e ignorado
- se `role` nao for informado, a listagem ordena por `name`
- `sortDir` invalido retorna `400`
- a busca por role e case-sensitive na pratica

Exemplo:

- `/api/users`
- `/api/users?sortDir=DESC`
- `/api/users?role=ADMIN`

Response `200 OK`:

```json
[
  {
    "id": 1,
    "email": "admin@authserver.com",
    "name": "Auth Server Administrator"
  }
]
```

Observacao:

- roles nao aparecem no payload de usuario.

### POST `/api/users`

Autenticacao:

- nao obrigatoria

Request body:

```json
{
  "email": "user@example.com",
  "password": "Abcdef1!",
  "name": "User Example"
}
```

Validacoes:

- `email` deve ter formato valido
- `password` deve obedecer a regex de complexidade
- `name` obrigatorio

Regras:

- se ja existir usuario com o mesmo email, retorna `400`
- usuario nasce sem roles

Response `201 Created`:

```json
{
  "id": 2,
  "email": "user@example.com",
  "name": "User Example"
}
```

Erros esperados:

- `400` usuario duplicado
- `400` payload invalido

### POST `/api/users/login`

Autenticacao:

- nao obrigatoria

Request body:

```json
{
  "email": "admin@authserver.com",
  "password": "admin"
}
```

Regras:

- se o email nao existir, retorna `401`
- se a senha nao coincidir exatamente, retorna `401`
- nao ha hashing de senha

Response `200 OK`:

```json
{
  "token": "<jwt>",
  "user": {
    "id": 1,
    "email": "admin@authserver.com",
    "name": "Auth Server Administrator"
  }
}
```

JWT emitido:

- `iss`: `PUCPR AuthServer`
- `sub`: id do usuario em string
- claim `user`:

```json
{
  "id": 1,
  "name": "Auth Server Administrator",
  "roles": ["ADMIN"]
}
```

- expiracao:
  - `1h` se o usuario tiver role `ADMIN`
  - `48h` caso contrario

### GET `/api/users/{id}`

Autenticacao:

- nao obrigatoria

Response `200 OK`:

```json
{
  "id": 1,
  "email": "admin@authserver.com",
  "name": "Auth Server Administrator"
}
```

Erros esperados:

- `404` se o usuario nao existir

### PATCH `/api/users/{id}`

Autenticacao:

- obrigatoria na pratica

Autorizacao:

- proprio usuario pode alterar o proprio nome
- admin pode alterar o nome de qualquer usuario
- usuario comum nao pode alterar outro usuario

Request body:

```json
{
  "name": "Novo Nome"
}
```

Validacoes:

- `name` obrigatorio e nao vazio

Regras:

- se o nome informado for igual ao atual, retorna `204 No Content`
- se houver alteracao, retorna `200 OK` com o usuario atualizado
- se o usuario nao existir, retorna `404`
- se o token nao corresponder ao proprio usuario e nao for admin, retorna `403`

Response `200 OK`:

```json
{
  "id": 2,
  "email": "user@example.com",
  "name": "Novo Nome"
}
```

Response `204 No Content`:

- sem corpo

Observacao:

- A anotacao `@PreAuthorize("permitAll()")` no controller nao torna o endpoint publico, porque a regra HTTP global ainda exige autenticacao para `PATCH`.

### DELETE `/api/users/{id}`

Autenticacao:

- obrigatoria
- requer role `ADMIN`

Regras:

- se o usuario nao existir, retorna `404`
- se for o ultimo admin do sistema, retorna `400`
- caso contrario, remove o usuario

Response atual:

- `200 OK` com corpo vazio

Observacao:

- O controller delega para um metodo `Unit`; o comportamento esperado na migracao e manter sucesso sem payload. Pode-se optar por `204`, mas isso mudaria o contrato.

### PUT `/api/users/{id}/roles/{role}`

Autenticacao:

- obrigatoria
- requer role `ADMIN`

Regras:

- o `role` do path e convertido para uppercase
- se o usuario nao existir, retorna `404`
- se a role nao existir, retorna `400`
- se o usuario ja possuir a role, retorna `204 No Content`
- se a role for adicionada, retorna `200 OK`

Response `200 OK`:

- sem corpo

Response `204 No Content`:

- sem corpo

## 3. Matriz resumida de acesso

| Metodo | Rota | Auth | Papel | Observacoes |
| --- | --- | --- | --- | --- |
| GET | `/api/users` | Nao | Nenhum | publico |
| POST | `/api/users` | Nao | Nenhum | publico |
| POST | `/api/users/login` | Nao | Nenhum | publico |
| GET | `/api/users/{id}` | Nao | Nenhum | publico |
| PATCH | `/api/users/{id}` | Sim | proprio usuario ou admin | atualiza apenas `name` |
| DELETE | `/api/users/{id}` | Sim | ADMIN | nao pode apagar ultimo admin |
| PUT | `/api/users/{id}/roles/{role}` | Sim | ADMIN | `200` se adiciona, `204` se ja existia |
| POST | `/api/roles` | Sim | ADMIN | nome da role vai para uppercase |
| GET | `/api/roles` | Sim | ADMIN | apesar do `GET` global estar liberado |

## 4. Payloads de DTO atuais

### CreateRoleRequest

```json
{
  "name": "ADMIN",
  "description": "System Administrator"
}
```

### RoleResponse

```json
{
  "name": "ADMIN",
  "description": "System Administrator"
}
```

### CreateUserRequest

```json
{
  "email": "user@example.com",
  "password": "Abcdef1!",
  "name": "User Example"
}
```

### LoginRequest

```json
{
  "email": "user@example.com",
  "password": "Abcdef1!"
}
```

### UpdateUserRequest

```json
{
  "name": "Novo Nome"
}
```

### UserResponse

```json
{
  "id": 2,
  "email": "user@example.com",
  "name": "User Example"
}
```

### LoginResponse

```json
{
  "token": "<jwt>",
  "user": {
    "id": 2,
    "email": "user@example.com",
    "name": "User Example"
  }
}
```
