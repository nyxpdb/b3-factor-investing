# B3 Factor Investing

Pipeline de triagem quantitativa que consome dados da B3 via Yahoo Finance (yfinance), aplica um filtro de Factor Investing (Value e Quality) e gera um ranking dos ativos listados. O projeto inclui a orquestração de extração, transformação e carga (ETL), além de um relatório corporativo de investimentos.

## Arquitetura e Processamento

1. Extração: Consumo da lista de ações do Ibovespa via `yfinance`.
2. Validação: Tipagem e checagem de integridade dos dados via Pydantic.
3. Transformação (Pandas): Filtragem de ativos de baixa liquidez e empresas com múltiplos negativos.
4. Ranking: Aplicação de metodologia baseada na Magic Formula.
5. Carga: Persistência do ranking completo diário em CSV e do Top 3 em banco relacional SQLite (via SQLAlchemy).
6. Visualização: Relatório corporativo interativo gerado em Streamlit.

## Estrutura do Projeto

```text
/
├── dashboard.py       # Relatório corporativo institucional (Streamlit)
├── src/
│   ├── config.py      # Configuração centralizada
│   ├── models.py      # Contratos de dados e validação (Pydantic)
│   ├── database.py    # Mapeamento ORM (SQLAlchemy)
│   ├── etl/
│   │   ├── extract.py # Extrator yfinance
│   │   ├── transform.py
│   │   └── load.py
│   └── main.py        # Orquestrador ETL
└── tests/
    └── test_transform.py
```

## Como Rodar

1. Clone e instale as dependências:

```bash
git clone <repo-url>
cd b3-factor-investing
pip install -r requirements.txt
```

2. Execute o pipeline de dados para gerar o ranking atualizado:

```bash
python -m src.main
```

3. Execute o painel de visualização:

```bash
python -m streamlit run dashboard.py
```

4. Execute a suíte de testes:

```bash
python -m pytest tests/ -v
```

## Regras de Negócio

O ranking combina dois fatores com peso equitativo:
- Value: Menor P/L (Price to Earnings)
- Quality: Maior ROE (Return on Equity)

Score = Rank(P/L) + Rank(ROE). O ativo com a menor soma é classificado na primeira posição.

Regras de exclusão aplicadas previamente ao ranking:
- Preço/Lucro menor ou igual a zero.
- Return on Equity menor ou igual a zero.
- Volume médio diário de negociação inferior a R$ 1.000.000,00.

## Stack Tecnológica

- Extratores: yfinance
- Contratos e Validação: pydantic
- Processamento Numérico: pandas
- Banco de Dados e ORM: sqlalchemy, sqlite3
- Interface Gráfica: streamlit, matplotlib
- Testes: pytest

## Licença
MIT
