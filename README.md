# B3 Factor Investing

Projeto de análise e ranking de ativos da B3 baseado em fatores de **Value** e **Quality**.

## Como Rodar

### 1. Clone o repositório e instale as dependências

```bash
git clone <repo-url>
cd b3-factor-investing
pip install -r requirements.txt
````

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Adicione seu token da **BRAPI** (`brapi.dev`) no arquivo `.env`.

### 3. Execute o pipeline de dados

```bash
python -m src.main
```

### 4. Execute o dashboard

```bash
streamlit run dashboard.py
```

### 5. Execute os testes

```bash
pytest tests/ -v
```

## Regras de Negócio

O ranking dos ativos combina dois fatores, com **peso de 50% para cada fator**:

* **Value:** menor P/L (Price-to-Earnings).
* **Quality:** maior ROE (Return on Equity).

### Cálculo do Score

O ranking de cada fator é calculado separadamente:

```text
Score = Rank(P/L) + Rank(ROE)
```

O ativo com a **menor pontuação total** ocupa a primeira posição no ranking.

### Filtros de Exclusão

Antes da aplicação do ranking, são excluídos os ativos que atendam a qualquer uma das seguintes condições:

* P/L menor ou igual a zero;
* ROE menor ou igual a zero;
* Volume médio diário de negociação inferior a **R$ 1.000.000,00**.

## Stack Tecnológica

| Categoria              | Tecnologia      |
| ---------------------- | --------------- |
| Extração de dados      | `requests`      |
| Validação e contratos  | `pydantic`      |
| Processamento de dados | `pandas`        |
| Banco de dados         | `SQLite`        |
| ORM                    | `SQLAlchemy`    |
| Dashboard              | `Streamlit`     |
| Visualização           | `Matplotlib`    |
| Testes                 | `pytest`        |
| Variáveis de ambiente  | `python-dotenv` |

## Licença

Este projeto está licenciado sob a licença **MIT**.
