# B3 Factor Investing 📊

Pipeline de triagem quantitativa que consome dados da B3 via API Brapi, aplica filtro **Factor Investing** (Value & Quality) e seleciona os **Top 3 ativos mais eficientes** do dia.

## 🎯 O que faz

1. **Extrai** a lista completa de ações da B3 (single call à API Brapi)
2. **Valida** cada registro com Pydantic (Data Contracts — rejeita dados corrompidos)
3. **Higieniza** removendo empresas com prejuízo (P/L ≤ 0), sem retorno (ROE ≤ 0) ou ilíquidas (Volume < R$ 1M)
4. **Rankeia** usando a Magic Formula de Greenblatt (50% P/L + 50% ROE)
5. **Persiste** o ranking completo em CSV e o Top 3 em SQLite (via SQLAlchemy ORM)
6. **Exibe** o Top 3 formatado no terminal

## 🏗️ Arquitetura

```
src/
├── config.py          # Configuração centralizada (.env)
├── models.py          # Pydantic Data Contracts (AcaoSchema)
├── database.py        # SQLAlchemy ORM (modelo Ranking)
├── etl/
│   ├── extract.py     # GET /api/quote/list → JSON cru
│   ├── transform.py   # Pydantic → Pandas → Magic Formula
│   └── load.py        # CSV + SQLite (UPSERT)
└── main.py            # Orquestrador ETL
```

## 🚀 Como Rodar

### 1. Clone e instale

```bash
git clone <repo-url>
cd b3-factor-investing
pip install -r requirements.txt
```

### 2. Configure o token

```bash
cp .env.example .env
# Edite .env e coloque seu token da Brapi
# Crie um gratuito em: https://brapi.dev/dashboard
```

### 3. Execute

```bash
python -m src.main
```

### 4. Testes

```bash
python -m pytest tests/ -v
```

## 📋 Exemplo de Output

```
========================================================================
  B3 FACTOR INVESTING — TOP 3 (2026-08-24)
========================================================================
  Rank   Ticker       P/L        ROE         Volume    Score
------------------------------------------------------------------------
  1      XPTO3       4.20      28.5%      5.200.000      12
  2      ABCD4       5.10      25.3%      3.800.000      15
  3      EFGH3       3.80      22.1%      2.100.000      18
========================================================================
  Score = Rank P/L + Rank ROE (menor = melhor)
  Filtros: P/L > 0 | ROE > 0 | Volume ≥ R$ 1.000.000
========================================================================
```

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| Requisições | `requests` | Consumo da API Brapi |
| Validação | `pydantic` | Data Contracts (bloqueio de dados corrompidos) |
| Manipulação | `pandas` | Higienização e ranking matemático |
| Persistência | `sqlalchemy` | ORM para SQLite (pronto para PostgreSQL) |
| Configuração | `python-dotenv` | Gestão segura do token da API |
| Testes | `pytest` | Testes unitários da transformação |

## 📐 Regra de Negócio — Magic Formula

O ranking combina dois fatores com **pesos iguais (50% + 50%)**:

| Fator | Indicador | Lógica |
|-------|-----------|--------|
| **Value** (Preço) | P/L (Price to Earnings) | Menor P/L = ação mais barata → melhor |
| **Quality** (Qualidade) | ROE (Return on Equity) | Maior ROE = empresa mais lucrativa → melhor |

**Score** = Rank P/L + Rank ROE → **menor soma = melhor ativo**

### Filtros de Higienização
- ❌ P/L ≤ 0 (empresas com prejuízo)
- ❌ ROE ≤ 0 (empresas sem retorno positivo)
- ❌ Volume < R$ 1.000.000 (ações "zumbis" sem liquidez)

## 🗺️ Roadmap — Fase 2

- [ ] PostgreSQL na nuvem (Supabase/Neon) — trocar 1 linha no `database.py`
- [ ] GitHub Actions para execução automática pós-pregão
- [ ] Power BI conectado ao PostgreSQL para análise histórica
- [ ] Mais fatores: Dividend Yield, P/VP, margem EBITDA

## 📄 Licença

MIT
