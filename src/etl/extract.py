import logging
import time
import yfinance as yf

logger = logging.getLogger(__name__)

TICKERS_IBOV = [
    "RRRP3", "ALOS3", "ALPA4", "ABEV3", "ARZZ3", "ASAI3", "AZUL4", "B3SA3", 
    "BBSE3", "BBDC3", "BBDC4", "BRAP4", "BBAS3", "BRKM5", "BRFS3", "BPAC11", 
    "CRFB3", "CCRO3", "CMIG4", "CIEL3", "COGN3", "CPLE6", "CSAN3", "CPFE3", 
    "CMIN3", "CVCB3", "CYRE3", "DXCO3", "ELET3", "ELET6", "EMBR3", "ENGI11", 
    "ENEV3", "EGIE3", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "NTCO3", 
    "SOMA3", "HAPV3", "HYPE3", "IGTI11", "IRBR3", "ITSA4", "ITUB4", "JBSS3", 
    "KLBN11", "RENT3", "LREN3", "LWSA3", "MGLU3", "MRFG3", "BEEF3", "MRVE3", 
    "MULT3", "PCAR3", "PETR3", "PETR4", "PRIO3", "PETZ3", "RADL3", "RAIZ4", 
    "RDOR3", "RAIL3", "SBSP3", "SANB11", "SMTO3", "CSNA3", "SLCE3", "SUZB3", 
    "TAEE11", "VIVT3", "TIMS3", "TOTS3", "UGPA3", "USIM5", "VALE3", "VAMO3", 
    "VBBR3", "WEGE3", "YDUQ3"
]

def extrair_acoes() -> list[dict]:
    logger.info("Extraindo dados do Yahoo Finance (IBOVESPA)...")
    resultados = []
    
    for i, ticker in enumerate(TICKERS_IBOV, 1):
        symbol_sa = f"{ticker}.SA"
        
        # Log a cada 10 ações para não sujar o terminal
        if i % 10 == 0 or i == 1:
            logger.info("Processando %d/%d: %s", i, len(TICKERS_IBOV), ticker)
        
        try:
            stock = yf.Ticker(symbol_sa)
            info = stock.info
            
            pl = info.get("trailingPE") or info.get("forwardPE")
            roe = info.get("returnOnEquity")
            volume = info.get("averageVolume") or info.get("volume")
            
            # Novos campos amigáveis
            import re
            nome_bruto = info.get("longName") or info.get("shortName") or ticker
            # Limpeza do nome (ex: "Petróleo Brasileiro S.A. - Petrobras" -> "Petrobras")
            if "-" in nome_bruto:
                nome = nome_bruto.split("-")[-1].strip()
            else:
                nome = re.sub(r'(?i)(\sS\.A\.| S/A| S\.A| Holding| Participações| Participacoes| S\.A).*$', '', nome_bruto).strip()
            
            preco = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            fechamento_ant = info.get("previousClose", 0)
            
            variacao = 0.0
            if preco and fechamento_ant:
                variacao = (preco - fechamento_ant) / fechamento_ant
                
            # Extrair domínio do site para usar na API do Clearbit Logo
            site = info.get("website", "")
            dominio = ""
            if site:
                dominio = site.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            
            resultados.append({
                "symbol": ticker,
                "companyName": nome,
                "website_domain": dominio,
                "priceEarnings": pl,
                "returnOnEquity": roe,
                "volume": volume,
                "dailyChange": variacao
            })
            
            time.sleep(0.1)
            
        except Exception as e:
            logger.warning("Falha ao extrair %s: %s", ticker, str(e))
            
    logger.info("Extração concluída: %d ativos processados.", len(resultados))
    return resultados
