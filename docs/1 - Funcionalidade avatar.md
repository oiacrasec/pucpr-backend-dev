# 1 - Funcionalidade Avatar (LocalStack)

Este documento descreve o passo a passo para instalar, testar e validar a funcionalidade de avatar usando S3 em ambiente local com LocalStack.

Se nenhuma configuracao de storage de avatar for informada no ambiente, o comportamento padrao da aplicacao e usar filesystem local.

## 1. Pre-requisitos

- Docker Desktop instalado e em execucao.
- API do projeto funcionando localmente.
- Banco de dados do projeto configurado no `.env`.
- Usuario de teste ja criado na base (exemplo: `user_id=1`).

## 2. Subir LocalStack (S3)

No terminal (CMD/PowerShell), execute:

```cmd
docker run --rm -it -p 4566:4566 -e SERVICES=s3 --name localstack-s3 localstack/localstack:3.8.0
```

Em outro terminal, valide saude do LocalStack:

```cmd
curl http://localhost:4566/_localstack/health
```

Esperado: resposta HTTP 200.

## 3. Criar bucket no LocalStack

Criar bucket:

```cmd
docker run --rm --network host -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 amazon/aws-cli s3api create-bucket --bucket pucpr-avatars-dev --endpoint-url http://localhost:4566
```

Listar buckets para confirmar:

```cmd
docker run --rm --network host -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 amazon/aws-cli s3api list-buckets --endpoint-url http://localhost:4566
```

Esperado: bucket `pucpr-avatars-dev` presente.

## 4. Configurar `.env` da aplicacao

Defina estas variaveis:

```env
AVATAR_STORAGE_BACKEND=s3
AVATAR_S3_BUCKET=pucpr-avatars-dev
AVATAR_S3_REGION=us-east-1
AVATAR_S3_ENDPOINT_URL=http://localhost:4566
AVATAR_S3_ACCESS_KEY_ID=test
AVATAR_S3_SECRET_ACCESS_KEY=test
AVATAR_S3_URL_EXPIRE_SECONDS=900
```

Reinicie a API apos alterar o `.env`.

## 5. Testes funcionais da API

### 5.1 Upload inicial

- Endpoint: `POST /api/users/{user_id}/avatar`
- Tipo: `multipart/form-data`
- Campo: `file`
- Exemplo: `user_id=1`

Esperado:
- HTTP `201`
- Retorno com `user_id`, `content_type`, `size_bytes`, `url`.

### 5.2 Validar objeto no bucket

```cmd
docker run --rm --network host -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 amazon/aws-cli s3api list-objects-v2 --bucket pucpr-avatars-dev --endpoint-url http://localhost:4566
```

Esperado: 1 objeto para o usuario (ex.: `1/<uuid>.png|jpg|webp`).

### 5.3 Consultar metadados

- Endpoint: `GET /api/users/{user_id}/avatar`

Esperado:
- HTTP `200`
- URL pre-assinada retornada no campo `url`.

### 5.4 Substituir avatar

- Refaca `POST /api/users/{user_id}/avatar` com outro arquivo.

Rode novamente `list-objects-v2`:

```cmd
docker run --rm --network host -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 amazon/aws-cli s3api list-objects-v2 --bucket pucpr-avatars-dev --endpoint-url http://localhost:4566
```

Esperado: continua com apenas 1 objeto (arquivo anterior removido).

### 5.5 Remover avatar

- Endpoint: `DELETE /api/users/{user_id}/avatar`

Rode novamente `list-objects-v2`.

Esperado: sem `Contents` (bucket sem objeto desse usuario).

### 5.6 Validar ausencia apos remocao

- Endpoint: `GET /api/users/{user_id}/avatar`

Esperado: HTTP `404`.

## 6. Resultado esperado final

Fluxo validado com sucesso quando todos os cenarios abaixo passam:

1. Upload cria objeto no S3 e metadados no banco.
2. Consulta retorna metadados e URL pre-assinada.
3. Substituicao remove arquivo antigo e mantem somente o novo.
4. Remocao apaga metadados e objeto.
5. Consulta apos remocao retorna `404`.

## 7. Remover completamente LocalStack do Docker

Use os comandos abaixo para limpar container, volumes e imagens relacionadas ao LocalStack.

Escolha o bloco conforme seu terminal: `PowerShell` ou `CMD`.

### 7.1 Remover container em execucao/parado

PowerShell/CMD:

```cmd
docker rm -f localstack-s3
```

### 7.2 Remover containers adicionais do LocalStack (se existirem)

PowerShell:

```powershell
docker ps -a --filter "ancestor=localstack/localstack" -q | ForEach-Object { docker rm -f $_ }
```

CMD:

```cmd
for /f %i in ('docker ps -a --filter "ancestor=localstack/localstack" -q') do docker rm -f %i
```

### 7.3 Remover volumes nomeados do LocalStack (se existirem)

PowerShell:

```powershell
docker volume ls -q | Select-String -Pattern "localstack" | ForEach-Object { docker volume rm $_.Line.Trim() }
```

CMD:

```cmd
for /f %i in ('docker volume ls -q ^| findstr /i localstack') do docker volume rm %i
```

### 7.4 Remover imagens do LocalStack

PowerShell/CMD:

```cmd
docker rmi localstack/localstack:3.8.0
docker rmi localstack/localstack:latest
```

### 7.5 Validar limpeza

PowerShell:

```powershell
docker ps -a
docker images | Select-String -Pattern "localstack"
docker volume ls | Select-String -Pattern "localstack"
```

CMD:

```cmd
docker ps -a
docker images | findstr /i localstack
docker volume ls | findstr /i localstack
```

Esperado: sem containers, imagens e volumes relacionados ao LocalStack.
