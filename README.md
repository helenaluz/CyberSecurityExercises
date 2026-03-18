# Servico de Registro e Autenticacao Segura

Este trabalho consiste na adaptacao de uma API simples em FastAPI para aplicar tecnicas basicas de seguranca no processo de registro e autenticacao de usuarios.

O objetivo principal foi impedir o uso de senhas fracas no cadastro e dificultar ataques de forca bruta no endpoint de login.

## Tecnicas Utilizadas

### 1. Validacao de Senha Forte

No endpoint `/register/`, foi implementada uma validacao para bloquear senhas fracas no momento do cadastro.

A senha so e aceita quando atende a todos os criterios abaixo:

- possui entre 6 e 15 caracteres
- contem pelo menos 1 letra maiuscula
- contem pelo menos 1 letra minuscula
- contem pelo menos 1 numero
- contem pelo menos 1 caractere especial

Essa tecnica reduz o risco de criacao de senhas faceis de adivinhar, aumentando a seguranca da conta desde o registro.

### 2. Atraso Progressivo no Login

No endpoint `/login/`, foi implementado atraso progressivo a cada tentativa falha de autenticacao.

Funcionamento:

- 1 erro: resposta apos 2 segundos
- 2 erros consecutivos: resposta apos 4 segundos
- 3 erros consecutivos: resposta apos 8 segundos

Essa tecnica dificulta ataques automatizados, porque aumenta o tempo necessario para testar varias senhas erradas em sequencia.

### 3. Bloqueio Temporario de Conta

Tambem no endpoint `/login/`, foi implementado bloqueio temporario da conta apos 3 tentativas falhas consecutivas.

Funcionamento:

- apos 3 erros seguidos, a conta e bloqueada por 5 minutos
- durante esse periodo, mesmo que a senha correta seja informada, o acesso continua bloqueado
- apos o tempo de bloqueio, o usuario pode tentar novamente

Essa tecnica reduz a chance de sucesso de ataques por tentativa e erro e protege melhor as contas dos usuarios.

## Estrutura da Solucao

Para viabilizar essas tecnicas, o modelo de usuario passou a armazenar informacoes extras:

- `failed_attempts`: quantidade de tentativas falhas consecutivas
- `blocked_until`: data e hora ate a qual a conta ficara bloqueada

Quando o login e bem-sucedido:

- o contador de falhas volta para zero
- o bloqueio temporario e removido

## Tecnicas Escolhidas para Atender ao Enunciado

O enunciado solicitava:

1. impedir senhas fracas no registro
2. implementar pelo menos duas tecnicas de protecao no login

As tecnicas escolhidas neste trabalho foram:

- bloqueio temporario de contas
- atraso progressivo

Essas duas opcoes foram selecionadas por serem simples de demonstrar, eficientes contra tentativas repetidas de acesso indevido e possiveis de implementar sem depender de servicos externos.

## Como Executar

No terminal, dentro da pasta do projeto, execute:

```powershell
python -m uvicorn servico:app --reload
```

Depois, abra no navegador:

```text
http://127.0.0.1:8000/docs
```

## Como Testar

### Teste 1: senha fraca no registro

No endpoint `/register/`, envie uma senha simples, como:

```json
{
  "username": "ana",
  "email": "ana@email.com",
  "password": "abc"
}
```

Resultado esperado:

- a API deve rejeitar o cadastro com erro `400`
- a mensagem deve indicar qual criterio da senha nao foi atendido

### Teste 2: senha forte no registro

Exemplo:

```json
{
  "username": "ana",
  "email": "ana@email.com",
  "password": "Ana@123"
}
```

Resultado esperado:

- usuario registrado com sucesso

### Teste 3: tentativas falhas no login

No endpoint `/login/`, tente entrar com senha errada varias vezes:

```json
{
  "username": "ana",
  "password": "senhaerrada"
}
```

Resultado esperado:

- primeira falha com atraso de 2 segundos
- segunda falha com atraso de 4 segundos
- terceira falha com atraso de 8 segundos
- apos a terceira falha, a conta deve ser bloqueada por 5 minutos

### Teste 4: tentativa durante o bloqueio

Mesmo informando a senha correta, o login deve continuar bloqueado ate o fim dos 5 minutos.

## Observacao

Neste trabalho, a senha ainda esta armazenada diretamente no banco apenas para manter a implementacao simples e focada no enunciado da atividade.

Em uma aplicacao real, o correto seria armazenar a senha com hash criptografico, usando bibliotecas como `passlib` ou `bcrypt`.
