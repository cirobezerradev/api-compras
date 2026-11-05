# Agente de Compras da Manutenção

Assistente em português para apoiar técnicos e compradores da manutenção industrial. O agente usa um modelo compatível com a API da OpenAI e ferramentas de consulta para responder sobre endereços de fornecedores e conversão de preços para reais. Ele apenas fornece informações: não realiza compras nem confirma pedidos.

## Funcionalidades

- **Consulta de CEP:** busca endereço brasileiro pelo ViaCEP.
- **Conversão de moeda:** converte valores de moedas estrangeiras para reais. Usa USD por padrão e aceita valores como `$ 1.5`; tenta um provedor alternativo se a cotação principal falhar.
- **Interface web:** conversa com o agente pelo Streamlit e exibe as ferramentas acionadas e o consumo de tokens.
- **Modo terminal:** permite conversar com o agente diretamente pelo terminal.

> **Em desenvolvimento:** as funções de consulta de CNPJ e verificação de dia útil ainda não estão implementadas. Elas não estão disponíveis como ferramentas do agente.

## Requisitos

- Python instalado.
- Uma chave de API para a OpenAI ou para um serviço compatível com sua API.
- Acesso à internet para conversar com o modelo e consultar os serviços externos.

## Instalação

Clone o repositório, entre na pasta do projeto e, opcionalmente, crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo local `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows, copie o arquivo `.env.example` para `.env` manualmente. Edite `.env` e informe sua chave:

```dotenv
OPENAI_API_KEY=sua-chave-de-api
MODELO=
# BASE_URL=https://seu-provedor-compativel/v1
```

`MODELO` é opcional: se estiver vazio, o agente usa `gpt-4o-mini`. `BASE_URL` também é opcional e deve ser configurada quando for usar um provedor compatível diferente do padrão. O `.env` não deve ser compartilhado nem enviado ao Git.

## Como executar

### Interface web

```bash
streamlit run app.py
```

O Streamlit exibirá o endereço local da aplicação no terminal. Use o campo de conversa para fazer perguntas.

### Terminal

```bash
python agente.py
```

Digite `sair` para encerrar. As chamadas de ferramentas realizadas são exibidas junto com as respostas.

### Verificar a configuração da API

```bash
python teste_chave.py
```

O script testa a autenticação e uma chamada ao modelo. Ele pode consumir tokens.

## Exemplos de perguntas

- “Qual é o endereço do CEP 01310-100?”
- “Quanto custa US$ 1,50 em reais?”
- “Converta 100 euros para reais.”

## Testes

Execute os testes automatizados com:

```bash
pytest
```

## Estrutura do projeto

| Arquivo | Descrição |
| --- | --- |
| `agente.py` | Instruções do agente, ferramentas disponíveis e ciclo de interação com o modelo. |
| `apis.py` | Integrações com serviços públicos, incluindo CEP e cotação de moedas. |
| `app.py` | Interface web construída com Streamlit. |
| `teste_chave.py` | Verificação da chave e de uma chamada ao modelo. |
| `tests/` | Testes automatizados das ferramentas de API. |
| `.env.example` | Modelo das variáveis de ambiente necessárias. |

## Serviços externos

- **OpenAI ou provedor compatível:** processamento das mensagens do agente.
- **ViaCEP:** consulta de CEP.
- **open.er-api.com** e **Frankfurter:** cotação cambial, com tentativa de fallback.

As consultas dependem de conexão com a internet e da disponibilidade dos serviços. As mensagens enviadas ao agente são encaminhadas ao provedor de modelo configurado. Não inclua credenciais ou informações sensíveis nas conversas.
