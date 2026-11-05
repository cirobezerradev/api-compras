"""Teste rápido da chave da API da OpenAI.

Rodar: python teste_chave.py
"""

import os
import sys
import time

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # o .env sempre vence variáveis antigas
chave = os.getenv("OPENAI_API_KEY", "").strip().strip("\"'")
if not chave or chave.startswith("cole-"):
    sys.exit("Crie o arquivo .env com OPENAI_API_KEY=sua-chave (veja o .env.example).")
if not chave.startswith("sk-"):
    sys.exit(f"A chave deve começar com sk-, mas começa com {chave[:4]!r}. Confira o .env.")

client = OpenAI(api_key=chave, base_url=os.getenv("BASE_URL") or None)

print("1/3 Conferindo a chave...")
try:
    modelos = sorted(m.id for m in client.models.list())
except openai.AuthenticationError:
    sys.exit("   Chave inválida ou revogada. Confira o .env.")
except openai.APIConnectionError:
    sys.exit("   Sem conexão com a API. Confira a internet ou o proxy da rede.")
print(f"   OK: a chave é válida e enxerga {len(modelos)} modelos.")

modelo = os.getenv("MODELO") or next(
    (m for m in modelos if m.startswith("gpt") and "mini" in m),
    next((m for m in modelos if m.startswith("gpt")), None),
)
if not modelo:
    sys.exit("   Nenhum modelo gpt encontrado. Defina MODELO no .env.")
print(f"2/3 Chamando o modelo {modelo}...")
inicio = time.perf_counter()
try:
    r = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": "Responda em português, em uma frase."},
            {"role": "user", "content": "O que é manutenção preditiva?"},
        ],
    )
except openai.RateLimitError:
    sys.exit("   Limite de uso ou cota atingido. Confira o saldo e o limite de gastos.")
except openai.APIStatusError as erro:
    sys.exit(f"   O serviço recusou o pedido ({erro.status_code}): {erro.message}")
tempo = time.perf_counter() - inicio
print(f"   Resposta ({tempo:.1f} s): {r.choices[0].message.content}")

u = r.usage
print(f"3/3 Consumo: {u.prompt_tokens} tokens enviados, {u.completion_tokens} gerados.")
print("\nTudo certo: a chave funciona. Para a interface, rode: streamlit run app_teste.py")
