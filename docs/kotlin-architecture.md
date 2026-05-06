# Arquitetura do projeto atual

## 1. Classificacao geral

O projeto atual e um backend monolitico em Kotlin com Spring Boot.

Classificacao arquitetural:

- monolito backend
- arquitetura em camadas
- API REST stateless
- autenticacao baseada em JWT
- organizacao modular por feature

Em termos praticos, ele segue o estilo tradicional do ecossistema Spring:

- camada web com controllers
- camada de negocio com services
- camada de persistencia com repositories
- entidades JPA para modelagem e armazenamento
- seguranca tratada como concern transversal

## 2. Estrutura em camadas

### 2.1 Camada web

Responsabilidade:

- expor endpoints HTTP
- receber requests
- validar payloads com `@Valid`
- delegar regras para services
- traduzir resultados para responses

Arquivos principais:

- `src/main/kotlin/br/pucpr/authserver/users/UserController.kt`
- `src/main/kotlin/br/pucpr/authserver/roles/RoleController.kt`

## 2.2 Camada de negocio

Responsabilidade:

- aplicar regras de negocio
- validar regras que vao alem do schema HTTP
- orquestrar repositories
- controlar regras de login, atribuicao de roles, delete e update

Arquivos principais:

- `src/main/kotlin/br/pucpr/authserver/users/UserService.kt`
- `src/main/kotlin/br/pucpr/authserver/roles/RoleService.kt`

Observacao:

- a maior parte da inteligencia do sistema esta aqui, nao nas entidades

## 2.3 Camada de persistencia

Responsabilidade:

- acesso ao banco via Spring Data JPA
- consultas por id, email e role
- persistencia de `User` e `Role`

Arquivos principais:

- `src/main/kotlin/br/pucpr/authserver/users/UserRepository.kt`
- `src/main/kotlin/br/pucpr/authserver/roles/RoleRepository.kt`

## 2.4 Modelo de dominio/persistencia

Responsabilidade:

- representar os dados persistidos
- declarar relacionamentos JPA

Arquivos principais:

- `src/main/kotlin/br/pucpr/authserver/users/User.kt`
- `src/main/kotlin/br/pucpr/authserver/roles/Role.kt`

Observacao:

- o dominio e anemico
- as entidades possuem pouca regra propria
- isso reforca que o projeto segue mais um estilo CRUD/service-oriented do que DDD

## 2.5 Seguranca

Responsabilidade:

- extrair e validar JWT
- montar autenticacao no contexto Spring Security
- proteger rotas por regra global e por method security

Arquivos principais:

- `src/main/kotlin/br/pucpr/authserver/security/SecurityConfig.kt`
- `src/main/kotlin/br/pucpr/authserver/security/JwtTokenFilter.kt`
- `src/main/kotlin/br/pucpr/authserver/security/JWT.kt`
- `src/main/kotlin/br/pucpr/authserver/security/UserToken.kt`

## 2.6 Bootstrap e inicializacao

Responsabilidade:

- garantir dados iniciais na subida da aplicacao
- criar roles padrao e um admin inicial, se necessario

Arquivo principal:

- `src/main/kotlin/br/pucpr/authserver/Bootstrapper.kt`

## 2.7 Configuracao transversal

Responsabilidade:

- definir datasource
- definir contexto `/api`
- definir H2 console
- controlar nivel de exposicao de erros
- configurar logs

Arquivo principal:

- `src/main/resources/application.yaml`

## 3. Organizacao modular

O projeto esta organizado por feature e nao por camada global.

Modulos/pacotes observados:

- `users`
- `roles`
- `security`
- `exceptions`

Ponto positivo:

- essa divisao facilita localizar a implementacao de cada recurso

Ponto negativo:

- como o sistema e pequeno, parte das responsabilidades transversais ainda fica espalhada entre anotacoes, services e configuracao Spring

## 4. Design patterns identificados

Patterns claramente usados:

- Layered Architecture
- MVC backend/web
- Repository Pattern
- Service Layer Pattern
- DTO Pattern
- Dependency Injection / IoC
- Filter Pattern
- Observer/Event Listener
- Bootstrap/Seed Pattern
- Exception Mapping Pattern
- Guard/Policy checks para autorizacao

### 4.1 Layered Architecture

Fluxo predominante:

- controller -> service -> repository -> banco

Esse e o desenho central do sistema.

### 4.2 MVC backend/web

Mesmo sem view server-side, a aplicacao usa o modelo classico do Spring MVC para:

- roteamento
- binding de request
- validacao
- serializacao HTTP

### 4.3 Repository Pattern

Os repositories encapsulam acesso a dados usando Spring Data JPA.

Exemplos:

- `findByEmail`
- `findByRole`
- `findByName`

### 4.4 Service Layer Pattern

Os services concentram as regras de negocio, como:

- impedir usuario duplicado
- impedir role duplicada
- impedir exclusao do ultimo admin
- controlar login
- controlar `PATCH /users/{id}`

### 4.5 DTO Pattern

O projeto separa entidades do contrato HTTP usando DTOs de request e response.

Exemplos:

- `CreateUserRequest`
- `UpdateUserRequest`
- `LoginRequest`
- `UserResponse`
- `RoleResponse`

### 4.6 Dependency Injection / IoC

O Spring instancia controllers, services, repositories e componentes de seguranca por injecao de dependencia.

Isso aparece de forma consistente em construtores como:

- `UserController(val service: UserService)`
- `UserService(val repository: UserRepository, ...)`

### 4.7 Filter Pattern

`JwtTokenFilter` intercepta a request e tenta montar autenticacao a partir do header `Authorization`.

### 4.8 Observer/Event Listener

`Bootstrapper` implementa `ApplicationListener<ContextRefreshedEvent>`, reagindo ao startup para semear dados.

### 4.9 Exception Mapping Pattern

Excecoes customizadas anotadas com `@ResponseStatus` mapeiam regras de negocio para status HTTP.

Exemplos:

- `BadRequestException`
- `NotFoundException`
- `UnauthorizedException`
- `ForbiddenException`

### 4.10 Guard/Policy checks

A autorizacao e aplicada por:

- regras globais em `SecurityConfig`
- `@PreAuthorize` em metodos
- checagem manual no `PATCH /users/{id}`

## 5. Estilo de dominio

O projeto nao usa DDD rico.

Caracteristicas observadas:

- entidades com pouca logica interna
- regras centralizadas em services
- foco em CRUD com regras pontuais
- forte acoplamento a Spring e JPA

Isso caracteriza um dominio mais anemico e procedural, o que e comum em backends pequenos e academicos.

## 6. Caracteristicas tecnicas importantes da arquitetura atual

### 6.1 Persistencia

- JPA/Hibernate
- H2 em memoria
- relacao muitos-para-muitos entre `User` e `Role`

### 6.2 Seguranca

- JWT HMAC
- secret hardcoded
- expira em 1h para admin e 48h para nao-admin
- mistura autorizacao por request e por metodo

### 6.3 Configuracao

- contexto global `/api`
- CORS totalmente aberto
- detalhes de erro amplamente expostos

### 6.4 Testes

- praticamente inexistentes
- apenas `contextLoads()`

## 7. Pontos fortes da arquitetura atual

- simples de entender para quem conhece Spring
- boa separacao entre web, negocio e persistencia
- organizacao por feature razoavel
- regras de negocio localizadas em poucos arquivos
- bootstrap inicial acelera o uso em desenvolvimento

## 8. Pontos fracos da arquitetura atual

- stack pesada para um dominio pequeno
- dominio anemico
- acoplamento alto a Spring Security e JPA
- falta de centralizacao formal de tratamento de erros
- ambiguidades de autorizacao por combinacao de regras globais e locais
- inexistencia de cobertura de comportamento

## 9. Conclusao

O projeto usa uma arquitetura em camadas, tipica de Spring Boot, com controllers, services, repositories e entidades JPA.

Ele nao segue Clean Architecture nem Hexagonal. O desenho e pragmatico e suficiente para o tamanho atual, mas carrega mais infraestrutura do que o dominio realmente exige.

Essa leitura e importante para a migracao:

- o melhor caminho inicial para FastAPI e preservar a ideia de camadas e modulos
- a migracao nao precisa copiar a complexidade acidental da stack atual
