import apis


def test_converter_moeda_converte_valor_com_simbolo_de_dolar(monkeypatch):
    def fake_get_json(url):
        assert url == "https://open.er-api.com/v6/latest/USD"
        return 200, {
            "result": "success",
            "rates": {"BRL": 5.25},
            "time_last_update_utc": "Thu, 05 Nov 2026 00:02:31 +0000",
        }

    monkeypatch.setattr(apis, "_get_json", fake_get_json)

    assert apis.converter_moeda("$ 1.5") == {
        "moeda": "USD",
        "valor_original": 1.5,
        "cotacao": 5.25,
        "valor_em_reais": 7.88,
        "consultado_em": "Thu, 05 Nov 2026 00:02:31 +0000",
    }


def test_converter_moeda_faz_fallback_se_provedor_primario_falhar(monkeypatch):
    def fake_get_json(url):
        if url == "https://open.er-api.com/v6/latest/USD":
            return 429, {"message": "Quota exceeded"}
        assert url == "https://api.frankfurter.dev/v1/latest?base=USD&symbols=BRL"
        return 200, {"date": "2026-11-05", "rates": {"BRL": 5.25}}

    monkeypatch.setattr(apis, "_get_json", fake_get_json)

    resultado = apis.converter_moeda(1.5, "dólares")

    assert resultado["moeda"] == "USD"
    assert resultado["valor_em_reais"] == 7.88
    assert resultado["consultado_em"] == "2026-11-05"


def test_converter_moeda_informa_indisponibilidade_dos_provedores(monkeypatch):
    monkeypatch.setattr(apis, "_get_json", lambda url: (None, None))

    assert apis.converter_moeda(1.5) == {
        "moeda": "USD",
        "erro": "serviço de cotação indisponível no momento",
    }


def test_converter_moeda_rejeita_valor_invalido():
    assert apis.converter_moeda("não é valor") == {
        "moeda": "USD",
        "erro": "o valor precisa ser numérico",
    }


def test_converter_moeda_rejeita_valor_nao_finito():
    assert apis.converter_moeda("nan") == {
        "moeda": "USD",
        "erro": "o valor precisa ser numérico",
    }


def test_converter_moeda_rejeita_codigo_de_moeda_invalido():
    assert apis.converter_moeda(1.5, "$$$") == {
        "moeda": "$$$",
        "erro": "código de moeda inválido",
    }
