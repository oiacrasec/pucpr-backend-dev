# Decisoes de implementacao FastAPI

## Modo escolhido

Foi adotado **endurecimento minimo com preservacao de contrato HTTP**.

## O que foi preservado

- prefixo `/api`
- rotas e semantica principal de `users`, `roles` e `login`
- claim JWT `user`
- `issuer` JWT `PUCPR AuthServer`
- expiracao de `1h` para admin e `24h` para nao-admin
- `PATCH /users/{id}` retornando `204` quando nao ha mudanca
- `PUT /users/{id}/roles/{role}` retornando `204` quando a role ja existe
- `DELETE /users/{id}` retornando `200` sem payload
- filtro por role case-sensitive na pratica
- seed das roles `ADMIN` e `PREMIUM`
- seed do admin padrao com email `admin@admin.com`

## O que foi corrigido

- senha agora e armazenada com hash PBKDF2
- `email` passou a ter unicidade no banco
- secret JWT foi externalizado para configuracao
- erros internos deixaram de expor detalhes em producao
- o projeto nasceu com testes de unidade e integracao
- o banco alvo passou a ser PostgreSQL com migration versionada em Alembic

## Compatibilidade com legado

- a verificacao de senha possui fallback para texto puro, o que permite migracao controlada caso dados legados sejam reaproveitados
- o payload do login continua retornando `{ token, user }`
- o JWT emitido continua carregando `sub`, `iss` e o claim `user` com `id`, `name` e `roles`

## Observacoes

- o admin seed continua com senha `admin` por compatibilidade, mas agora o valor e hasheado no banco
- o schema alvo e `public`
- a aplicacao pode criar schema automaticamente em desenvolvimento/teste; em ambiente serio, o caminho recomendado e `alembic upgrade head`
