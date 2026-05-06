# Objetivos da comparacao futura com FastAPI

## 1. Objetivo deste documento

Este documento define o que deve ser comparado entre:

- o backend atual em Spring Boot + Kotlin
- a futura implementacao em FastAPI

Ele nao faz a comparacao final ainda.

Ele registra:

- quais criterios serao avaliados
- o que deve ser observado em cada criterio
- quais perguntas precisam ser respondidas quando o projeto FastAPI estiver pronto

## 2. Resultado esperado da comparacao futura

A comparacao final deve permitir responder, com base em codigo e comportamento real:

- qual stack foi mais simples de desenvolver para este dominio
- qual stack entregou melhor equilibrio entre clareza, seguranca e manutencao
- qual stack exigiu mais infraestrutura, configuracao e codigo cerimonial
- onde o FastAPI melhorou ou piorou o projeto em relacao ao backend atual

## 3. Criterios de comparacao obrigatorios

### 3.1 Facilidade de desenvolvimento

O que comparar:

- quantidade de arquivos e camadas necessarias para expor um endpoint
- clareza do fluxo request -> validacao -> regra -> persistencia -> response
- esforco para adicionar um novo endpoint
- esforco para alterar uma regra existente
- volume de codigo cerimonial
- tempo para localizar onde uma regra esta implementada

Perguntas que a comparacao final deve responder:

- em qual stack o backend ficou mais simples de evoluir?
- onde houve mais "magia" de framework?
- em qual stack o fluxo ficou mais facil de ler por um novo desenvolvedor?

### 3.2 Framework de validacao

O que comparar:

- mecanismo de validacao usado em cada stack
- clareza das regras de validacao
- facilidade para criar validacoes simples e customizadas
- formato e consistencia dos erros de validacao
- impacto das validacoes no contrato HTTP

Pontos que devem ser analisados:

- diferenca entre Bean Validation e Pydantic
- vantagens e desvantagens de cada abordagem
- comportamento default de erro
- necessidade de customizacao para manter compatibilidade de contrato

Perguntas que a comparacao final deve responder:

- qual abordagem ficou mais expressiva?
- qual ficou mais simples de testar?
- o FastAPI preservou ou alterou o comportamento atual de validacao?

### 3.3 Seguranca

O que comparar:

- integracao com JWT
- mecanismo para proteger rotas
- clareza do fluxo de autenticacao e autorizacao
- facilidade para implementar regras como `admin` e `self or admin`
- risco de inconsistencias entre regras globais e locais

Pontos que devem ser analisados:

- como o token e criado
- como o token e validado
- como a identidade do usuario autenticado chega ate a regra de negocio
- como roles e permissoes sao verificadas

Perguntas que a comparacao final deve responder:

- qual stack deixou a seguranca mais clara no codigo?
- qual stack exigiu menos configuracao acidental?
- o FastAPI reduziu as ambiguidades atuais de autorizacao?

### 3.4 Tratamento de erros

O que comparar:

- como erros de negocio sao mapeados para HTTP
- como erros de validacao sao retornados
- se existe ou nao um contrato unico de erro
- facilidade para padronizar payloads de erro

Pontos que devem ser analisados:

- forma de declarar excecoes
- centralizacao ou dispersao da estrategia de erro
- consistencia entre endpoints
- exposicao indevida de detalhes internos

Perguntas que a comparacao final deve responder:

- qual stack gerou um contrato de erro mais limpo?
- o FastAPI melhorou o controle sobre erros e detalhes expostos?
- houve quebra de compatibilidade relevante?

### 3.5 Logging e configuracao

O que comparar:

- mecanismo de logging
- configuracao por arquivo, env vars e defaults
- clareza da configuracao por ambiente
- facilidade para externalizar secrets
- facilidade para separar desenvolvimento, teste e producao

Pontos que devem ser analisados:

- como logs sao emitidos
- como logs de acesso e de aplicacao sao separados
- como o secret JWT e configurado
- como parametros de banco, seguranca e debug sao controlados

Perguntas que a comparacao final deve responder:

- qual stack ficou mais organizada para operacao?
- qual exige menos trabalho manual para configurar?
- o FastAPI ficou mais explicito ou mais artesanal?

## 4. Outros pontos positivos e negativos a comparar

A comparacao final tambem deve incluir observacoes criticas sobre:

- qualidade e clareza da documentacao OpenAPI gerada
- facilidade para testar endpoints e regras de negocio
- grau de acoplamento ao framework
- produtividade da camada de persistencia
- facilidade para manter o projeto pequeno sem inflar a arquitetura
- custo de onboard de um novo desenvolvedor

Perguntas que a comparacao final deve responder:

- o FastAPI deixou o sistema mais enxuto?
- houve perda de produtividade em alguma area?
- quais ganhos vieram da mudanca de stack e quais vieram apenas de melhor disciplina de implementacao?

## 5. Analise critica obrigatoria

Tao importante quanto o codigo gerado e a analise critica entre a alternativa atual e a futura implementacao em FastAPI.

A comparacao final nao deve se limitar a listar diferencas tecnicas.

Ela deve responder:

- o que a stack atual fazia melhor
- o que a stack FastAPI passou a fazer melhor
- quais problemas do projeto atual foram realmente resolvidos
- quais problemas eram do codigo e nao do framework
- quais melhorias do FastAPI dependeram de boas decisoes de arquitetura, e nao apenas da troca de tecnologia

## 6. Formato esperado da comparacao final

Quando o projeto FastAPI estiver pronto, a comparacao ideal deve conter:

1. resumo executivo
2. tabela comparativa por criterio
3. analise critica por tema
4. ganhos reais obtidos
5. perdas, tradeoffs e riscos
6. conclusao objetiva sobre a escolha da stack para este dominio

## 7. Checklist para usar no futuro

Checklist minimo:

- comparar o numero de artefatos necessarios para uma feature simples
- comparar a clareza da validacao de entrada
- comparar a clareza do fluxo JWT
- comparar a protecao de rotas por role
- comparar o contrato de erro
- comparar o mecanismo de logging
- comparar a configuracao por ambiente
- comparar a facilidade de testes
- listar ganhos e perdas reais
- separar problema de framework de problema de implementacao

## 8. Conclusao

Este documento define os objetivos da comparacao futura.

O documento de arquitetura mostra como o projeto atual foi construido.

Quando a versao em FastAPI existir, a comparacao devera usar estes criterios para produzir uma analise tecnica e critica, e nao apenas uma troca superficial de framework.
