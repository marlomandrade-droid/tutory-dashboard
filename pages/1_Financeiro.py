"""
Painel Financeiro — Dashboard Tutory v2
Visao consolidada de receita HUB, Mentoria, Platinum e Renovacoes.
Design: cards grandes, graficos radiais compactos, header discreto.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# -- Imports internos --
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.auth import require_login
from utils.brand import (
    inject_custom_css, AZUL, LARANJA, GREEN, RED, YELLOW, PURPLE,
    CARD_BG, CARD_BG_HOVER, DIM, MUTED, BORDER, BG_DARK,
)
from utils.formatters import brl, brl_compact, num_br, pct, delta_pct
from utils.db import get_hub_connection, get_mentoria_connection
from utils.queries import (
    hub_gmv_acumulado_por_ano,
    hub_receita_mensal,
    hub_receita_ultimos_meses,
    hub_receita_breakdown_mensal,
    hub_gmv_mes_atual,
    hub_platinum_mensal,
    mentoria_receita_b2b_mensal,
    mentoria_receita_mes_atual,
    mentoria_renovacoes_mensal,
    mentoria_recorrencia_mensal,
    mentoria_planos_anuais_diferidos,
    mentoria_renovacoes_clientes_mes,
    mentoria_clientes_vencendo_mes,
    carregar_orcamento,
)

# -- Configuracao da pagina --
st.set_page_config(page_title="Financeiro — Tutory", page_icon="🧠", layout="wide")
inject_custom_css()

# -- Logo na sidebar --
logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "tutory_logo_nova_branca.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=180)
    st.sidebar.markdown("---")

# -- Auth --
require_login()

# -- Health check de conexoes (UMA VEZ, sem repetir) --
_hub_ok = get_hub_connection() is not None
_mentoria_ok = get_mentoria_connection() is not None

if not _hub_ok:
    st.error("❌ **Sem conexão com o HUB** (PostgreSQL) — dados do HUB indisponíveis.")
if not _mentoria_ok:
    st.warning(
        "⚠️ **Sem conexão com a Mentoria** (SQL Server) — dados de Mentoria indisponíveis.\n\n"
        "💡 Verifique se o IP está liberado no Security Group da AWS."
    )


# ══════════════════════════════════════════════════════
# CSS CUSTOMIZADO PARA O PAINEL FINANCEIRO
# ══════════════════════════════════════════════════════

st.markdown(f"""
<style>
/* ══ Cards grandes do painel financeiro ══ */
.fin-card {{
    background: linear-gradient(135deg, {CARD_BG}, {CARD_BG_HOVER});
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 8px;
}}
.fin-card-accent {{
    border-left: 4px solid;
}}
.fin-label {{
    font-family: 'Inter', sans-serif;
    color: {DIM};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 0 0 6px 0;
    font-weight: 700;
}}
.fin-value {{
    font-family: 'Inter', sans-serif;
    color: #e8e8f0;
    font-size: 36px;
    font-weight: 800;
    margin: 0 0 4px 0;
    line-height: 1.1;
    letter-spacing: -0.5px;
}}
.fin-value-sm {{
    font-family: 'Inter', sans-serif;
    color: #e8e8f0;
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 2px 0;
    line-height: 1.1;
}}
.fin-budget {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    margin: 6px 0 0 0;
}}
.fin-delta-up {{ color: {GREEN}; font-size: 13px; font-weight: 700; margin: 2px 0 0 0; font-family: 'Inter', sans-serif; }}
.fin-delta-down {{ color: {RED}; font-size: 13px; font-weight: 700; margin: 2px 0 0 0; font-family: 'Inter', sans-serif; }}
.fin-sub-label {{
    font-family: 'Inter', sans-serif;
    color: {MUTED};
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 2px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.fin-sub-value {{
    font-family: 'Inter', sans-serif;
    color: #c8c8e0;
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    white-space: nowrap;
}}
.section-title {{
    font-family: 'Inter', sans-serif;
    color: {DIM};
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 28px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid {BORDER};
}}
/* ══ Tags de status de clientes ══ */
.client-tag-ok {{
    background: rgba(0,214,143,0.12);
    color: {GREEN};
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}}
.client-tag-pending {{
    background: rgba(255,149,0,0.12);
    color: {YELLOW};
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}}
.client-tag-none {{
    background: rgba(255,107,107,0.12);
    color: {RED};
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# DADOS
# ══════════════════════════════════════════════════════

now = datetime.now()
MES_ATUAL = now.month
ANO_ATUAL = now.year
MESES_NOME = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
              7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

# Orcamento
orcamento = carregar_orcamento()

# HUB
df_gmv_anos = hub_gmv_acumulado_por_ano()
df_hub_meses = hub_receita_ultimos_meses(5)
df_hub_breakdown = hub_receita_breakdown_mensal(5)
df_hub_atual = hub_gmv_mes_atual()

# Platinum
df_platinum = hub_platinum_mensal(5)

# Mentoria
df_mentoria_meses = mentoria_receita_b2b_mensal(5)
df_mentoria_atual = mentoria_receita_mes_atual()
df_renovacoes = mentoria_renovacoes_mensal(5)
df_recorrencia = mentoria_recorrencia_mensal()
df_anuais = mentoria_planos_anuais_diferidos()

# Renovacoes clientes
df_renov_clientes = mentoria_renovacoes_clientes_mes(ANO_ATUAL, MES_ATUAL)
df_clientes_vencendo = mentoria_clientes_vencendo_mes(ANO_ATUAL, MES_ATUAL)


# ══════════════════════════════════════════════════════
# FUNCOES AUXILIARES
# ══════════════════════════════════════════════════════

def mes_label(ano, mes):
    return f"{MESES_NOME.get(mes, '?')}/{str(ano)[2:]}"


def hex_to_rgba(hex_color, alpha=0.5):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def gauge_chart(valor, budget, color=AZUL, height=140):
    """Cria grafico radial (gauge) mostrando progresso vs budget."""
    if budget and budget > 0:
        pct_val = min(valor / budget, 1.5)  # cap em 150%
        pct_display = valor / budget * 100
    else:
        pct_val = 0
        pct_display = 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_display,
        number={"suffix": "%", "font": {"size": 22, "color": "#e0e0e0"}},
        gauge={
            "axis": {"range": [0, 150], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)",
                     "tickfont": {"size": 1, "color": "rgba(0,0,0,0)"}},
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "rgba(42,42,62,0.6)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 100], "color": "rgba(42,42,62,0.3)"},
                {"range": [100, 150], "color": "rgba(0,214,143,0.08)"},
            ],
            "threshold": {
                "line": {"color": LARANJA, "width": 2},
                "thickness": 0.8,
                "value": 100,
            },
        },
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e0e0"},
    )
    return fig


def mini_trend(labels, values, color=AZUL, height=100):
    """Mini grafico de area/linha para tendencia dos ultimos meses."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=labels, y=values,
        mode="lines+markers+text",
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=6, color=color, line=dict(width=1, color="#0a0a0f")),
        fill="tozeroy",
        fillcolor=hex_to_rgba(color, 0.1),
        text=[brl_compact(v) for v in values],
        textposition="top center",
        textfont=dict(size=9, color="#c0c0d4"),
        hovertemplate="%{x}: %{customdata}<extra></extra>",
        customdata=[brl(v) for v in values],
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=18, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color=DIM), showline=False),
        yaxis=dict(visible=False),
    )
    return fig


# ══════════════════════════════════════════════════════
# CABECALHO (discreto, canto superior direito)
# ══════════════════════════════════════════════════════

st.markdown(f"""
<div style="display: flex; justify-content: flex-end; align-items: center;
            padding: 4px 0; margin-bottom: 8px;">
    <p style="font-family: 'Inter', sans-serif; color: {MUTED}; font-size: 11px; margin: 0; text-align: right; letter-spacing: 0.2px;">
        💰 <b style="color: {DIM};">Painel Financeiro</b> &nbsp;·&nbsp;
        Dados em tempo real &nbsp;·&nbsp;
        {now.strftime('%d/%m/%Y %H:%M')} &nbsp;·&nbsp;
        Ref: <b>{MESES_NOME[MES_ATUAL]}/{ANO_ATUAL}</b>
    </p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 1. GMV ACUMULADO HUB
# ══════════════════════════════════════════════════════

st.markdown('<p class="section-title">📈 GMV Acumulado HUB — Historico por Ano</p>',
            unsafe_allow_html=True)

if not df_gmv_anos.empty:
    gmv_atual_mes = float(df_hub_atual.iloc[0]["gmv"]) if not df_hub_atual.empty else 0
    receita_atual_mes = float(df_hub_atual.iloc[0]["receita_tutory"]) if not df_hub_atual.empty else 0

    col_card, col_chart = st.columns([1.2, 1])

    with col_card:
        # Card principal GMV
        total_gmv_all = float(df_gmv_anos["gmv"].sum())
        st.markdown(f"""
        <div class="fin-card fin-card-accent" style="border-left-color: {AZUL};">
            <p class="fin-label">GMV {MESES_NOME[MES_ATUAL]}/{ANO_ATUAL} (parcial)</p>
            <p class="fin-value">{brl(gmv_atual_mes)}</p>
            <p style="color: {DIM}; font-size: 12px; margin: 8px 0 0 0;">
                Receita Tutory no mes: <b style="color: {GREEN};">{brl(receita_atual_mes)}</b>
            </p>
            <p style="color: {MUTED}; font-size: 11px; margin: 6px 0 0 0;">
                GMV Historico Total: {brl(total_gmv_all)}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Mini cards por ano
        cols_anos = st.columns(min(len(df_gmv_anos), 5))
        for i, (_, row) in enumerate(df_gmv_anos.iterrows()):
            if i < 5:  # Max 5 anos
                with cols_anos[i % len(cols_anos)]:
                    st.markdown(f"""
                    <div style="background: {CARD_BG}; border: 1px solid {BORDER};
                                border-radius: 8px; padding: 10px; text-align: center;">
                        <p style="color: {MUTED}; font-size: 10px; margin: 0;">{int(row['ano'])}</p>
                        <p style="color: #c0c0d4; font-size: 14px; font-weight: 700; margin: 2px 0 0 0;">
                            {brl_compact(float(row['gmv']))}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

    with col_chart:
        # Gauge de GMV do mes vs budget (usando venda_hub_gmv do orcamento)
        budget_gmv = orcamento.get("venda_hub_gmv", {}).get(MES_ATUAL, 0)
        if budget_gmv > 0:
            fig_gauge = gauge_chart(gmv_atual_mes, budget_gmv, color=AZUL, height=110)
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
            st.markdown(f"""
            <p style="text-align: center; color: {MUTED}; font-size: 10px; margin-top: -8px;">
                Budget GMV: {brl(budget_gmv)}
            </p>
            """, unsafe_allow_html=True)
        else:
            # Tendencia se nao tem budget
            anos_lbl = [str(int(r['ano'])) for _, r in df_gmv_anos.iterrows()]
            gmvs = [float(r['gmv']) for _, r in df_gmv_anos.iterrows()]
            fig = mini_trend(anos_lbl, gmvs, color=AZUL, height=110)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.warning("Sem dados de GMV disponiveis.")

st.markdown("")


# ══════════════════════════════════════════════════════
# 2. RECEITA HUB x ORCAMENTO (com breakdown)
# ══════════════════════════════════════════════════════

st.markdown('<p class="section-title">🏦 Receita HUB x Orcamento</p>',
            unsafe_allow_html=True)

if not df_hub_breakdown.empty:
    # Dados do mes atual (ultima linha)
    row_atual = df_hub_breakdown.iloc[-1]
    receita_hub_total = float(row_atual["receita_total"])
    comissao_val = float(row_atual["comissao"])
    taxa_fixa_val = float(row_atual["taxa_fixa"])
    juros_val = float(row_atual["juros"])
    transacoes_val = int(row_atual["transacoes"])

    budget_hub = orcamento.get("receita_hub", {}).get(MES_ATUAL, 0)
    budget_comissao = orcamento.get("receita_hub_comissao", {}).get(MES_ATUAL, 0)
    budget_taxa = orcamento.get("receita_hub_taxa", {}).get(MES_ATUAL, 0)
    budget_financeira = orcamento.get("receita_hub_financeira", {}).get(MES_ATUAL, 0)

    # Delta vs mes anterior
    if len(df_hub_breakdown) >= 2:
        receita_anterior = float(df_hub_breakdown.iloc[-2]["receita_total"])
        delta_hub = delta_pct(receita_hub_total, receita_anterior)
    else:
        delta_hub = None

    # ── Todos os cards HUB na mesma linha ──
    col_hub_total, col_hub_com, col_hub_taxa, col_hub_juros = st.columns([1.6, 1, 1, 1])

    with col_hub_total:
        delta_class = "fin-delta-up" if delta_hub and delta_hub.startswith("+") else "fin-delta-down"
        delta_html = f'<p class="{delta_class}">vs anterior: {delta_hub}</p>' if delta_hub else ''
        hub_pct = (receita_hub_total / budget_hub * 100) if budget_hub > 0 else 0

        st.markdown(f"""
        <div class="fin-card fin-card-accent" style="border-left-color: {AZUL};">
            <p class="fin-label">Receita HUB Total</p>
            <p class="fin-value">{brl(receita_hub_total)}</p>
            {delta_html}
            <p class="fin-budget" style="color: {LARANJA};">
                Budget: {brl_compact(budget_hub)} · <b>{hub_pct:.0f}%</b>
            </p>
            <p style="color: {MUTED}; font-size: 10px; margin: 2px 0 0 0;">
                {num_br(transacoes_val)} transacoes
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_hub_com:
        st.markdown(f"""
        <div class="fin-card" style="text-align: center;">
            <p class="fin-sub-label">Comissao</p>
            <p class="fin-sub-value">{brl_compact(comissao_val)}</p>
            <p style="color: {MUTED}; font-size: 10px; margin: 4px 0 0 0;">
                Budget: {brl_compact(budget_comissao)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_hub_taxa:
        st.markdown(f"""
        <div class="fin-card" style="text-align: center;">
            <p class="fin-sub-label">Taxa Fixa</p>
            <p class="fin-sub-value">{brl_compact(taxa_fixa_val)}</p>
            <p style="color: {MUTED}; font-size: 10px; margin: 4px 0 0 0;">
                Budget: {brl_compact(budget_taxa)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_hub_juros:
        st.markdown(f"""
        <div class="fin-card" style="text-align: center;">
            <p class="fin-sub-label">Juros</p>
            <p class="fin-sub-value">{brl_compact(juros_val)}</p>
            <p style="color: {MUTED}; font-size: 10px; margin: 4px 0 0 0;">
                Budget: {brl_compact(budget_financeira)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Mini gauge + tendencia compactos lado a lado
    col_hub_gauge_sm, col_hub_trend = st.columns([0.4, 1])
    with col_hub_gauge_sm:
        fig_hub_gauge = gauge_chart(receita_hub_total, budget_hub, color=AZUL, height=100)
        st.plotly_chart(fig_hub_gauge, use_container_width=True, config={"displayModeBar": False})
    with col_hub_trend:
        hub_labels = [mes_label(int(r["ano"]), int(r["mes"])) for _, r in df_hub_breakdown.iterrows()]
        hub_values = [float(r["receita_total"]) for _, r in df_hub_breakdown.iterrows()]
        fig_trend = mini_trend(hub_labels, hub_values, color=AZUL, height=70)
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

else:
    st.warning("Sem dados de receita HUB.")

st.markdown("")


# ══════════════════════════════════════════════════════
# 3. RECEITA MENTORIA CONSOLIDADA (Recorrente + Anual)
# ══════════════════════════════════════════════════════

st.markdown('<p class="section-title">🎓 Receita Mentoria — Consolidada</p>',
            unsafe_allow_html=True)

# Calcular valores
recorrencia_valor = 0
if not df_recorrencia.empty and df_recorrencia.iloc[0]["receita"] is not None:
    recorrencia_valor = float(df_recorrencia.iloc[0]["receita"])

diferido_total = 0
if not df_anuais.empty:
    diferido_total = float(df_anuais["mensal_diferido"].sum())

receita_mentoria_total = recorrencia_valor + diferido_total
budget_mentoria = orcamento.get("receita_mentoria", {}).get(MES_ATUAL, 0)
budget_recorr = orcamento.get("receita_recorrencia", {}).get(MES_ATUAL, 0)
budget_diferido = orcamento.get("receita_anual_diferida", {}).get(MES_ATUAL, 0)

# ── Todos os cards Mentoria na mesma linha ──
ment_pct = (receita_mentoria_total / budget_mentoria * 100) if budget_mentoria > 0 else 0

col_ment_total, col_ment_recorr, col_ment_anual = st.columns([1.4, 1, 1])

with col_ment_total:
    st.markdown(f"""
    <div class="fin-card fin-card-accent" style="border-left-color: {GREEN};">
        <p class="fin-label">Receita Total Mentoria</p>
        <p class="fin-value">{brl(receita_mentoria_total)}</p>
        <p class="fin-budget" style="color: {LARANJA};">
            Budget: {brl_compact(budget_mentoria)} · <b>{ment_pct:.0f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ment_recorr:
    st.markdown(f"""
    <div class="fin-card" style="text-align: center;">
        <p class="fin-sub-label">🔄 Recorrencia Mensal</p>
        <p class="fin-sub-value">{brl_compact(recorrencia_valor)}</p>
        <p style="color: {MUTED}; font-size: 10px; margin: 4px 0 0 0;">
            Budget: {brl_compact(budget_recorr)}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ment_anual:
    st.markdown(f"""
    <div class="fin-card" style="text-align: center;">
        <p class="fin-sub-label">📅 Anual Diferido</p>
        <p class="fin-sub-value">{brl_compact(diferido_total)}</p>
        <p style="color: {MUTED}; font-size: 10px; margin: 4px 0 0 0;">
            Budget: {brl_compact(budget_diferido)}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Mini gauge + tendencia compactos
col_ment_gauge_sm, col_ment_trend = st.columns([0.4, 1])
with col_ment_gauge_sm:
    fig_ment_gauge = gauge_chart(receita_mentoria_total, budget_mentoria, color=GREEN, height=100)
    st.plotly_chart(fig_ment_gauge, use_container_width=True, config={"displayModeBar": False})
with col_ment_trend:
    if not df_mentoria_meses.empty:
        ment_labels = [mes_label(int(r["ano"]), int(r["mes"])) for _, r in df_mentoria_meses.iterrows()]
        ment_values = [float(r["receita"]) for _, r in df_mentoria_meses.iterrows()]
        fig_ment_trend = mini_trend(ment_labels, ment_values, color=GREEN, height=70)
        st.plotly_chart(fig_ment_trend, use_container_width=True, config={"displayModeBar": False})

# Detalhamento planos anuais
if not df_anuais.empty:
    with st.expander("📋 Detalhamento dos Planos Anuais Ativos"):
        display_df = df_anuais.copy()
        display_df.columns = ["Plano", "Contratos", "Valor Total", "Mensal Diferido"]
        display_df["Valor Total"] = display_df["Valor Total"].apply(lambda x: brl(float(x)))
        display_df["Mensal Diferido"] = display_df["Mensal Diferido"].apply(lambda x: brl(float(x)))
        st.dataframe(display_df, hide_index=True, use_container_width=True)

st.markdown("")


# ══════════════════════════════════════════════════════
# 4. RECEITA PLATINUM (Estrategia — 40% Tutory)
# ══════════════════════════════════════════════════════

st.markdown('<p class="section-title">💎 Receita Platinum — Estrategia Concursos (40% Tutory)</p>',
            unsafe_allow_html=True)

if not df_platinum.empty:
    plat_atual = df_platinum.iloc[-1]
    receita_plat = float(plat_atual["receita_tutory_40pct"])
    gmv_plat = float(plat_atual["gmv"])
    budget_plat = orcamento.get("receita_platinum", {}).get(MES_ATUAL, 0)

    if len(df_platinum) >= 2:
        delta_plat = delta_pct(receita_plat, float(df_platinum.iloc[-2]["receita_tutory_40pct"]))
    else:
        delta_plat = None

    delta_class = "fin-delta-up" if delta_plat and delta_plat.startswith("+") else "fin-delta-down"
    delta_html = f'<p class="{delta_class}">vs anterior: {delta_plat}</p>' if delta_plat else ''
    plat_pct = (receita_plat / budget_plat * 100) if budget_plat > 0 else 0

    st.markdown(f"""
    <div class="fin-card fin-card-accent" style="border-left-color: {PURPLE};">
        <p class="fin-label">Receita Tutory (40% do GMV Estrategia)</p>
        <p class="fin-value">{brl(receita_plat)}</p>
        {delta_html}
        <p style="color: {MUTED}; font-size: 11px; margin: 6px 0 0 0;">
            GMV Estrategia: {brl(gmv_plat)} · Budget: <span style="color: {LARANJA};">{brl(budget_plat)}</span> · <b>{plat_pct:.0f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Gauge + tendencia compactos
    col_plat_gauge_sm, col_plat_trend = st.columns([0.4, 1])
    with col_plat_gauge_sm:
        fig_plat_gauge = gauge_chart(receita_plat, budget_plat, color=PURPLE, height=100)
        st.plotly_chart(fig_plat_gauge, use_container_width=True, config={"displayModeBar": False})
    with col_plat_trend:
        plat_labels = [mes_label(int(r["ano"]), int(r["mes"])) for _, r in df_platinum.iterrows()]
        plat_values = [float(r["receita_tutory_40pct"]) for _, r in df_platinum.iterrows()]
        fig_plat_trend = mini_trend(plat_labels, plat_values, color=PURPLE, height=70)
        st.plotly_chart(fig_plat_trend, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Sem dados Platinum disponiveis.")

st.markdown("")


# ══════════════════════════════════════════════════════
# 5. RECEITA DE RENOVACAO x ORCAMENTO
# ══════════════════════════════════════════════════════

st.markdown('<p class="section-title">🔁 Receita de Renovacao x Orcamento</p>',
            unsafe_allow_html=True)

if not df_renovacoes.empty:
    df_renov = df_renovacoes[df_renovacoes["categoria"] == "renovacao"].copy()

    if not df_renov.empty:
        renov_atual = float(df_renov.iloc[-1]["bruto"]) if not df_renov.empty and df_renov.iloc[-1]["bruto"] else 0
        recebido_atual = float(df_renov.iloc[-1]["recebido"]) if not df_renov.empty and df_renov.iloc[-1]["recebido"] else 0
        budget_renov = orcamento.get("renovacao_plano_anual", {}).get(MES_ATUAL, 0)

        if len(df_renov) >= 2:
            delta_renov = delta_pct(renov_atual, float(df_renov.iloc[-2]["bruto"]) if df_renov.iloc[-2]["bruto"] else 0)
        else:
            delta_renov = None

        delta_class = "fin-delta-up" if delta_renov and delta_renov.startswith("+") else "fin-delta-down"
        delta_html = f'<p class="{delta_class}">vs anterior: {delta_renov}</p>' if delta_renov else ''
        renov_pct = (renov_atual / budget_renov * 100) if budget_renov > 0 else 0

        st.markdown(f"""
        <div class="fin-card fin-card-accent" style="border-left-color: {LARANJA};">
            <p class="fin-label">Renovacoes — Valor Bruto Contrato</p>
            <p class="fin-value">{brl(renov_atual)}</p>
            {delta_html}
            <p style="color: {DIM}; font-size: 12px; margin: 4px 0 0 0;">
                Recebido: <b style="color: {GREEN};">{brl(recebido_atual)}</b>
            </p>
            <p class="fin-budget" style="color: {LARANJA};">
                Budget: {brl(budget_renov)} · <b>{renov_pct:.0f}%</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Gauge + tendencia compactos
        col_renov_gauge_sm, col_renov_trend = st.columns([0.4, 1])
        with col_renov_gauge_sm:
            fig_renov_gauge = gauge_chart(renov_atual, budget_renov, color=LARANJA, height=100)
            st.plotly_chart(fig_renov_gauge, use_container_width=True, config={"displayModeBar": False})
        with col_renov_trend:
            renov_labels = [mes_label(int(r["ano"]), int(r["mes"])) for _, r in df_renov.iterrows()]
            renov_values = [float(r["bruto"]) if r["bruto"] else 0 for _, r in df_renov.iterrows()]
            fig_renov_trend = mini_trend(renov_labels, renov_values, color=LARANJA, height=70)
            st.plotly_chart(fig_renov_trend, use_container_width=True, config={"displayModeBar": False})

        # ── Detalhamento de clientes ──
        st.markdown(f"""
        <p style="color: {DIM}; font-size: 12px; font-weight: 600; margin: 16px 0 8px 0;">
            👥 Clientes com Planos Vencendo em {MESES_NOME[MES_ATUAL]}/{ANO_ATUAL}
        </p>
        """, unsafe_allow_html=True)

        if not df_clientes_vencendo.empty:
            # Separar por status
            renovados = df_clientes_vencendo[df_clientes_vencendo["status_renovacao"] == "Renovado"]
            pendentes = df_clientes_vencendo[df_clientes_vencendo["status_renovacao"] == "Pendente"]
            sem_link = df_clientes_vencendo[df_clientes_vencendo["status_renovacao"] == "Sem link"]

            col_ok, col_pend, col_none = st.columns(3)

            with col_ok:
                st.markdown(f"""
                <div class="fin-card" style="border-top: 3px solid {GREEN};">
                    <p style="color: {GREEN}; font-size: 12px; font-weight: 700; margin: 0 0 6px 0;">
                        ✅ Renovaram ({len(renovados)})
                    </p>
                """, unsafe_allow_html=True)
                if not renovados.empty:
                    for _, r in renovados.iterrows():
                        st.markdown(f"""
                        <p style="color: #c0c0d4; font-size: 12px; margin: 3px 0; padding-left: 8px;
                                  border-left: 2px solid {GREEN};">
                            {r['cliente']}<br/>
                            <span style="color: {MUTED}; font-size: 10px;">{r['plano']} · {brl(float(r['valor_anual']))}</span>
                        </p>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color: {MUTED}; font-size: 11px;">Nenhum ainda</p>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_pend:
                st.markdown(f"""
                <div class="fin-card" style="border-top: 3px solid {YELLOW};">
                    <p style="color: {YELLOW}; font-size: 12px; font-weight: 700; margin: 0 0 6px 0;">
                        ⏳ Pendente ({len(pendentes)})
                    </p>
                """, unsafe_allow_html=True)
                if not pendentes.empty:
                    for _, r in pendentes.iterrows():
                        st.markdown(f"""
                        <p style="color: #c0c0d4; font-size: 12px; margin: 3px 0; padding-left: 8px;
                                  border-left: 2px solid {YELLOW};">
                            {r['cliente']}<br/>
                            <span style="color: {MUTED}; font-size: 10px;">{r['plano']} · {brl(float(r['valor_anual']))}</span>
                        </p>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color: {MUTED}; font-size: 11px;">Nenhum</p>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_none:
                st.markdown(f"""
                <div class="fin-card" style="border-top: 3px solid {RED};">
                    <p style="color: {RED}; font-size: 12px; font-weight: 700; margin: 0 0 6px 0;">
                        ❌ Sem Link ({len(sem_link)})
                    </p>
                """, unsafe_allow_html=True)
                if not sem_link.empty:
                    for _, r in sem_link.iterrows():
                        st.markdown(f"""
                        <p style="color: #c0c0d4; font-size: 12px; margin: 3px 0; padding-left: 8px;
                                  border-left: 2px solid {RED};">
                            {r['cliente']}<br/>
                            <span style="color: {MUTED}; font-size: 10px;">{r['plano']} · {brl(float(r['valor_anual']))}</span>
                        </p>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color: {MUTED}; font-size: 11px;">Nenhum</p>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Sem dados de clientes vencendo neste mes.")

        # Tabela de renovacoes
        with st.expander("📋 Detalhamento Completo — Links de Renovacao"):
            if not df_renov_clientes.empty:
                display_renov = df_renov_clientes.copy()
                display_renov["valor_contrato"] = display_renov["valor_contrato"].apply(
                    lambda x: brl(float(x)) if x else "—"
                )
                display_renov["valor_pago"] = display_renov["valor_pago"].apply(
                    lambda x: brl(float(x)) if x else "—"
                )
                display_renov.columns = ["Cliente", "Valor Contrato", "Valor Pago", "Status", "Data"]
                st.dataframe(display_renov, hide_index=True, use_container_width=True)
            else:
                st.info("Sem links de renovacao no mes.")
    else:
        st.info("Sem renovacoes no periodo.")
else:
    st.info("Dados de renovacao indisponiveis.")


# ── Rodape ──
st.markdown("")
st.markdown(
    f"<p style='text-align: center; color: {MUTED}; font-size: 10px;'>"
    f"Cache: 15min (KPIs) · 24h (orcamento) &nbsp;·&nbsp; Budget 2026 v.Marlom"
    "</p>",
    unsafe_allow_html=True,
)
