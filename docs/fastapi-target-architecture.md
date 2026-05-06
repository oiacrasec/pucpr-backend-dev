# Arquitetura alvo para a implementacao em FastAPI

## 1. Objetivo deste documento

Este documento define a arquitetura recomendada para a nova implementacao em FastAPI.

A meta e:

- manter o sistema simples agora
- continuar monolitico
- evitar complexidade acidental
- preparar fronteiras internas para futura extracao em microsservicos

Este documento deve ser usado como guia de execucao por outro agente.

## 2. Decisao arquitetural

A recomendacao e construir um **modular monolith** em FastAPI.

Em termos praticos:

- um unico deploy
- um unico processo de aplicacao
- um unico banco de dados
- um unico repositorio
- modulos internos com fronteiras claras

O sistema atual e pequeno. Separar em microsservicos agora introduziria custo operacional, duplicacao de configuracao, mais pontos de falha e mais complexidade de teste sem ganho real para o dominio atual.

## 3. Fronteira de dominio recomendada

Nao separar `users`, `roles` e `auth` como dominios independentes.

Para este projeto, a fronteira correta hoje e um unico modulo:

- `identity_access_management`

Justificativa:

- autenticacao, usuarios e papeis pertencem ao mesmo contexto de negocio
- a regra de acesso depende diretamente de `User`, `Role` e JWT
- separar esses itens cedo demais criaria fronteiras artificiais

Portanto, a recomendacao e ter um monolito modular com o modulo `identity_access_management` bem isolado internamente.

## 4. Principios de projeto

O agente que implementar deve seguir estes principios:

1. Simplicidade primeiro.
2. Fronteiras internas claras por modulo.
3. Camadas leves, sem excesso de abstracao.
4. Controllers e routers finos.
5. Regras de negocio centralizadas em services.
6. Persistencia isolada em repositories.
7. Configuracao por ambiente, sem segredos hardcoded.
8. Preparar o modulo `identity_access_management` para futura extracao, sem implementar infraestrutura de microsservicos agora.

## 5. Estrutura de pastas recomendada

```text
app/
  main.py

  core/
    config.py
    security.py
    exceptions.py
    logging.py
    dependencies.py

  db/
    base.py
    session.py
    migrations/

  modules/
    identity_access_management/
      api/
        auth_router.py
        users_router.py
        roles_router.py
      schemas/
        auth.py
        user.py
        role.py
      models/
        user.py
        role.py
      repositories/
        user_repository.py
        role_repository.py
      services/
        auth_service.py
        user_service.py
        role_service.py
      policies/
        access.py
      bootstrap/
        seed.py

tests/
  integration/
  unit/
```

## 6. Responsabilidade de cada area

### 6.1 `app/main.py`

Responsavel por:

- criar a aplicacao FastAPI
- registrar routers
- configurar startup
- conectar middlewares e handlers globais

Nao deve conter regra de negocio.

### 6.2 `app/core/`

Responsavel por infraestrutura transversal.

Arquivos esperados:

- `config.py`: configuracao por env vars com `BaseSettings`
- `security.py`: criacao e validacao de JWT
- `exceptions.py`: excecoes da aplicacao e handlers globais
- `logging.py`: configuracao de logging
- `dependencies.py`: dependencias compartilhadas, como sessao de banco

Regra:

- `core` pode ser usado pelos modulos
- `core` nao deve importar o modulo `identity_access_management` para evitar acoplamento invertido

### 6.3 `app/db/`

Responsavel por:

- engine
- session factory
- base declarativa
- migrations com Alembic

Regra:

- manter a configuracao de banco isolada aqui
- modelos ORM podem herdar da base definida nesta camada

### 6.4 `app/modules/identity_access_management/api/`

Responsavel por:

- definir rotas
- receber request schemas
- aplicar `Depends`
- retornar response schemas e status codes corretos

Regras:

- router nao acessa ORM diretamente
- router nao implementa regra de negocio
- router delega para service

### 6.5 `app/modules/identity_access_management/schemas/`

Responsavel por:

- contratos HTTP de entrada e saida
- validacao Pydantic

Separar schemas por tema:

- `auth.py`
- `user.py`
- `role.py`

Regra:

- schemas HTTP nao devem ser usados como modelos de persistencia

### 6.6 `app/modules/identity_access_management/models/`

Responsavel por:

- modelos ORM `User` e `Role`
- relacionamento muitos-para-muitos

Regra:

- o modelo deve representar persistencia
- evitar colocar regra de negocio complexa aqui

### 6.7 `app/modules/identity_access_management/repositories/`

Responsavel por:

- queries
- busca por id, email, role
- save, delete e operacoes de persistencia

Regra:

- repository nao decide autorizacao
- repository nao conhece HTTP

### 6.8 `app/modules/identity_access_management/services/`

Responsavel por:

- regras de negocio reais do sistema
- duplicidade de usuario
- login
- atualizacao de nome
- protecao de ultimo admin
- atribuicao de role

Esta e a camada mais importante da aplicacao.

### 6.9 `app/modules/identity_access_management/policies/`

Responsavel por regras de acesso reutilizaveis, por exemplo:

- `get_current_user`
- `get_optional_current_user`
- `require_admin`
- `require_self_or_admin`

Observacao:

- essas policies podem usar utilitarios de `core/security.py`
- manter essa logica separada dos routers ajuda a futura extracao

### 6.10 `app/modules/identity_access_management/bootstrap/`

Responsavel por:

- seed inicial de roles
- seed do admin padrao, se a regra de compatibilidade exigir

## 7. Fluxo de dependencias permitido

Fluxo recomendado:

```text
api -> services -> repositories -> db/models
api -> policies -> core/security
services -> repositories
services -> core
repositories -> db/models
```

Fluxos que devem ser evitados:

- `api` acessando `models` diretamente
- `repositories` importando `schemas`
- `services` retornando `Response` do FastAPI
- `core` dependendo do modulo `identity_access_management`

## 8. Decisoes tecnicas recomendadas

### 8.1 Estilo de execucao

Usar stack sincronica:

- FastAPI
- SQLAlchemy 2.x sync
- Uvicorn

Justificativa:

- o dominio e pequeno
- o projeto nao mostra necessidade clara de `async`
- `async` aqui aumentaria a superficie de complexidade

### 8.2 Banco de dados

Recomendacao:

- PostgreSQL como banco principal
- SQLite pode ser aceito apenas para testes locais simples, se necessario

Justificativa:

- se a meta e evoluir com seriedade, o banco principal deve ser o mesmo tipo usado em ambiente real

### 8.3 Migracoes

Usar Alembic desde o inicio.

Nao depender apenas de criacao automatica de schema em runtime.

### 8.4 Configuracao

Toda configuracao deve vir de ambiente:

- URL do banco
- JWT secret
- JWT issuer
- flags de debug
- configuracao de CORS

Nao hardcode secret em codigo.

### 8.5 Testes

Criar testes desde o inicio em:

- `tests/unit`
- `tests/integration`

O contrato atual documentado em `docs/current-api-contract.md` deve orientar os testes de integracao.

## 9. Seguranca e autorizacao

O desenho recomendado e dependency-based.

Implementar dependencias como:

- `get_optional_current_user()`
- `get_current_user()`
- `require_admin()`
- `require_self_or_admin(user_id)`

Recomendacao de uso por rota:

- `GET /users`: publica
- `POST /users`: publica
- `POST /users/login`: publica
- `GET /users/{id}`: publica
- `PATCH /users/{id}`: autenticada, self ou admin
- `DELETE /users/{id}`: admin
- `PUT /users/{id}/roles/{role}`: admin
- `GET /roles`: admin
- `POST /roles`: admin

## 10. Como preparar a futura extracao para microsservico

O objetivo nao e implementar microsservicos agora.

O objetivo e deixar o modulo `identity_access_management` extraivel com baixo atrito depois.

Para isso:

1. Concentrar tudo de identidade e acesso em `modules/identity_access_management/`.
2. Evitar imports espalhados do modulo para fora sem necessidade.
3. Evitar que outros modulos futuros acessem tabelas de `identity_access_management` diretamente sem passar por services ou interfaces claras.
4. Manter contratos de entrada e saida bem definidos.
5. Isolar side effects externos atras de adaptadores, quando eles surgirem.

Sinais reais de que `identity_access_management` pode virar microsservico no futuro:

- outros dominios independentes surgirem no monolito
- escala de deploy de identidade divergir do restante
- politicas de autenticacao e autorizacao crescerem em complexidade
- necessidade de ownership por times separados

Enquanto esses sinais nao existirem, manter monolito.

## 11. O que evitar agora

O agente nao deve introduzir:

- CQRS
- event bus interno
- arquitetura hexagonal completa
- repository generico
- abstracoes prematuras
- multiplos bancos
- comunicacao assincrona entre modulos
- `async` sem necessidade objetiva

Esses itens podem parecer preparacao para o futuro, mas no contexto atual so adicionam custo.

## 12. Sequencia sugerida de implementacao

O agente que executar esta arquitetura deve seguir a sequencia abaixo:

1. Criar o esqueleto de pastas de `app/` conforme este documento.
2. Implementar `core/config.py`, `db/session.py` e `db/base.py`.
3. Implementar modelos ORM de `User` e `Role`.
4. Criar schemas Pydantic equivalentes ao contrato atual.
5. Implementar repositories do modulo `identity_access_management`.
6. Implementar services de `auth`, `user` e `role`.
7. Implementar JWT e dependencias de seguranca.
8. Implementar routers sob prefixo `/api`.
9. Implementar seed inicial.
10. Criar testes de integracao cobrindo o contrato atual.

## 13. Decisoes de implementacao que o agente deve manter explicitas

Ao implementar, o agente deve registrar claramente:

- se o modo escolhido e paridade funcional ou endurecimento minimo
- se a senha sera mantida em texto puro temporariamente ou se havera hash
- se o secret JWT sera compativel com o legado ou totalmente novo
- se `email` tera unique constraint no banco
- se `DELETE /users/{id}` permanecera `200` ou mudara para `204`

Essas decisoes nao devem ficar implicitas no codigo.

## 14. Resumo executivo

A recomendacao final e:

- **um monolito modular**
- **um unico modulo de negocio chamado `identity_access_management`**
- **camadas leves: api, service, repository, model, schema**
- **stack sincronica**
- **PostgreSQL + Alembic**
- **JWT e configuracao centralizados em `core/`**
- **estrutura interna pensada para futura extracao, mas sem complexidade prematura**

Se o agente seguir este documento, o projeto ficara simples para o estado atual e com uma trilha realista de evolucao futura.
