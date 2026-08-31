import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import glob
import os
import urllib.parse
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import html as html_module
from datetime import datetime


st.set_page_config(
    page_title="B3 Factor Investing | Equity Ranking",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ───────────────────────────────────────────────── */
    html, body, [class*="css"], .stMarkdown, .stText, p, span, div, td, th, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    /* ── Header ───────────────────────────────────────────────── */
    .report-header {
        border-bottom: 3px solid #1E3A5F;
        padding-bottom: 1.25rem;
        margin-bottom: 0.25rem;
    }
    .report-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1A1A2E;
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.15;
    }
    .report-subtitle {
        font-size: 0.875rem;
        color: #6B7280;
        margin-top: 0.4rem;
        font-weight: 400;
        line-height: 1.5;
    }
    .report-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-top: 0.75rem;
        font-size: 0.78rem;
        color: #6B7280;
    }
    .report-meta-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .meta-label {
        font-weight: 700;
        color: #1E3A5F;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* ── Section Titles ───────────────────────────────────────── */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E3A5F;
        border-left: 4px solid #1E3A5F;
        padding-left: 0.75rem;
        margin-top: 2rem;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
    }
    .section-desc {
        font-size: 0.82rem;
        color: #6B7280;
        margin-bottom: 1rem;
        line-height: 1.55;
    }

    /* ── KPI Metrics ──────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #F7F8FA;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 0.85rem 1rem;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #6B7280 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #1A1A2E !important;
        font-variant-numeric: tabular-nums !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    /* ── Corporate Table ──────────────────────────────────────── */
    .corp-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        font-variant-numeric: tabular-nums;
        margin-top: 0.5rem;
    }
    .corp-table thead th {
        background: #1E3A5F;
        color: #FFFFFF;
        font-weight: 600;
        padding: 0.65rem 0.55rem;
        text-align: left;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border: none;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .corp-table thead th.r { text-align: right; }
    .corp-table thead th.c { text-align: center; }
    .corp-table tbody td {
        padding: 0.55rem 0.55rem;
        border-bottom: 1px solid #EAEDF0;
        color: #1A1A2E;
        vertical-align: middle;
        line-height: 1.3;
    }
    .corp-table tbody td.r {
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    .corp-table tbody td.c {
        text-align: center;
    }
    .corp-table tbody tr:hover {
        background: #F0F4F8;
    }
    .corp-table .row-top {
        background: #F4F8F6;
    }
    .corp-table .row-top:hover {
        background: #E8F0EC;
    }

    /* ── Rank Badge ───────────────────────────────────────────── */
    .rk {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.75rem;
        height: 1.75rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .rk-1 { background: #1E3A5F; color: #fff; }
    .rk-2 { background: #2D5F8A; color: #fff; }
    .rk-3 { background: #4A7FB5; color: #fff; }
    .rk-n { background: #E5E7EB; color: #1A1A2E; }

    /* ── Score Bar ────────────────────────────────────────────── */
    .score-wrap {
        display: flex; align-items: center; gap: 0.4rem;
    }
    .score-bar {
        width: 60px; height: 5px; background: #E5E7EB;
        border-radius: 3px; overflow: hidden;
    }
    .score-fill {
        height: 100%; border-radius: 3px;
    }
    .score-val { font-weight: 700; font-size: 0.82rem; }

    /* ── Variation ────────────────────────────────────────────── */
    .v-pos { color: #0D7C3E; font-weight: 600; }
    .v-neg { color: #D32F2F; font-weight: 600; }
    .v-nil { color: #9CA3AF; }

    /* ── Company Name ─────────────────────────────────────────── */
    .co-name {
        font-weight: 600;
        color: #1A1A2E;
        font-size: 0.82rem;
    }
    .co-ticker {
        font-size: 0.72rem;
        color: #6B7280;
        font-weight: 500;
    }

    /* ── Insight Card ─────────────────────────────────────────── */
    .insight {
        background: #F7F8FA;
        border-left: 4px solid #1E3A5F;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.6rem;
        font-size: 0.84rem;
        line-height: 1.6;
        color: #374151;
        border-radius: 0 4px 4px 0;
    }
    .insight strong { color: #1E3A5F; }
    .insight-warn {
        border-left-color: #D4A017;
    }
    .insight-neg {
        border-left-color: #D32F2F;
    }

    /* ── Analysis Box ─────────────────────────────────────────── */
    .analysis-box {
        background: #F7F8FA;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 1.25rem;
    }
    .analysis-hdr {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 0.75rem;
    }
    .analysis-co {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1A1A2E;
    }
    .analysis-rk {
        font-size: 0.8rem;
        font-weight: 700;
        color: #fff;
        background: #1E3A5F;
        padding: 0.25rem 0.7rem;
        border-radius: 4px;
    }
    .analysis-row {
        display: flex;
        justify-content: space-between;
        padding: 0.45rem 0;
        border-bottom: 1px solid #F0F0F0;
        font-size: 0.84rem;
    }
    .analysis-lbl { color: #6B7280; }
    .analysis-val {
        font-weight: 600;
        color: #1A1A2E;
        font-variant-numeric: tabular-nums;
    }
    .pt-pos { color: #0D7C3E; font-size: 0.82rem; padding: 0.2rem 0; }
    .pt-neg { color: #D32F2F; font-size: 0.82rem; padding: 0.2rem 0; }

    /* ── Score Explanation ─────────────────────────────────────── */
    .formula-box {
        background: #F7F8FA;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 1.1rem 1.25rem;
        text-align: center;
        margin: 0.75rem 0;
    }
    .formula-main {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.35rem;
    }
    .formula-sub {
        font-size: 0.8rem;
        color: #6B7280;
        line-height: 1.5;
    }
    .factor-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 0.9rem;
    }
    .factor-name {
        font-weight: 700;
        color: #1E3A5F;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    .factor-desc {
        font-size: 0.78rem;
        color: #6B7280;
        line-height: 1.5;
    }

    /* ── Glossary ──────────────────────────────────────────────── */
    .gloss-item {
        display: flex;
        gap: 0.75rem;
        padding: 0.55rem 0;
        border-bottom: 1px solid #F0F0F0;
        font-size: 0.82rem;
    }
    .gloss-term {
        font-weight: 700;
        color: #1E3A5F;
        min-width: 140px;
        flex-shrink: 0;
    }
    .gloss-def {
        color: #6B7280;
        line-height: 1.5;
    }

    /* ── Divider ───────────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }

    /* ── Scrollable table wrapper ──────────────────────────────── */
    .table-scroll {
        max-height: 650px;
        overflow-y: auto;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
    }
    .table-scroll::-webkit-scrollbar { width: 6px; }
    .table-scroll::-webkit-scrollbar-track { background: #F7F8FA; }
    .table-scroll::-webkit-scrollbar-thumb { background: #C4C9D1; border-radius: 3px; }
    .table-scroll::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

    /* ── Hide default streamlit elements ───────────────────────── */
    .stDeployButton { display: none; }
    div[data-testid="stDecoration"] { display: none; }

    /* ── Expander ──────────────────────────────────────────────── */
    details summary {
        font-weight: 600;
        color: #1E3A5F;
        cursor: pointer;
    }

</style>
""", unsafe_allow_html=True)



def fmt_brl(val):
    """Formata número no padrão brasileiro (1.234.567)."""
    if pd.isna(val):
        return "—"
    s = f"{val:,.0f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(val, decimals=2):
    """Formata percentual com sinal."""
    if pd.isna(val):
        return "—"
    sign = "+" if val > 0 else ""
    return f"{sign}{val * 100:.{decimals}f}%"


def fmt_pl(val):
    """Formata P/L."""
    if pd.isna(val):
        return "—"
    return f"{val:.1f}x"


def fmt_roe(val):
    """Formata ROE como percentual."""
    if pd.isna(val):
        return "—"
    return f"{val * 100:.1f}%"


def var_class(val):
    """Retorna classe CSS para variação."""
    if pd.isna(val) or val == 0:
        return "v-nil"
    return "v-pos" if val > 0 else "v-neg"


def rank_class(rank):
    """Retorna classe CSS para badge de rank."""
    if rank <= 3:
        return f"rk-{rank}"
    return "rk-n"


def score_color(score, min_score, max_score):
    """Retorna cor para barra de score (invertida: menor = melhor)."""
    if max_score == min_score:
        return "#1E3A5F"
    ratio = (score - min_score) / (max_score - min_score)
    if ratio <= 0.2:
        return "#0D7C3E"  
    elif ratio <= 0.4:
        return "#1E3A5F"  
    elif ratio <= 0.6:
        return "#D4A017"  
    elif ratio <= 0.8:
        return "#E07C24"  
    return "#D32F2F"      


def score_width(score, min_score, max_score):
    """Retorna largura % da barra de score (invertida: menor score = barra maior)."""
    if max_score == min_score:
        return 100
    return max(5, 100 - int(((score - min_score) / (max_score - min_score)) * 100))


def escape(text):
    """Escapa HTML."""
    return html_module.escape(str(text))




csv_files = glob.glob("output/ranking_*.csv")

if not csv_files:
    st.warning("Nenhum dado encontrado. Execute o pipeline primeiro com `python -m src.main`.")
    st.stop()

latest_csv = max(csv_files, key=os.path.getctime)
df = pd.read_csv(latest_csv, sep=";")

csv_date_str = os.path.basename(latest_csv).replace("ranking_", "").replace(".csv", "")
try:
    csv_date = datetime.strptime(csv_date_str, "%Y-%m-%d")
    date_display = csv_date.strftime("%d/%m/%Y")
except ValueError:
    date_display = csv_date_str

def get_avatar(row):
    dominio = row.get("website_domain", "")
    if pd.notna(dominio) and str(dominio).strip() != "":
        return f"https://logo.clearbit.com/{dominio}"
    name = row.get("companyName") or row.get("symbol")
    safe_name = urllib.parse.quote(str(name))
    return f"https://ui-avatars.com/api/?name={safe_name}&background=random&color=fff&rounded=true&size=128"

if "companyName" in df.columns:
    df["Logo"] = df.apply(get_avatar, axis=1)
else:
    df["Logo"] = df["symbol"].apply(get_avatar)
    df["companyName"] = df["symbol"]
    df["dailyChange"] = 0.0

total_empresas = len(df)
min_score = df["combined_score"].min()
max_score = df["combined_score"].max()
median_pl = df["priceEarnings"].median()
median_roe = df["returnOnEquity"].median()
mean_change = df["dailyChange"].mean()

empresa_lider = df.loc[df["rank"] == 1].iloc[0]
empresa_pior = df.loc[df["rank"] == df["rank"].max()].iloc[0]

top5 = df[df["rank"] <= 5]
bottom5 = df[df["rank"] > total_empresas - 5]

positivas_hoje = len(df[df["dailyChange"] > 0])
negativas_hoje = len(df[df["dailyChange"] < 0])


st.markdown(f"""
<div class="report-header">
    <div class="report-title">Ranking Ibovespa — {date_display}</div>
    <div class="report-subtitle">
        {total_empresas} empresas · P/L &gt; 0 · ROE &gt; 0 · Volume ≥ R$ 1M · Score = Rank P/L + Rank ROE
    </div>
</div>
""", unsafe_allow_html=True)



st.markdown('<div class="section-title">Resumo Executivo</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Visão geral do ranking atual. '
    'Métricas principais para avaliação rápida do cenário.</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Empresas Analisadas",
        value=str(total_empresas),
    )
with col2:
    st.metric(
        label="Líder do Ranking",
        value=str(empresa_lider["symbol"]),
        delta=f"Score {int(empresa_lider['combined_score'])}",
    )
with col3:
    st.metric(
        label="Pior Classificada",
        value=str(empresa_pior["symbol"]),
        delta=f"Score {int(empresa_pior['combined_score'])}",
        delta_color="inverse",
    )
with col4:
    st.metric(
        label="Em Alta Hoje",
        value=f"{positivas_hoje}",
        delta=f"de {total_empresas}",
        delta_color="off",
    )
with col5:
    st.metric(
        label="Variação Média",
        value=fmt_pct(mean_change),
        delta_color="off",
    )




st.markdown('<div class="section-title">Ranking de Ações</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Classificação completa das empresas por score multifatorial. '
    'Quanto menor o score, melhor a combinação de valuation atrativo (P/L baixo) e '
    'alta rentabilidade (ROE elevado). Ordenado do melhor para o pior.</div>',
    unsafe_allow_html=True,
)

table_rows = []
for _, row in df.iterrows():
    rank = int(row["rank"])
    symbol = escape(str(row["symbol"]))
    company = escape(str(row["companyName"]))
    score = row["combined_score"]
    pl = row["priceEarnings"]
    roe = row["returnOnEquity"]
    volume = row["volume"]
    change = row["dailyChange"]

    rk_cls = rank_class(rank)
    row_cls = "row-top" if rank <= 5 else ""
    v_cls = var_class(change)

    s_color = score_color(score, min_score, max_score)
    s_width = score_width(score, min_score, max_score)

    table_rows.append(f"""
    <tr class="{row_cls}">
        <td class="c"><span class="rk {rk_cls}">{rank}</span></td>
        <td>
            <div class="co-name">{company}</div>
            <div class="co-ticker">{symbol}</div>
        </td>
        <td class="r">
            <div class="score-wrap">
                <span class="score-val">{int(score)}</span>
                <div class="score-bar">
                    <div class="score-fill" style="width:{s_width}%;background:{s_color};"></div>
                </div>
            </div>
        </td>
        <td class="r">{fmt_pl(pl)}</td>
        <td class="r">{fmt_roe(roe)}</td>
        <td class="r"><span class="{v_cls}">{fmt_pct(change)}</span></td>
        <td class="r">R$ {fmt_brl(volume)}</td>
    </tr>
    """)

table_body = ''.join(table_rows)

_table_h = min(700, 44 + len(df) * 42 + 8)

table_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: transparent;
        overflow-x: hidden;
    }}
    .table-scroll {{
        max-height: {_table_h}px;
        overflow-y: auto;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
    }}
    .table-scroll::-webkit-scrollbar {{ width: 6px; }}
    .table-scroll::-webkit-scrollbar-track {{ background: #F7F8FA; }}
    .table-scroll::-webkit-scrollbar-thumb {{ background: #C4C9D1; border-radius: 3px; }}
    .table-scroll::-webkit-scrollbar-thumb:hover {{ background: #9CA3AF; }}
    .corp-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        font-variant-numeric: tabular-nums;
    }}
    .corp-table thead th {{
        background: #1E3A5F;
        color: #FFFFFF;
        font-weight: 600;
        padding: 0.65rem 0.55rem;
        text-align: left;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border: none;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 10;
    }}
    .corp-table thead th.r {{ text-align: right; }}
    .corp-table thead th.c {{ text-align: center; }}
    .corp-table tbody td {{
        padding: 0.55rem 0.55rem;
        border-bottom: 1px solid #EAEDF0;
        color: #1A1A2E;
        vertical-align: middle;
        line-height: 1.3;
    }}
    .corp-table tbody td.r {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .corp-table tbody td.c {{ text-align: center; }}
    .corp-table tbody tr:hover {{ background: #F0F4F8; }}
    .corp-table .row-top {{ background: #F4F8F6; }}
    .corp-table .row-top:hover {{ background: #E8F0EC; }}
    .rk {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 1.75rem; height: 1.75rem; border-radius: 4px;
        font-weight: 700; font-size: 0.8rem;
    }}
    .rk-1 {{ background: #1E3A5F; color: #fff; }}
    .rk-2 {{ background: #2D5F8A; color: #fff; }}
    .rk-3 {{ background: #4A7FB5; color: #fff; }}
    .rk-n {{ background: #E5E7EB; color: #1A1A2E; }}
    .score-wrap {{ display: flex; align-items: center; gap: 0.4rem; }}
    .score-bar {{ width: 60px; height: 5px; background: #E5E7EB; border-radius: 3px; overflow: hidden; }}
    .score-fill {{ height: 100%; border-radius: 3px; }}
    .score-val {{ font-weight: 700; font-size: 0.82rem; }}
    .v-pos {{ color: #0D7C3E; font-weight: 600; }}
    .v-neg {{ color: #D32F2F; font-weight: 600; }}
    .v-nil {{ color: #9CA3AF; }}
    .co-name {{ font-weight: 600; color: #1A1A2E; font-size: 0.82rem; }}
    .co-ticker {{ font-size: 0.72rem; color: #6B7280; font-weight: 500; }}
</style>
</head>
<body>
<div class="table-scroll">
<table class="corp-table">
    <thead>
        <tr>
            <th class="c" style="width:55px;">Pos.</th>
            <th style="min-width:180px;">Empresa</th>
            <th class="r" style="width:130px;">Score</th>
            <th class="r" style="width:75px;">P/L</th>
            <th class="r" style="width:75px;">ROE</th>
            <th class="r" style="width:90px;">Hoje</th>
            <th class="r" style="width:130px;">Volume</th>
        </tr>
    </thead>
    <tbody>
        {table_body}
    </tbody>
</table>
</div>
</body>
</html>
"""
components.html(table_html, height=_table_h + 10, scrolling=False)


st.markdown('<div class="section-title">Como o Score é Calculado</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">O score geral é uma combinação dos rankings individuais de cada indicador. '
    'Quanto menor o score, melhor posicionada está a empresa no modelo.</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="formula-box">
    <div class="formula-main">Score = Rank P/L + Rank ROE</div>
    <div class="formula-sub">
        Cada empresa recebe uma posição (rank) em P/L e em ROE separadamente.<br>
        O score final é a soma desses dois ranks. <strong>Menor score = melhor oportunidade.</strong>
    </div>
</div>
""", unsafe_allow_html=True)

fc1, fc2 = st.columns(2)
with fc1:
    st.markdown("""
    <div class="factor-box">
        <div class="factor-name">P/L — Preço sobre Lucro</div>
        <div class="factor-desc">
            Mede quanto o mercado paga por cada real de lucro da empresa.
            <strong>Quanto menor, mais "barata" a ação</strong> em relação ao lucro que ela gera.
            Uma empresa com P/L 5 significa que o investidor paga R$ 5 por cada R$ 1 de lucro anual.
            No ranking, empresas com P/L mais baixo recebem posições melhores (rank menor).
        </div>
    </div>
    """, unsafe_allow_html=True)
with fc2:
    st.markdown("""
    <div class="factor-box">
        <div class="factor-name">ROE — Retorno sobre Patrimônio</div>
        <div class="factor-desc">
            Mede a eficiência da empresa em gerar lucro com o capital dos acionistas.
            <strong>Quanto maior, mais lucrativa e eficiente.</strong>
            Um ROE de 30% significa que a empresa gera R$ 0,30 de lucro para cada R$ 1,00 de patrimônio.
            No ranking, empresas com ROE mais alto recebem posições melhores (rank menor).
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">Análise Individual</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Selecione uma empresa para visualizar seus indicadores detalhados, '
    'pontos fortes e fracos identificados pelo modelo.</div>',
    unsafe_allow_html=True,
)

opcoes = [f"#{int(r['rank'])} — {r['symbol']} ({r['companyName']})" for _, r in df.iterrows()]
selecionada = st.selectbox("Selecione a empresa", opcoes, label_visibility="collapsed")

if selecionada:
    idx = opcoes.index(selecionada)
    emp = df.iloc[idx]

    rank_emp = int(emp["rank"])
    score_emp = int(emp["combined_score"])
    pl_emp = emp["priceEarnings"]
    roe_emp = emp["returnOnEquity"]
    vol_emp = emp["volume"]
    change_emp = emp["dailyChange"]
    name_emp = escape(str(emp["companyName"]))
    symbol_emp = escape(str(emp["symbol"]))

    percentil = ((total_empresas - rank_emp) / total_empresas) * 100

    pontos_pos = []
    pontos_neg = []

    if pl_emp < median_pl:
        pontos_pos.append(f"P/L de {fmt_pl(pl_emp)} está abaixo da mediana do grupo ({fmt_pl(median_pl)}), indicando valuation relativamente atrativo.")
    else:
        pontos_neg.append(f"P/L de {fmt_pl(pl_emp)} está acima da mediana do grupo ({fmt_pl(median_pl)}), indicando valuation relativamente caro.")

    if roe_emp > median_roe:
        pontos_pos.append(f"ROE de {fmt_roe(roe_emp)} está acima da mediana ({fmt_roe(median_roe)}), indicando boa rentabilidade.")
    else:
        pontos_neg.append(f"ROE de {fmt_roe(roe_emp)} está abaixo da mediana ({fmt_roe(median_roe)}), indicando rentabilidade inferior à maioria.")

    if change_emp > 0:
        pontos_pos.append(f"Variação positiva de {fmt_pct(change_emp)} no dia.")
    elif change_emp < 0:
        pontos_neg.append(f"Variação negativa de {fmt_pct(change_emp)} no dia.")

    if rank_emp <= 5:
        pontos_pos.append(f"Está entre as 5 melhores posições do ranking (Top {percentil:.0f}%).")
    elif rank_emp <= 10:
        pontos_pos.append(f"Está entre as 10 melhores posições do ranking (Top {percentil:.0f}%).")
    elif rank_emp > total_empresas * 0.75:
        pontos_neg.append(f"Está no quartil inferior do ranking (posição {rank_emp} de {total_empresas}).")

    ac1, ac2 = st.columns([1, 1])

    with ac1:
        var_html_class = var_class(change_emp)
        st.markdown(f"""
        <div class="analysis-box">
            <div class="analysis-hdr">
                <div>
                    <div class="analysis-co">{name_emp}</div>
                    <div class="co-ticker">{symbol_emp}</div>
                </div>
                <div class="analysis-rk">#{rank_emp} de {total_empresas}</div>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Score Geral</span>
                <span class="analysis-val">{score_emp} pontos</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Percentil</span>
                <span class="analysis-val">Top {percentil:.0f}%</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Preço / Lucro (P/L)</span>
                <span class="analysis-val">{fmt_pl(pl_emp)}</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Retorno sobre Patrimônio (ROE)</span>
                <span class="analysis-val">{fmt_roe(roe_emp)}</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Volume Médio Diário</span>
                <span class="analysis-val">R$ {fmt_brl(vol_emp)}</span>
            </div>
            <div class="analysis-row">
                <span class="analysis-lbl">Variação do Dia</span>
                <span class="analysis-val {var_html_class}">{fmt_pct(change_emp)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ac2:
        pos_html = ""
        neg_html = ""
        for p in pontos_pos:
            pos_html += f'<div class="pt-pos">✓ {escape(p)}</div>'
        for n in pontos_neg:
            neg_html += f'<div class="pt-neg">✗ {escape(n)}</div>'

        st.markdown(f"""
        <div class="analysis-box">
            <div style="font-weight:700;color:#1E3A5F;margin-bottom:0.75rem;font-size:0.9rem;">
                Diagnóstico do Modelo
            </div>
            {f'<div style="font-weight:600;color:#0D7C3E;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.35rem;">Pontos Favoráveis</div>{pos_html}' if pontos_pos else ''}
            {f'<div style="font-weight:600;color:#D32F2F;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em;margin-top:0.75rem;margin-bottom:0.35rem;">Pontos de Atenção</div>{neg_html}' if pontos_neg else ''}
        </div>
        """, unsafe_allow_html=True)


st.markdown('<div class="section-title">Insights Executivos</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Principais observações derivadas automaticamente dos dados do ranking atual. '
    'Todas as afirmações são sustentáveis pelos indicadores disponíveis.</div>',
    unsafe_allow_html=True,
)

lider_name = escape(str(empresa_lider["companyName"]))
lider_sym = escape(str(empresa_lider["symbol"]))
lider_score = int(empresa_lider["combined_score"])
lider_pl = empresa_lider["priceEarnings"]
lider_roe = empresa_lider["returnOnEquity"]
st.markdown(
    f'<div class="insight"><strong>{lider_sym} ({lider_name})</strong> lidera o ranking com score '
    f'<strong>{lider_score}</strong>, combinando P/L de {fmt_pl(lider_pl)} e ROE de '
    f'{fmt_roe(lider_roe)}. Isso indica uma empresa com valuation atrativo e alta rentabilidade.</div>',
    unsafe_allow_html=True,
)

top5_names = ", ".join([f"<strong>{escape(str(r['symbol']))}</strong>" for _, r in top5.iterrows()])
st.markdown(
    f'<div class="insight">As 5 empresas melhor posicionadas são: {top5_names}. '
    f'Todas apresentam combinação favorável de valuation e rentabilidade no modelo.</div>',
    unsafe_allow_html=True,
)

if positivas_hoje > negativas_hoje:
    st.markdown(
        f'<div class="insight">{positivas_hoje} de {total_empresas} empresas ({positivas_hoje/total_empresas*100:.0f}%) '
        f'registraram variação positiva no dia, com média geral de <strong>{fmt_pct(mean_change)}</strong>.</div>',
        unsafe_allow_html=True,
    )
elif negativas_hoje > positivas_hoje:
    st.markdown(
        f'<div class="insight insight-warn">{negativas_hoje} de {total_empresas} empresas ({negativas_hoje/total_empresas*100:.0f}%) '
        f'registraram variação negativa no dia, com média geral de <strong>{fmt_pct(mean_change)}</strong>.</div>',
        unsafe_allow_html=True,
    )

maior_alta = df.loc[df["dailyChange"].idxmax()]
maior_queda = df.loc[df["dailyChange"].idxmin()]

if maior_alta["dailyChange"] > 0:
    st.markdown(
        f'<div class="insight">A maior valorização do dia foi de <strong>{escape(str(maior_alta["symbol"]))}</strong> '
        f'(<strong>{fmt_pct(maior_alta["dailyChange"])}</strong>), posição #{int(maior_alta["rank"])} no ranking.</div>',
        unsafe_allow_html=True,
    )

if maior_queda["dailyChange"] < 0:
    st.markdown(
        f'<div class="insight insight-neg">A maior desvalorização do dia foi de <strong>{escape(str(maior_queda["symbol"]))}</strong> '
        f'(<strong>{fmt_pct(maior_queda["dailyChange"])}</strong>), posição #{int(maior_queda["rank"])} no ranking.</div>',
        unsafe_allow_html=True,
    )

pior_name = escape(str(empresa_pior["companyName"]))
pior_sym = escape(str(empresa_pior["symbol"]))
pior_pl = empresa_pior["priceEarnings"]
pior_roe = empresa_pior["returnOnEquity"]
st.markdown(
    f'<div class="insight insight-warn"><strong>{pior_sym} ({pior_name})</strong> ocupa a última posição '
    f'(#{int(empresa_pior["rank"])}) com P/L de {fmt_pl(pior_pl)} e ROE de {fmt_roe(pior_roe)}, '
    f'indicando combinação desfavorável de valuation elevado e baixa rentabilidade.</div>',
    unsafe_allow_html=True,
)




st.markdown('<div class="section-title">Mapa de Posicionamento</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Dispersão P/L × ROE das empresas analisadas. '
    'Empresas posicionadas no <strong>quadrante inferior direito</strong> '
    '(P/L baixo e ROE alto) representam as melhores combinações de valuation e rentabilidade. '
    'O tamanho do círculo representa o volume negociado. '
    'Verde indica alta no dia, vermelho indica queda.</div>',
    unsafe_allow_html=True,
)

fig, ax = plt.subplots(figsize=(11, 5.5))

ax.set_facecolor("#FFFFFF")
fig.patch.set_facecolor("#FFFFFF")

colors = ["#0D7C3E" if val > 0 else "#B0B8C4" if val == 0 else "#D32F2F" for val in df["dailyChange"]]
alphas = [0.7 if rank <= 10 else 0.45 for rank in df["rank"]]

for i, (_, row) in enumerate(df.iterrows()):
    ax.scatter(
        row["priceEarnings"],
        row["returnOnEquity"] * 100,
        s=max(row["volume"] / 400000, 30),
        c=colors[i],
        alpha=alphas[i],
        edgecolors="#FFFFFF",
        linewidths=0.8,
        zorder=3,
    )

for _, row in top5.iterrows():
    ax.annotate(
        row["symbol"],
        (row["priceEarnings"], row["returnOnEquity"] * 100),
        textcoords="offset points",
        xytext=(8, 4),
        fontsize=7.5,
        fontweight="bold",
        color="#1E3A5F",
        fontfamily="sans-serif",
        zorder=5,
    )

ax.grid(color="#EAEDF0", linestyle="-", linewidth=0.5, alpha=0.8)
ax.set_axisbelow(True)

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["bottom", "left"]:
    ax.spines[spine].set_color("#D1D5DB")
    ax.spines[spine].set_linewidth(0.8)

ax.set_xlabel("P/L — Preço / Lucro (menor = mais barato)", fontsize=9, fontweight="600", color="#374151", labelpad=8)
ax.set_ylabel("ROE — Retorno sobre Patrimônio (%)\n(maior = mais rentável)", fontsize=9, fontweight="600", color="#374151", labelpad=8)

ax.tick_params(axis="both", labelsize=8, colors="#6B7280", length=3)

median_pl_val = df["priceEarnings"].median()
median_roe_val = df["returnOnEquity"].median() * 100

ax.axvline(median_pl_val, color="#9CA3AF", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)
ax.axhline(median_roe_val, color="#9CA3AF", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)

ax.annotate(
    "Melhor combinação\nP/L baixo + ROE alto",
    xy=(0.02, 0.96),
    xycoords="axes fraction",
    color="#0D7C3E",
    fontsize=8,
    fontweight="bold",
    ha="left",
    va="top",
    bbox=dict(boxstyle="round,pad=0.4", fc="#F0FFF4", ec="#0D7C3E", lw=1, alpha=0.9),
    zorder=5,
)

ax.annotate(
    "Pior combinação\nP/L alto + ROE baixo",
    xy=(0.98, 0.04),
    xycoords="axes fraction",
    color="#D32F2F",
    fontsize=8,
    fontweight="bold",
    ha="right",
    va="bottom",
    bbox=dict(boxstyle="round,pad=0.4", fc="#FFF5F5", ec="#D32F2F", lw=1, alpha=0.9),
    zorder=5,
)

plt.tight_layout(pad=1.5)
st.pyplot(fig)
plt.close(fig)


st.markdown('<div class="section-title">Glossário de Indicadores</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-desc">Referência rápida dos termos e indicadores utilizados neste relatório.</div>',
    unsafe_allow_html=True,
)

glossario = [
    ("P/L (Preço/Lucro)", "Quanto o mercado paga por cada real de lucro. Menor = mais barata."),
    ("ROE", "Retorno sobre patrimônio. Mede eficiência em gerar lucro. Maior = melhor."),
    ("Volume", "Média diária negociada em reais. Indica liquidez do ativo."),
    ("Score", "Soma do rank P/L + rank ROE. Menor = melhor combinação."),
    ("Variação", "Mudança % do preço em relação ao fechamento anterior."),
    ("Ranking", "Posição no modelo. #1 = melhor combinação P/L + ROE."),
]

gloss_rows = ""
for term, definition in glossario:
    gloss_rows += f'<tr><td style="font-weight:700;color:#1E3A5F;padding:6px 12px 6px 0;white-space:nowrap;vertical-align:top;font-size:0.82rem;">{term}</td><td style="color:#6B7280;padding:6px 0;font-size:0.82rem;line-height:1.4;">{definition}</td></tr>'

gloss_html = f"""
<!DOCTYPE html><html><head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:transparent; }}
    table {{ border-collapse:collapse; width:100%; }}
    tr {{ border-bottom:1px solid #F0F0F0; }}
    tr:last-child {{ border-bottom:none; }}
</style>
</head><body>
<table>{gloss_rows}</table>
</body></html>
"""
components.html(gloss_html, height=len(glossario) * 34 + 10, scrolling=False)

st.markdown(
    f'<div style="border-top:1px solid #E5E7EB;margin-top:2rem;padding-top:1rem;text-align:center;font-size:0.72rem;color:#9CA3AF;">'
    f'B3 Factor Investing — Dados extraídos via Yahoo Finance (yfinance) · '
    f'Modelo: Rank P/L + Rank ROE · Atualizado em {date_display} · '
    f'Este relatório é gerado automaticamente e não constitui recomendação de investimento.'
    f'</div>',
    unsafe_allow_html=True,
)
