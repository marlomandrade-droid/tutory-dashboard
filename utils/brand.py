"""
Paleta de cores e CSS customizado da marca Tutory.
Referência: manual_marca_tutory.pdf + gerar_funil_hub.py
"""
import streamlit as st

# ── Cores oficiais Tutory ──
AZUL = "#334EFF"
LARANJA = "#EE5A24"
PRETO = "#000000"
BRANCO = "#FFFFFF"

# ── Cores derivadas para UI ──
BG_DARK = "#0a0a0f"
CARD_BG = "#12121e"
CARD_BG_HOVER = "#1a1a2e"
DIM = "#a0a0b4"
MUTED = "#5a5a72"
BORDER = "#2a2a3e"

# ── Cores de status ──
GREEN = "#00d68f"
RED = "#ff6b6b"
YELLOW = "#ff9500"
PURPLE = "#9b51e0"

# ── Cores dos times ──
COR_ALFA = "#e74c3c"
COR_BRAVO = "#0693e3"
COR_CHARLIE = "#f39c12"


def inject_custom_css():
    """Injeta CSS customizado para branding Tutory no Streamlit."""
    st.markdown("""
    <style>
    /* ── Cards de métricas ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #12121e, #1a1a2e);
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #a0a0b4;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0a0a14;
        border-right: 1px solid #1e1e30;
    }

    /* ── Esconde menu e footer do Streamlit ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Containers com borda sutil ── */
    .stTabs [data-baseweb="tab-panel"] {
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 16px;
        background: #0f0f18;
    }

    /* ── Divisores ── */
    hr {
        border-color: #2a2a3e;
    }

    /* ── Logo na sidebar ── */
    .sidebar-logo {
        padding: 20px 16px;
        text-align: center;
    }
    .sidebar-logo img {
        max-width: 180px;
    }

    /* ── Tela de login customizada ── */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
    }
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .login-header img {
        max-width: 200px;
        margin-bottom: 16px;
    }
    .login-header h2 {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
