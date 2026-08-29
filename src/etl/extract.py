import logging
import time
import requests
from src.config import BASE_URL, MIN_VOLUME, get_token

logger = logging.getLogger(__name__)
MAX_RETRIES = 3
BACKOFF_BASE = 2
THROTTLE_SECS = 0.2


def _request_com_retry(url: str, params: dict, descricao: str) -> dict | None:
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code in (401, 403):
                logger.warning(
                    "%s — Permissão negada (HTTP %d). Seu plano pode não cobrir este ativo.",
                    descricao,
                    response.status_code,
                )
                return None
            logger.warning(
                "%s — HTTP %s (tentativa %d/%d): %s",
                descricao,
                response.status_code,
                tentativa,
                MAX_RETRIES,
                e,
            )
        except requests.exceptions.ConnectionError as e:
            logger.warning(
                "%s — Erro de conexão (tentativa %d/%d): %s",
                descricao,
                tentativa,
                MAX_RETRIES,
                e,
            )
        except requests.exceptions.Timeout:
            logger.warning(
                "%s — Timeout (tentativa %d/%d)", descricao, tentativa, MAX_RETRIES
            )
        except requests.exceptions.RequestException as e:
            logger.warning(
                "%s — Erro inesperado (tentativa %d/%d): %s",
                descricao,
                tentativa,
                MAX_RETRIES,
                e,
            )
        if tentativa < MAX_RETRIES:
            wait = BACKOFF_BASE**tentativa
            time.sleep(wait)
    return None


def _extrair_lista_tickers() -> list[dict]:
    url = f"{BASE_URL}/quote/list"
    params = {
        "type": "stock",
        "sortBy": "volume",
        "sortOrder": "desc",
        "limit": 1000,
        "token": get_token(),
    }
    logger.info("Extraindo lista de tickers da B3...")
    data = _request_com_retry(url, params, "quote/list")
    if data is None:
        logger.critical("Falha ao extrair lista de tickers. Abortando.")
        raise SystemExit(1)
    stocks = data.get("stocks", [])
    logger.info("Lista obtida: %d tickers.", len(stocks))
    return stocks


def _extrair_fundamentos(ticker: str, token: str) -> dict | None:
    url = f"{BASE_URL}/quote/{ticker}"
    params = {"modules": "financialData", "token": token}
    data = _request_com_retry(url, params, f"quote/{ticker}")
    if data is None:
        return None
    results = data.get("results", [])
    if not results:
        return None
    stock_data = results[0]
    pe = stock_data.get("priceEarnings")
    fin_data = stock_data.get("financialData", {})
    roe = fin_data.get("returnOnEquity")
    return {"priceEarnings": pe, "returnOnEquity": roe}


def extrair_acoes() -> list[dict]:
    stocks = _extrair_lista_tickers()
    token = get_token()
    stocks_liquidos = [s for s in stocks if s.get("volume", 0) >= MIN_VOLUME]
    logger.info(
        "Tickers com volume >= %s: %d (de %d)",
        f"{MIN_VOLUME:,.0f}",
        len(stocks_liquidos),
        len(stocks),
    )
    resultados: list[dict] = []
    total = len(stocks_liquidos)
    for i, stock in enumerate(stocks_liquidos, 1):
        ticker = stock.get("stock", "")
        volume = stock.get("volume", 0)
        if not ticker:
            continue
        if i % 10 == 0 or i == 1:
            logger.info("Extraindo fundamentos: %d/%d (%s)...", i, total, ticker)
        fundamentos = _extrair_fundamentos(ticker, token)
        time.sleep(THROTTLE_SECS)
        if fundamentos:
            registro = {
                "symbol": ticker,
                "volume": volume,
                "priceEarnings": fundamentos.get("priceEarnings"),
                "returnOnEquity": fundamentos.get("returnOnEquity"),
            }
            resultados.append(registro)
    logger.info(
        "Extração concluída: %d ativos processados com sucesso.", len(resultados)
    )
    return resultados
