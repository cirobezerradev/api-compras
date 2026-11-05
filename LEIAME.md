# Agente de Compras da Manutenção (código inicial)

1. `pip install -r requirements.txt`
2. Copie `.env.example` para `.env` e cole a chave da API em `OPENAI_API_KEY`.
3. `python teste_chave.py` — confere a chave.
4. Complete os `# TODO` restantes de `apis.py` e `agente.py`.
5. `streamlit run app.py` — a tela do agente.

- `apis.py` — as ferramentas que consultam APIs públicas (CEP, CNPJ, feriados, cotação).
  `buscar_cep` já está pronta: use como modelo.
- `converter_moeda` aceita valores como `$ 1.5`, assume USD quando a moeda é omitida e usa
  um provedor alternativo se a API de cotação principal estiver indisponível.
- `agente.py` — instruções, descrição das ferramentas e ciclo do agente.
- `app.py` — a tela.
