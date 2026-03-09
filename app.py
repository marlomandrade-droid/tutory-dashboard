"""
Dashboard Tutory — Ponto de Entrada
Tela de login + página inicial de boas-vindas.
Identidade visual: Manual de Marca Tutory 2024.
"""
import streamlit as st
from utils.brand import (
    inject_custom_css, AZUL, LARANJA, BRANCO,
    CARD_BG, CARD_BG_HOVER, BORDER, DIM, MUTED,
)
from utils.auth import require_login

# ── Configuração da página ──
st.set_page_config(
    page_title="Tutory Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS da marca ──
inject_custom_css()

# ── Logo na sidebar (antes do login para aparecer na tela de login) ──
import os
logo_path = os.path.join(os.path.dirname(__file__), "assets", "tutory_logo_nova_branca.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=180)
    st.sidebar.markdown("---")

# ── Autenticação ──
require_login()

# ══════════════════════════════════════════════════════
# A partir daqui, o usuário está autenticado
# ══════════════════════════════════════════════════════

nome = st.session_state.get("name", "")

# ── Cabeçalho de boas-vindas ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {AZUL}15, {LARANJA}08, {CARD_BG});
    border: 1px solid {BORDER};
    border-left: 4px solid {AZUL};
    border-radius: 16px;
    padding: 44px 48px;
    margin-bottom: 32px;
">
    <h1 style="
        font-family: 'Inter', sans-serif;
        color: {BRANCO};
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 10px 0;
    ">Bem-vindo, {nome}! 👋</h1>
    <p style="
        font-family: 'Inter', sans-serif;
        color: {DIM};
        font-size: 16px;
        margin: 0;
        font-weight: 400;
    ">Painel de dados da Tutory — selecione uma área no menu lateral.</p>
</div>
""", unsafe_allow_html=True)

# ── Cards informativos (áreas do dashboard) ──
st.markdown(f"""
<p style="
    font-family: 'Inter', sans-serif;
    color: {DIM};
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 0 0 16px 0;
">Áreas Disponíveis</p>
""", unsafe_allow_html=True)

# Helper para gerar card HTML
def _area_card(cor, icone, titulo, descricao, status="✅ Ativo"):
    tag_bg = f"rgba(0,214,143,0.12)" if status == "✅ Ativo" else f"rgba(255,149,0,0.12)"
    tag_cor = "#00d68f" if status == "✅ Ativo" else "#ff9500"
    return f"""
    <div style="
        background: linear-gradient(135deg, {CARD_BG}, {CARD_BG_HOVER});
        border: 1px solid {BORDER};
        border-top: 3px solid {cor};
        border-radius: 14px;
        padding: 24px 24px 20px;
        height: 130px;
        transition: all 0.2s ease;
    ">
        <h3 style="
            font-family: 'Inter', sans-serif;
            color: {cor};
            margin: 0 0 8px 0;
            font-size: 17px;
            font-weight: 800;
            letter-spacing: -0.2px;
        ">{icone} {titulo}</h3>
        <p style="
            font-family: 'Inter', sans-serif;
            color: {DIM};
            font-size: 13px;
            margin: 0 0 12px 0;
            font-weight: 400;
        ">{descricao}</p>
        <span style="
            background: {tag_bg};
            color: {tag_cor};
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
        ">{status}</span>
    </div>
    """

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(_area_card(AZUL, "💰", "Financeiro", "Receita HUB, B2B, Platinum"), unsafe_allow_html=True)
with col2:
    st.markdown(_area_card(LARANJA, "🎯", "Gamificação", "Operação Golias, times, metas", "🔜 Em breve"), unsafe_allow_html=True)
with col3:
    st.markdown(_area_card("#00d68f", "📈", "Alunos", "Crescimento, engajamento", "🔜 Em breve"), unsafe_allow_html=True)

st.markdown("")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(_area_card("#9b51e0", "💬", "Atendimento", "Intercom, tickets, NPS", "🔜 Em breve"), unsafe_allow_html=True)
with col5:
    st.markdown(_area_card(LARANJA, "📣", "Marketing", "Facebook Ads, métricas", "🔜 Em breve"), unsafe_allow_html=True)
with col6:
    st.markdown(_area_card("#e74c3c", "🤝", "Comercial", "HubSpot, pipeline, vendas", "🔜 Em breve"), unsafe_allow_html=True)

# ── Rodapé ──
st.markdown("---")
st.markdown(
    f"<p style='text-align: center; color: {MUTED}; font-size: 11px; "
    f"font-family: Inter, sans-serif; letter-spacing: 0.3px;'>"
    "Tutory Dashboard v1.0 — Dados seguros, decisões inteligentes."
    "</p>",
    unsafe_allow_html=True,
)
