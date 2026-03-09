"""
Dashboard Tutory — Ponto de Entrada
Tela de login + página inicial de boas-vindas.
"""
import streamlit as st
from utils.brand import inject_custom_css, AZUL, LARANJA
from utils.auth import require_login

# ── Configuração da página ──
st.set_page_config(
    page_title="Tutory Dashboard",
    page_icon="📊",
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
    background: linear-gradient(135deg, {AZUL}22, {LARANJA}11);
    border: 1px solid {AZUL}33;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin-bottom: 30px;
">
    <h1 style="
        color: #e0e0e0;
        font-size: 36px;
        font-weight: 800;
        margin: 0 0 8px 0;
    ">Bem-vindo, {nome}! 👋</h1>
    <p style="
        color: #a0a0b4;
        font-size: 16px;
        margin: 0;
    ">Painel de dados da Tutory — selecione uma área no menu lateral.</p>
</div>
""", unsafe_allow_html=True)

# ── Cards informativos (placeholder para futuras páginas) ──
st.markdown("### 📋 Áreas disponíveis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: {AZUL}; margin: 0 0 8px 0; font-size: 18px;">💰 Financeiro</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">Receita HUB, B2B, transações</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: {LARANJA}; margin: 0 0 8px 0; font-size: 18px;">🎯 Gamificação</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">Operação Golias, times, metas</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: #00d68f; margin: 0 0 8px 0; font-size: 18px;">📈 Alunos</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">Crescimento, engajamento</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: #9b51e0; margin: 0 0 8px 0; font-size: 18px;">💬 Atendimento</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">Intercom, tickets, NPS</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: #ff9500; margin: 0 0 8px 0; font-size: 18px;">📣 Marketing</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">Facebook Ads, métricas</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 24px;
        height: 120px;
    ">
        <h3 style="color: #e74c3c; margin: 0 0 8px 0; font-size: 18px;">🤝 Comercial</h3>
        <p style="color: #a0a0b4; font-size: 13px; margin: 0;">HubSpot, pipeline, vendas</p>
        <p style="color: #5a5a72; font-size: 11px; margin-top: 8px;">🔜 Em breve</p>
    </div>
    """, unsafe_allow_html=True)

# ── Rodapé ──
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #5a5a72; font-size: 12px;'>"
    "Tutory Dashboard v1.0 — Dados seguros, decisões inteligentes."
    "</p>",
    unsafe_allow_html=True,
)
