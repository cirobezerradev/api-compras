"""Agente de Compras da Manutenção: instruções, ferramentas e ciclo.

Rodar no terminal: python agente.py
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from apis import buscar_cep, consultar_cnpj, converter_moeda, verificar_dia_util

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL") or None)
MODELO = os.getenv("MODELO") or "gpt-4o-mini"

INSTRUCOES = """Você é o agente de compras e planejamento da manutenção da fábrica.
Ajude técnicos e compradores a conferir fornecedores, converter preços de peças
importadas e escolher datas para paradas de manutenção.

Regras:
- Use as ferramentas para consultar CEP, CNPJ, cotação e dias úteis; nunca invente esses dados.
- Ao receber um valor com "$" ou mencionado em dólares, interprete a moeda como USD e use converter_moeda.
- Se a moeda não for informada, converter_moeda usa USD por padrão.
- Se uma ferramenta devolver "erro", explique o problema em palavras simples.
- Ao converter preços, informe a cotação usada e o horário da consulta.
- Não feche compras nem confirme pedidos: você só informa.
- Responda sempre em português.

Formato:
- Respostas curtas, em até 5 itens, com os números em destaque."""

FUNCOES = {
    "buscar_cep": buscar_cep,
    "consultar_cnpj": consultar_cnpj,
    "verificar_dia_util": verificar_dia_util,
    "converter_moeda": converter_moeda,
}


def ferramenta(nome, descricao, parametros, obrigatorios):
    return {"type": "function", "function": {"name": nome, "description": descricao,
            "parameters": {"type": "object", "properties": parametros, "required": obrigatorios}}}


TOOLS = [
    ferramenta("buscar_cep", "Retorna o endereço de um CEP brasileiro.",
               {"cep": {"type": "string", "description": "CEP com ou sem traço"}}, ["cep"]),
    # TODO (prata): descreva consultar_cnpj e verificar_dia_util, como as outras duas.
    ferramenta(
        "converter_moeda",
        "Converte um valor em moeda estrangeira para reais. Use USD para valores com '$' "
        "ou em dólares. Se a moeda for omitida, assume USD. O valor pode conter '$', como '$ 1.5'.",
        {
            "valor": {
                "type": "string",
                "description": "Valor a converter, por exemplo '$ 1.5' ou '1,5'",
            },
            "moeda": {
                "type": "string",
                "description": "Código da moeda: USD, EUR, JPY...; opcional, padrão USD",
            },
        },
        ["valor"],
    ),
]


def rodar_agente(mensagens, max_passos=6):
    """Chama o modelo até a resposta final. Devolve (resposta, ferramentas usadas, tokens)."""
    usadas, tokens = [], 0
    for _ in range(max_passos):
        r = client.chat.completions.create(model=MODELO, messages=mensagens, tools=TOOLS)
        tokens += r.usage.total_tokens if r.usage else 0
        msg = r.choices[0].message
        if not msg.tool_calls:
            mensagens.append({"role": "assistant", "content": msg.content})
            return msg.content, usadas, tokens
        mensagens.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments}}
                           for c in msg.tool_calls],
        })
        for chamada in msg.tool_calls:
            funcao = FUNCOES.get(chamada.function.name)
            try:
                args = json.loads(chamada.function.arguments or "{}")
                resultado = funcao(**args) if funcao else {"erro": "ferramenta desconhecida"}
            except (json.JSONDecodeError, TypeError):
                args, resultado = {}, {"erro": "argumentos inválidos"}
            usadas.append((chamada.function.name, args, resultado))
            mensagens.append({"role": "tool", "tool_call_id": chamada.id,
                              "content": json.dumps(resultado, ensure_ascii=False)})
    return "Não consegui concluir dentro do limite de passos.", usadas, tokens


if __name__ == "__main__":
    historico = [{"role": "system", "content": INSTRUCOES}]
    print("Agente de Compras da Manutenção. Digite 'sair' para encerrar.")
    while (pergunta := input("Você: ").strip()).lower() != "sair":
        historico.append({"role": "user", "content": pergunta})
        resposta, usadas, _ = rodar_agente(historico)
        for nome, args, resultado in usadas:
            print(f"  [ferramenta] {nome}({args}) -> {resultado}")
        print(f"Agente: {resposta}\n")
