import logging
import sys
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _exibir_top_n(top_n, data: str) -> None:
    print()
    print("=" * 72)
    print(f"  B3 FACTOR INVESTING — TOP {len(top_n)} ({data})")
    print("=" * 72)
    print(
        f"  {'Rank':<6} {'Ticker':<10} {'P/L':>8} {'ROE':>10} {'Volume':>14} {'Score':>8}"
    )
    print("-" * 72)
    for _, row in top_n.iterrows():
        roe_pct = f"{row['returnOnEquity'] * 100:.1f}%"
        volume_fmt = f"{row['volume']:,.0f}".replace(",", ".")
        print(
            f"  {int(row['rank']):<6} {row['symbol']:<10} {row['priceEarnings']:>8.2f} {roe_pct:>10} {volume_fmt:>14} {row['combined_score']:>8.0f}"
        )
    print("=" * 72)
    print("  Score = Rank P/L + Rank ROE (menor = melhor)")
    print("  Filtros: P/L > 0 | ROE > 0 | Volume ≥ R$ 1.000.000")
    print("=" * 72)
    print()


def main() -> None:
    logger.info("Iniciando pipeline B3 Factor Investing...")
    from src.config import ensure_output_dir, get_token

    get_token()
    ensure_output_dir()
    from src.etl.extract import extrair_acoes
    from src.etl.load import carregar
    from src.etl.transform import transformar

    logger.info("[1/3] EXTRACT — Consultando API Brapi...")
    dados_crus = extrair_acoes()
    logger.info("[2/3] TRANSFORM — Validando, higienizando e rankeando...")
    ranking_completo, top_n = transformar(dados_crus)
    logger.info("[3/3] LOAD — Persistindo resultados...")
    csv_path = carregar(ranking_completo, top_n)
    data = date.today().isoformat()
    _exibir_top_n(top_n, data)
    logger.info("Pipeline concluído com sucesso!")
    logger.info("CSV: %s", csv_path)
    logger.info("SQLite: output/b3_factor.db")


if __name__ == "__main__":
    main()
