│   │   ├── extract.py
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
2. Configure a variável de ambiente:
```bash
cp .env.example .env
# Adicione seu token da Brapi (brapi.dev) no arquivo .env
```
3. Execute o pipeline de dados:
```bash
python -m src.main
```
4. Execute o painel de visualização:
```bash
python -m streamlit run dashboard.py
```
5. Execute a suíte de testes:
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
- Extratores: requests
- Contratos e Validação: pydantic
- Processamento Numérico: pandas
- Banco de Dados e ORM: sqlalchemy, sqlite3
- Interface Gráfica: streamlit, matplotlib
- Testes: pytest
- Gestão de Ambiente: python-dotenv
## Licença
MIT
