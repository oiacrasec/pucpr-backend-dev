# Documentacao para migracao para FastAPI

Este diretorio concentra a analise do backend Kotlin atual e os insumos para a futura comparacao com a implementacao em FastAPI.

Arquivos:

- `current-architecture.md`: arquitetura do projeto atual, camadas, modulos e design patterns identificados.
- `fastapi-comparison-objectives.md`: objetivos da comparacao futura entre Spring/Kotlin e FastAPI.
- `current-system-analysis.md`: analise funcional e tecnica do backend atual.
- `current-api-contract.md`: contrato HTTP atual, incluindo payloads, respostas, autenticacao e status codes.
- `fastapi-migration-guide.md`: guia de migracao tecnica para a futura implementacao em FastAPI.
- `fastapi-target-architecture.md`: arquitetura alvo recomendada para a implementacao em FastAPI, mantendo monolito modular e preparando futura extracao para microsservicos.

Escopo da analise:

- codigo-fonte em `src/main/kotlin/br/pucpr/authserver`
- configuracao em `src/main/resources/application.yaml`
- dependencias em `build.gradle.kts`
- testes existentes em `src/test/kotlin/br/pucpr/authserver`

Observacoes:

- a analise foi feita por inspecao estatica do codigo
- o projeto praticamente nao possui testes automatizados alem do carregamento do contexto
- os documentos de comparacao futura definem criterios e objetivos; a avaliacao final dependera da implementacao FastAPI
