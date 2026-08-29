import pandas as pd
import pytest
from pydantic import ValidationError
from src.etl.transform import _higienizar, _rankear, _validar_com_pydantic
from src.models import AcaoSchema


@pytest.fixture
def dados_validos() -> list[dict]:
    return [
        {
            "symbol": "ACAO1",
            "priceEarnings": 5.0,
            "returnOnEquity": 0.3,
            "volume": 5000000,
        },
        {
            "symbol": "ACAO2",
            "priceEarnings": 10.0,
            "returnOnEquity": 0.2,
            "volume": 3000000,
        },
        {
            "symbol": "ACAO3",
            "priceEarnings": 3.0,
            "returnOnEquity": 0.4,
            "volume": 8000000,
        },
    ]


@pytest.fixture
def dados_com_lixo() -> list[dict]:
    return [
        {
            "symbol": "BOA3",
            "priceEarnings": 6.0,
            "returnOnEquity": 0.25,
            "volume": 2000000,
        },
        {
            "symbol": "RUIM1",
            "priceEarnings": None,
            "returnOnEquity": 0.15,
            "volume": 1500000,
        },
        {"symbol": "", "priceEarnings": 8.0, "returnOnEquity": 0.1, "volume": 1000000},
        {
            "symbol": "RUIM3",
            "priceEarnings": 7.0,
            "returnOnEquity": "abc",
            "volume": 1000000,
        },
    ]


@pytest.fixture
def df_para_higienizar() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": "OK1",
                "priceEarnings": 5.0,
                "returnOnEquity": 0.2,
                "volume": 2000000,
            },
            {
                "symbol": "RUIM_PL",
                "priceEarnings": -3.0,
                "returnOnEquity": 0.15,
                "volume": 1500000,
            },
            {
                "symbol": "RUIM_ROE",
                "priceEarnings": 8.0,
                "returnOnEquity": -0.05,
                "volume": 3000000,
            },
            {
                "symbol": "RUIM_VOL",
                "priceEarnings": 4.0,
                "returnOnEquity": 0.3,
                "volume": 500000,
            },
            {
                "symbol": "ZERO_PL",
                "priceEarnings": 0.0,
                "returnOnEquity": 0.1,
                "volume": 5000000,
            },
            {
                "symbol": "OK2",
                "priceEarnings": 12.0,
                "returnOnEquity": 0.1,
                "volume": 4000000,
            },
        ]
    )


class TestValidacaoPydantic:

    def test_modelo_aceita_dados_validos(self):
        acao = AcaoSchema(
            symbol="PETR4", priceEarnings=6.5, returnOnEquity=0.28, volume=10000000
        )
        assert acao.symbol == "PETR4"
        assert acao.priceEarnings == 6.5

    def test_modelo_rejeita_symbol_vazio(self):
        with pytest.raises(ValidationError):
            AcaoSchema(symbol="", priceEarnings=5.0, returnOnEquity=0.2, volume=1000000)

    def test_modelo_rejeita_priceearnings_none(self):
        with pytest.raises(ValidationError):
            AcaoSchema(
                symbol="TEST3", priceEarnings=None, returnOnEquity=0.2, volume=1000000
            )

    def test_modelo_rejeita_volume_negativo(self):
        with pytest.raises(ValidationError):
            AcaoSchema(
                symbol="TEST3", priceEarnings=5.0, returnOnEquity=0.2, volume=-100
            )

    def test_validar_com_pydantic_filtra_invalidos(self, dados_com_lixo):
        resultado = _validar_com_pydantic(dados_com_lixo)
        assert len(resultado) == 1
        assert resultado[0]["symbol"] == "BOA3"


class TestHigienizacao:

    def test_remove_pl_negativo_e_zero(self, df_para_higienizar):
        resultado = _higienizar(df_para_higienizar)
        symbols = resultado["symbol"].tolist()
        assert "RUIM_PL" not in symbols
        assert "ZERO_PL" not in symbols

    def test_remove_roe_negativo(self, df_para_higienizar):
        resultado = _higienizar(df_para_higienizar)
        assert "RUIM_ROE" not in resultado["symbol"].tolist()

    def test_remove_volume_baixo(self, df_para_higienizar):
        resultado = _higienizar(df_para_higienizar)
        assert "RUIM_VOL" not in resultado["symbol"].tolist()

    def test_mantem_acoes_validas(self, df_para_higienizar):
        resultado = _higienizar(df_para_higienizar)
        symbols = resultado["symbol"].tolist()
        assert "OK1" in symbols
        assert "OK2" in symbols
        assert len(resultado) == 2


class TestRanking:

    def test_ranking_ordem_correta(self):
        df = pd.DataFrame(
            [
                {
                    "symbol": "ACAO_C",
                    "priceEarnings": 10.0,
                    "returnOnEquity": 0.2,
                    "volume": 5000000,
                },
                {
                    "symbol": "ACAO_A",
                    "priceEarnings": 3.0,
                    "returnOnEquity": 0.4,
                    "volume": 8000000,
                },
                {
                    "symbol": "ACAO_B",
                    "priceEarnings": 5.0,
                    "returnOnEquity": 0.3,
                    "volume": 3000000,
                },
            ]
        )
        resultado = _rankear(df)
        assert resultado.iloc[0]["symbol"] == "ACAO_A"
        assert resultado.iloc[1]["symbol"] == "ACAO_B"
        assert resultado.iloc[2]["symbol"] == "ACAO_C"

    def test_ranking_tem_colunas_esperadas(self):
        df = pd.DataFrame(
            [
                {
                    "symbol": "X",
                    "priceEarnings": 5.0,
                    "returnOnEquity": 0.2,
                    "volume": 1000000,
                }
            ]
        )
        resultado = _rankear(df)
        assert "rank_pl" in resultado.columns
        assert "rank_roe" in resultado.columns
        assert "combined_score" in resultado.columns
        assert "rank" in resultado.columns

    def test_ranking_score_menor_e_melhor(self):
        df = pd.DataFrame(
            [
                {
                    "symbol": "A",
                    "priceEarnings": 2.0,
                    "returnOnEquity": 0.5,
                    "volume": 1000000,
                },
                {
                    "symbol": "B",
                    "priceEarnings": 20.0,
                    "returnOnEquity": 0.05,
                    "volume": 1000000,
                },
            ]
        )
        resultado = _rankear(df)
        score_primeiro = resultado.iloc[0]["combined_score"]
        score_ultimo = resultado.iloc[-1]["combined_score"]
        assert score_primeiro < score_ultimo
