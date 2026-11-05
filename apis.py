"""Ferramentas do agente: consultas a APIs públicas brasileiras."""

import math
import re
from datetime import datetime

import requests

TEMPO_LIMITE = 8
_cache_feriados = {}


def _so_digitos(texto):
    return re.sub(r"\D", "", str(texto))


def _get_json(url):
    """Faz o GET e devolve (status, json). Erros de rede viram status None."""
    try:
        resposta = requests.get(url, timeout=TEMPO_LIMITE)
        return resposta.status_code, (resposta.json() if resposta.content else None)
    except (requests.RequestException, ValueError):
        return None, None


def buscar_cep(cep):
    """Endereço de um CEP, pelo ViaCEP."""
    cep = _so_digitos(cep)
    if len(cep) != 8:
        return {"cep": cep, "erro": "o CEP precisa ter 8 dígitos"}
    status, dados = _get_json(f"https://viacep.com.br/ws/{cep}/json/")
    if status is None:
        return {"cep": cep, "erro": "serviço de CEP indisponível no momento"}
    if status != 200 or not dados or dados.get("erro"):
        return {"cep": cep, "erro": "CEP não encontrado"}
    return {
        "cep": dados.get("cep"),
        "logradouro": dados.get("logradouro"),
        "bairro": dados.get("bairro"),
        "cidade": dados.get("localidade"),
        "uf": dados.get("uf"),
    }


def consultar_cnpj(cnpj):
    """Razão social e situação cadastral de um fornecedor, pela BrasilAPI."""
    # TODO (prata): siga o modelo de buscar_cep.
    # 1. Deixe só os dígitos e confira se são 14; senão, devolva um erro.
    # 2. Chame https://brasilapi.com.br/api/cnpj/v1/{cnpj} com _get_json.
    # 3. Trate: serviço fora do ar (status None) e CNPJ não encontrado (status diferente de 200).
    # 4. Devolva razao_social, nome_fantasia, situacao (campo descricao_situacao_cadastral),
    #    cidade (municipio), uf e atividade (cnae_fiscal_descricao).
    return {"cnpj": cnpj, "erro": "não implementado"}


def _feriados_do_ano(ano):
    """Devolve {data_iso: nome} dos feriados nacionais do ano, ou None se a API falhar."""
    # TODO (prata): chame https://brasilapi.com.br/api/feriados/v1/{ano} com _get_json.
    # TODO (ouro): guarde o resultado em _cache_feriados para não chamar a API de novo.
    return None


def _ler_data(texto):
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto.strip(), formato).date()
        except (AttributeError, ValueError):
            continue
    return None


def verificar_dia_util(data):
    """Diz se a data é dia útil (sem fim de semana nem feriado nacional) e qual o próximo dia útil."""
    # TODO (prata):
    # 1. Converta a data com _ler_data; se vier None, devolva um erro pedindo dd/mm/aaaa.
    # 2. Uma data não é útil se for sábado (weekday() == 5), domingo (6) ou feriado.
    # 3. Devolva {"data": ..., "util": True/False}; se não for útil, inclua "motivo"
    #    e "proximo_dia_util" (some um dia com timedelta até achar um dia útil).
    # 4. Se a API de feriados falhar, ainda verifique o fim de semana e inclua um "aviso".
    return {"data": data, "erro": "não implementado"}


def _normalizar_valor(valor):
    texto = re.sub(r"^(?:US)?\$\s*", "", str(valor).strip(), flags=re.IGNORECASE)
    texto = texto.replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        return None
    return numero if math.isfinite(numero) else None


def _normalizar_moeda(moeda):
    codigo = str(moeda or "USD").strip().upper()
    if codigo in {"$", "US$", "DOLAR", "DÓLAR", "DOLARES", "DÓLARES", "DOLLAR", "DOLLARS"}:
        return "USD"
    return codigo


def _buscar_cotacao(moeda):
    provedores = (
        (
            f"https://open.er-api.com/v6/latest/{moeda}",
            lambda dados: (
                dados.get("rates", {}).get("BRL"),
                dados.get("time_last_update_utc"),
            )
            if dados.get("result") == "success"
            and isinstance(dados.get("rates"), dict)
            else (None, None),
        ),
        (
            f"https://api.frankfurter.dev/v1/latest?base={moeda}&symbols=BRL",
            lambda dados: (dados.get("rates", {}).get("BRL"), dados.get("date"))
            if isinstance(dados.get("rates"), dict)
            else (None, None),
        ),
    )
    falha_de_conexao = True
    resposta_invalida = False

    for url, extrair in provedores:
        status, dados = _get_json(url)
        if status is None:
            continue
        falha_de_conexao = False
        if status == 404 or status == 400:
            resposta_invalida = True
            continue
        if status != 200 or not isinstance(dados, dict):
            continue

        taxa, consultado_em = extrair(dados)
        try:
            taxa = float(taxa)
        except (TypeError, ValueError):
            resposta_invalida = True
            continue
        if math.isfinite(taxa) and taxa > 0:
            return taxa, consultado_em
        resposta_invalida = True

    if falha_de_conexao:
        return None, "serviço de cotação indisponível no momento"
    if resposta_invalida:
        return None, "moeda não encontrada ou cotação inválida"
    return None, "serviço de cotação indisponível no momento"


def converter_moeda(valor, moeda="USD"):
    """Converte uma moeda estrangeira para reais pela cotação disponível."""
    valor = _normalizar_valor(valor)
    if valor is None:
        return {"moeda": moeda, "erro": "o valor precisa ser numérico"}

    moeda = _normalizar_moeda(moeda)
    if not re.fullmatch(r"[A-Z]{3}", moeda):
        return {"moeda": moeda, "erro": "código de moeda inválido"}

    cotacao, consultado_em = _buscar_cotacao(moeda)
    if cotacao is None:
        return {"moeda": moeda, "erro": consultado_em}

    return {
        "moeda": moeda,
        "valor_original": valor,
        "cotacao": cotacao,
        "valor_em_reais": round(valor * cotacao, 2),
        "consultado_em": consultado_em,
    }
