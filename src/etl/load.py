import logging
from datetime import date
import pandas as pd
from src.config import DB_PATH, OUTPUT_DIR, ensure_output_dir
from src.database import Ranking, create_db_engine, get_session, init_db

logger = logging.getLogger(__name__)


def _salvar_csv(ranking_completo: pd.DataFrame, data: str) -> str:
    colunas = [
        "rank",
        "symbol",
        "companyName",
        "website_domain",
        "priceEarnings",
        "returnOnEquity",
        "volume",
        "dailyChange",
        "combined_score",
    ]
    colunas_disponiveis = [c for c in colunas if c in ranking_completo.columns]
    filepath = OUTPUT_DIR / f"ranking_{data}.csv"
    ranking_completo[colunas_disponiveis].to_csv(filepath, index=False, sep=";")
    logger.info("CSV salvo em: %s (%d linhas)", filepath, len(ranking_completo))
    return str(filepath)


def _salvar_sqlite(top_n: pd.DataFrame, data: str) -> None:
    engine = create_db_engine(str(DB_PATH))
    init_db(engine)
    session = get_session(engine)
    try:
        for _, row in top_n.iterrows():
            existente = (
                session.query(Ranking)
                .filter_by(date=data, symbol=row["symbol"])
                .first()
            )
            if existente:
                existente.rank = int(row["rank"])
                existente.price_earnings = float(row["priceEarnings"])
                existente.return_on_equity = float(row["returnOnEquity"])
                existente.volume = float(row["volume"])
                existente.combined_score = float(row["combined_score"])
            else:
                novo = Ranking(
                    date=data,
                    rank=int(row["rank"]),
                    symbol=row["symbol"],
                    price_earnings=float(row["priceEarnings"]),
                    return_on_equity=float(row["returnOnEquity"]),
                    volume=float(row["volume"]),
                    combined_score=float(row["combined_score"]),
                )
                session.add(novo)
        session.commit()
        logger.info(
            "SQLite atualizado: %d registros para %s em %s", len(top_n), data, DB_PATH
        )
    except Exception as e:
        session.rollback()
        logger.error("Erro ao salvar no SQLite: %s", e)
        raise
    finally:
        session.close()


def carregar(ranking_completo: pd.DataFrame, top_n: pd.DataFrame) -> str:
    data = date.today().isoformat()
    ensure_output_dir()
    csv_path = _salvar_csv(ranking_completo, data)
    _salvar_sqlite(top_n, data)
    return csv_path
