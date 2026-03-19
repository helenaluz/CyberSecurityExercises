# Serviço de Registro e Autenticação Segura

Este trabalho consiste na adaptação de uma API simples em FastAPI para aplicar técnicas básicas de segurança no processo de registro e autenticação de usuários.

O objetivo principal foi impedir o uso de senhas fracas no cadastro e dificultar ataques de força bruta no endpoint de login.

## Técnicas Utilizadas

### 1. Validação de Senha Forte

No endpoint `/register/`, foi implementada uma validação para bloquear senhas fracas no momento do cadastro.

A senha só é aceita quando atende a todos os critérios abaixo:

- possui entre 6 e 15 caracteres  
- contém pelo menos 1 letra maiúscula  
- contém pelo menos 1 letra minúscula  
- contém pelo menos 1 número  
- contém pelo menos 1 caractere especial  

Essa técnica reduz o risco de criação de senhas fáceis de adivinhar, aumentando a segurança da conta desde o registro.

### 2. Atraso Progressivo no Login

No endpoint `/login/`, foi implementado atraso progressivo a cada tentativa falha de autenticação.

Funcionamento:

- 1 erro: resposta após 2 segundos  
- 2 erros consecutivos: resposta após 4 segundos  
- 3 erros consecutivos: resposta após 8 segundos  

Essa técnica dificulta ataques automatizados, porque aumenta o tempo necessário para testar várias senhas erradas em sequência.

### 3. Bloqueio Temporário de Conta

Também no endpoint `/login/`, foi implementado bloqueio temporário da conta após 3 tentativas falhas consecutivas.

Funcionamento:

- após 3 erros seguidos, a conta é bloqueada por 5 minutos  
- durante esse período, mesmo que a senha correta seja informada, o acesso continua bloqueado  
- após o tempo de bloqueio, o usuário pode tentar novamente  

Essa técnica reduz a chance de sucesso de ataques por tentativa e erro e protege melhor as contas dos usuários.

## Estrutura da Solução

Para viabilizar essas técnicas, o modelo de usuário passou a armazenar informações extras:

- `failed_attempts`: quantidade de tentativas falhas consecutivas  
- `blocked_until`: data e hora até a qual a conta ficará bloqueada  

Quando o login é bem-sucedido:

- o contador de falhas volta para zero  
- o bloqueio temporário é removido  

## Técnicas Escolhidas para Atender ao Enunciado

O enunciado solicitava:

1. impedir senhas fracas no registro  
2. implementar pelo menos duas técnicas de proteção no login  

As técnicas escolhidas neste trabalho foram:

- bloqueio temporário de contas  
- atraso progressivo  

Essas duas opções foram selecionadas por serem simples de demonstrar, eficientes contra tentativas repetidas de acesso indevido e possíveis de implementar sem depender de serviços externos.

## Como Executar

No terminal, dentro da pasta do projeto, execute:

```bash
python -m uvicorn servico:app --reload
