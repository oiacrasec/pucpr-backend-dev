# Analise do sistema atual

## 1. Visao geral

O projeto atual é um backend Spring Boot em Kotlin voltado para autenticacao e autorizacao simples com usuarios, papeis e JWT.

Stack principal:

- Kotlin `2.2.21`
- Spring Boot `4.0.5`
- Spring Web MVC
- Spring Data JPA
- Spring Security
- JJWT `0.13.0`
- H2 em memoria
- Springdoc OpenAPI

Fonte: `build.gradle.kts`

## 2. Estrutura do projeto

Pacotes relevantes:

- `br.pucpr.authserver`
  - `AuthserverApplication.kt`: bootstrap Spring.
  - `Bootstrapper.kt`: seed de roles e usuario admin.
- `br.pucpr.authserver.roles`
  - entidade `Role`
  - controller, service, repository, DTOs
- `br.pucpr.authserver.users`
  - entidade `User`
  - controller, service, repository, DTOs
- `br.pucpr.authserver.security`
  - configuracao HTTP/security
  - filtro JWT
  - criacao e leitura de token
  - payload `UserToken`
- `br.pucpr.authserver.exceptions`
  - excecoes HTTP

Observacao:

- Os arquivos `ForbiddenException.kt`, `NotFoundException.kt` e `UnauthorizedException.kt` estao fisicamente em `exceptions/`, mas o `package` declarado neles e `br.pucpr.authserver.exception` no singular. O codigo compila porque os imports acompanham esse package, mas isso deve ser limpo na migracao.

## 3. Configuracao de runtime

Arquivo: `src/main/resources/application.yaml`

Comportamento atual:

- `server.servlet.context-path: /api`
  - todos os endpoints ficam sob `/api`
- H2 em memoria:
  - URL: `jdbc:h2:mem:db`
  - usuario: `sa`
  - senha: `sa`
- `spring.jpa.show-sql: true`
- H2 console habilitado em `/h2-console`
- resposta de erro com muita exposicao:
  - `include-message: always`
  - `include-binding-errors: always`
  - `include-stacktrace: always`
  - `include-exception: true`
- `springdoc.swagger-ui.use-root-path: true`
- logs em `./logs`

Implicacoes para a migracao:

- O novo projeto FastAPI deve expor rotas sob `/api` se a compatibilidade de caminho for obrigatoria.
- O banco atual e efemero. A migracao precisa decidir se o novo projeto preserva esse comportamento apenas para desenvolvimento ou se ja nasce com banco persistente.
- O formato detalhado dos erros atuais e bastante permissivo; reproduzir isso em producao nao e recomendavel.

## 4. Dominio e persistencia

### 4.1 Role

Arquivo-fonte: `src/main/kotlin/br/pucpr/authserver/roles/Role.kt`

Campos:

- `id: Long?`
- `name: String`
  - `unique = true`
  - `nullable = false`
- `description: String`
  - `nullable = false`

Regras:

- Ao criar role, o nome e normalizado para uppercase em `RoleService.insert`.
- Existe validacao de unicidade em nivel de service antes do save.

Observacao:

- A constraint de unicidade de `name` existe no banco e tambem na camada de aplicacao.

### 4.2 User

Arquivo-fonte: `src/main/kotlin/br/pucpr/authserver/users/User.kt`

Campos:

- `id: Long?`
- `email: String`
  - `nullable = false`
  - sem `unique` no banco
- `password: String`
  - sem `nullable = false` explicito
- `name: String`
  - default `""`
  - sem `nullable = false` explicito
- `roles: MutableSet<Role>`
  - relacao `@ManyToMany`

Tabela:

- nome explicito: `UserTable`

Tabela de associacao:

- `UserRole`
- coluna FK usuario: `idUser`
- coluna FK role: `idRole`

Regras:

- O metodo `isAdmin()` verifica se existe algum role com nome `ADMIN`.
- Usuarios novos nao recebem role padrao.
- A unicidade de email e garantida apenas por regra de service, nao por constraint de banco.

Implicacoes para a migracao:

- Se o novo banco tiver constraint unica em `email`, isso corrige um problema real, mas muda o ponto em que o erro aparece.
- Como `password` hoje e armazenada em texto puro, qualquer migracao que passe a usar hash precisa tratar compatibilidade com usuarios ja existentes ou assumir quebra controlada.

## 5. Bootstrap inicial

Arquivo-fonte: `src/main/kotlin/br/pucpr/authserver/Bootstrapper.kt`

Na subida da aplicacao:

1. Garante a existencia das roles:
   - `ADMIN`
   - `PREMIUM`
2. Se nao existir nenhum usuario com role `ADMIN`, cria:
   - email: `admin@authserver.com`
   - password: `admin`
   - name: `Auth Server Administrator`

Observacoes criticas:

- A senha seeded do admin e `admin`, em texto puro.
- Essa senha nao atende a regex exigida para criacao publica de usuario.
- O seed consulta administradores via `userRepository.findByRole("ADMIN")`.

Implicacoes para a migracao:

- O novo projeto precisa decidir se vai preservar exatamente esse seed ou substitui-lo por seed via env/config.
- Se houver hashing de senha, o admin seed precisa nascer com hash, nao em texto puro.

## 6. Seguranca

## 6.1 Configuracao HTTP

Arquivo-fonte: `src/main/kotlin/br/pucpr/authserver/security/SecurityConfig.kt`

Comportamento:

- sessao stateless
- CORS liberado para qualquer origem, header e metodo
- CSRF desabilitado
- `frameOptions` desabilitado
- filtro JWT adicionado antes de `BasicAuthenticationFilter`

Regras globais de autorizacao:

- todo `GET` e liberado em nivel de HTTP security
- `POST /users` liberado
- `POST /users/login` liberado
- `/h2-console/**` liberado
- qualquer outra rota exige autenticacao

Observacao importante:

- Mesmo com `GET` liberado na camada HTTP, o `RoleController` tem `@PreAuthorize("hasRole('ADMIN')")`. Portanto, `GET /roles` continua efetivamente restrito a admin por method security.
- O `PATCH /users/{id}` tem `@PreAuthorize("permitAll()")`, mas isso nao o torna publico de fato, porque a regra HTTP global ainda exige autenticacao para qualquer `PATCH`. Na pratica, o endpoint requer JWT valido.

## 6.2 JWT

Arquivo-fonte: `src/main/kotlin/br/pucpr/authserver/security/JWT.kt`

Caracteristicas do token:

- issuer: `PUCPR AuthServer`
- secret hardcoded: `6d92f1d355bb43e11e8f04a9f115adabdcfb32b4`
- claim customizado: `user`
- subject: `user.id` em string
- `issuedAt`: horario UTC atual
- expiracao:
  - admin: `1` hora
  - nao-admin: `48` horas

Payload `user`:

- `id`
- `name`
- `roles`

Origem:

- `UserToken(user)` transforma os roles em `SortedSet<String>`
- o email nao e incluido no JWT

Extracao:

- o filtro le o header `Authorization`
- aceita prefixo `Bearer`
- valida assinatura e issuer
- se der qualquer erro, rejeita silenciosamente e segue sem autenticacao

Implicacoes para a migracao:

- Se a meta for compatibilidade com tokens antigos, o FastAPI deve usar o mesmo secret, issuer e claim `user`.
- Se a meta for apenas compatibilidade funcional daqui para frente, o novo projeto pode emitir JWTs equivalentes sem se preocupar com tokens gerados pelo sistema Kotlin.

## 6.3 Autorizacao por papel e identidade

Regras de negocio relevantes:

- `RoleController`: somente `ADMIN`
- `DELETE /users/{id}`: somente `ADMIN`
- `PUT /users/{id}/roles/{role}`: somente `ADMIN`
- `PATCH /users/{id}`:
  - permitido para o proprio usuario autenticado
  - permitido para admin
  - proibido para usuario comum tentando alterar outro usuario

Implementacao atual:

- o principal autenticado esperado no controller e `UserToken`
- a checagem de self-update compara `token.id` com o path param `id`

## 7. Validacoes de entrada

### 7.1 CreateUserRequest

Campos:

- `email`
  - `@Email`
- `password`
  - regex: `^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$`
- `name`
  - `@NotBlank`

Interpretacao da regex de senha:

- minimo 8 caracteres
- pelo menos uma letra
- pelo menos um digito
- pelo menos um caractere especial entre `@$!%*#?&`

### 7.2 LoginRequest

- `email`: `@NotBlank`
- `password`: `@NotBlank`

### 7.3 UpdateUserRequest

- `name`: `@NotBlank`

### 7.4 CreateRoleRequest

- `name`: `@NotBlank`
- `description`: `@NotBlank`

## 8. Repositorios e consultas

### 8.1 UserRepository

Metodos:

- `findByEmail(email)`
- `findByRole(role)`

JPQL de `findByRole`:

- join entre `User` e `roles`
- filtro por igualdade exata de `r.name`
- `distinct`
- ordenacao por `u.name`

Observacao importante:

- `findByRole(role)` nao faz uppercase. Como os nomes de role sao persistidos em uppercase, a busca efetiva depende de o cliente enviar `ADMIN`, `PREMIUM` etc.

### 8.2 RoleRepository

Metodo:

- `findByName(name)`

## 9. Excecoes e status HTTP

Excecoes customizadas:

- `BadRequestException` -> `400`
- `ForbiddenException` -> `403`
- `NotFoundException` -> `404`
- `UnauthorizedException` -> `401`

Origem tipica:

- duplicidade de role -> `400`
- usuario duplicado -> `400`
- role inexistente ao conceder -> `400`
- tentativa de apagar ultimo admin -> `400`
- usuario inexistente -> `404`
- login com usuario inexistente -> `401`
- login com senha invalida -> `401`
- patch sem permissao -> `403`

Observacao:

- Validacoes bean validation do Spring tambem geram `400`.

## 10. Cobertura de testes

Existe apenas:

- `AuthserverApplicationTests.contextLoads()`

Na pratica:

- nao ha testes de controller
- nao ha testes de service
- nao ha testes de seguranca
- nao ha testes de repositorio

Implicacao:

- O agente que migrar para FastAPI nao tera suite confiavel para verificar equivalencia funcional. A documentacao deste diretório deve ser tratada como contrato inicial.

## 11. Riscos e inconsistencias que precisam ser conhecidos

1. Senhas estao em texto puro.
2. O secret JWT esta hardcoded em codigo-fonte.
3. `email` nao tem unique constraint no banco.
4. O banco e H2 em memoria; nada persiste entre reinicios.
5. CORS esta totalmente aberto.
6. O seed do admin usa senha fraca e fora da propria politica de senha da API.
7. O pacote das excecoes esta inconsistente entre nome de pasta e `package`.
8. O sistema expoe detalhes de erro e stacktrace.
9. A busca de usuarios por role e case-sensitive na pratica.
10. `UserResponse` nao expoe roles; clientes dependem de outros caminhos para inferir autorizacao.

## 12. Regras que o proximo agente precisa preservar ou decidir conscientemente

Regras de compatibilidade forte:

- contexto `/api`
- entidades `User`, `Role` e associacao muitos-para-muitos
- bootstrap de `ADMIN` e `PREMIUM`
- login retornando `{ token, user }`
- claim JWT `user` com `id`, `name`, `roles`
- expiracao de 1h para admin e 48h para nao-admin
- `PATCH /users/{id}` com `200` quando altera e `204` quando nao ha mudanca
- `PUT /users/{id}/roles/{role}` com `200` quando adiciona e `204` quando usuario ja tem a role

Pontos a decidir conscientemente:

- manter senha em texto puro ou corrigir para hash
- manter o mesmo secret JWT ou externalizar
- manter H2 em memoria ou migrar para banco persistente
- manter resposta de erro detalhada
- adicionar unique constraint de banco em `email`
