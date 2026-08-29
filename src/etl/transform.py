import logging
import pandas as pd
from pydantic import ValidationError
from src.config import MIN_VOLUME, TOP_N
from src.models import AcaoSchema

logger = logging.getLogger(__name__)


def _validar_com_pydantic(dados_crus: list[dict]) -> list[dict]:
    validados: list[dict] = []
    rejeitados = 0
    for item in dados_crus:
        try:
            acao = AcaoSchema(
                symbol=item.get("symbol", ""),
                priceEarnings=item.get("priceEarnings"),
                returnOnEquity=item.get("returnOnEquity"),
                volume=item.get("volume", 0),
            )
            validados.append(acao.model_dump())
        except (ValidationError, TypeError, ValueError) as e:
            rejeitados += 1
            ticker = item.get("symbol", "DESCONHECIDO")
            logger.debug("Rejeitado [%s]: %s", ticker, e)
    logger.info(
        "Validação Pydantic: %d aprovados, %d rejeitados.", len(validados), rejeitados
    )
    return validados


def _higienizar(df: pd.DataFrame) -> pd.DataFrame:
    total_inicial = len(df)
    df = df[df["priceEarnings"] > 0].copy()
    apos_pl = len(df)
    df = df[df["returnOnEquity"] > 0].copy()
    apos_roe = len(df)
    df = df[df["volume"] >= MIN_VOLUME].copy()
    apos_volume = len(df)
    logger.info(
        "Higienização: %d → P/L>0: %d → ROE>0: %d → Vol≥%s: %d",
        total_inicial,
        apos_pl,
        apos_roe,
        f"{MIN_VOLUME:,.0f}",
        apos_volume,
    )
    return df


def _rankear(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rank_pl"] = df["priceEarnings"].rank(ascending=True, method="min")
    df["rank_roe"] = df["returnOnEquity"].rank(ascending=False, method="min")
    df["combined_score"] = df["rank_pl"] + df["rank_roe"]
    df = df.sort_values("combined_score", ascending=True).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def transformar(dados_crus: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    validados = _validar_com_pydantic(dados_crus)
    if not validados:
        logger.error("Nenhum ativo passou na validação Pydantic. Abortando.")
        raise SystemExit(1)
    df = pd.DataFrame(validados)
    df = _higienizar(df)
    if df.empty:
        logger.error("Nenhum ativo restou após higienização. Abortando.")
        raise SystemExit(1)
    ranking_completo = _rankear(df)
    top_n = ranking_completo.head(TOP_N).copy()
    logger.info(
        "Ranking finalizado: %d ativos rankeados, Top %d selecionados.",
        len(ranking_completo),
        TOP_N,
    )
    return (ranking_completo, top_n)
