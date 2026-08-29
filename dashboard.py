import streamlit as st
import pandas as pd
import sqlite3
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(page_title="B3 Factor Screener", layout="wide")
st.markdown(
    "\n    <style>\n    .stDataFrame { font-family: 'Inter', 'Helvetica Neue', sans-serif; }\n    div[data-testid=\"stMetricValue\"] { color: #C8A24B; }\n    </style>\n",
    unsafe_allow_html=True,
)
st.title("B3 Factor Investing: Magic Formula Screener")
st.markdown(
    "Triagem quantitativa combinando Value (P/L) e Quality (ROE) em um único Score."
)
st.divider()
GOLD_BASE = "#C8A24B"
DARK_BG = "#0B0B0D"
cmap_gold = LinearSegmentedColormap.from_list("btg_gold", [DARK_BG, GOLD_BASE])
cmap_gold_r = LinearSegmentedColormap.from_list("btg_gold_r", [GOLD_BASE, DARK_BG])
st.subheader("01 / Top 3 Ativos")
db_path = "output/b3_factor.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    df_top3 = pd.read_sql_query(
        "SELECT * FROM rankings ORDER BY date DESC, rank ASC", conn
    )
    conn.close()
    df_top3 = df_top3.rename(
        columns={
            "date": "Data",
            "rank": "Rank",
            "symbol": "Ativo",
            "price_earnings": "P/L",
            "return_on_equity": "ROE",
            "volume": "Volume R$",
            "combined_score": "Score",
        }
    )
    styled_top3 = (
        df_top3.style.format(
            {
                "P/L": "{:.2f}",
                "ROE": "{:.2%}",
                "Volume R$": "{:,.0f}",
                "Score": "{:.1f}",
            }
        )
        .background_gradient(subset=["ROE"], cmap=cmap_gold, vmin=0)
        .background_gradient(subset=["P/L"], cmap=cmap_gold_r)
        .set_properties(**{"text-align": "right", "border": "1px solid #26262B"})
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("text-align", "right"),
                        ("border-bottom", "1px solid #C8A24B"),
                    ],
                }
            ]
        )
    )
    st.dataframe(styled_top3, use_container_width=True, hide_index=True)
else:
    st.caption("Banco de dados SQLite não encontrado.")
st.divider()
st.subheader("02 / Ranking Completo")
csv_files = glob.glob("output/ranking_*.csv")
if csv_files:
    latest_csv = max(csv_files, key=os.path.getctime)
    df_full = pd.read_csv(latest_csv, sep=";")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        df_view = df_full.rename(
            columns={
                "rank": "Rank",
                "symbol": "Ativo",
                "priceEarnings": "P/L",
                "returnOnEquity": "ROE",
                "volume": "Volume",
                "combined_score": "Score",
            }
        )
        styled_full = (
            df_view.style.format(
                {
                    "P/L": "{:.2f}",
                    "ROE": "{:.2%}",
                    "Volume": "{:,.0f}",
                    "Score": "{:.1f}",
                }
            )
            .bar(subset=["Score"], color="#8B4513", vmin=0)
            .background_gradient(subset=["ROE"], cmap=cmap_gold)
            .set_properties(
                **{"text-align": "right", "border-bottom": "1px solid #26262B"}
            )
        )
        st.dataframe(styled_full, use_container_width=True, hide_index=True, height=500)
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(DARK_BG)
        ax.set_facecolor(DARK_BG)
        scatter = ax.scatter(
            df_full["priceEarnings"],
            df_full["returnOnEquity"] * 100,
            s=df_full["volume"] / 100000,
            c=GOLD_BASE,
            alpha=0.6,
            edgecolors="#F5F5F4",
            linewidths=0.5,
        )
        ax.grid(color="#26262B", linestyle="-", linewidth=0.5)
        ax.spines["bottom"].set_color("#26262B")
        ax.spines["left"].set_color("#26262B")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors="#6B7280", labelsize=9)
        ax.set_xlabel("P/L (Value)", color="#6B7280", fontsize=10, loc="right")
        ax.set_ylabel("ROE % (Quality)", color="#6B7280", fontsize=10, loc="top")
        median_pl = df_full["priceEarnings"].median()
        median_roe = df_full["returnOnEquity"].median() * 100
        ax.axvline(median_pl, color="#C8A24B", linestyle="--", linewidth=0.5, alpha=0.5)
        ax.axhline(
            median_roe, color="#C8A24B", linestyle="--", linewidth=0.5, alpha=0.5
        )
        ax.annotate(
            "Opportunity Zone\n(Low P/L, High ROE)",
            xy=(0.95, 0.05),
            xycoords="axes fraction",
            color="#C8A24B",
            fontsize=9,
            ha="right",
            va="bottom",
            alpha=0.8,
        )
        st.pyplot(fig)
