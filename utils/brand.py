"""
Paleta de cores e CSS customizado da marca Tutory.
Referência: Manual de Marca Tutory 2024 (@cairo.stdo)

Cores oficiais:
  Azul  #334EFF  RGB(51,78,255)   — cor primária, tecnologia
  Laranja #EE5A24  RGB(238,90,36) — cor secundária, energia
  Preto #000000                   — base dark mode
  Branco #FFFFFF                  — base light / contraste

Tipografia: Fieldwork (Bold p/ títulos, Italic p/ subtítulos, Regular p/ texto)
Substituto web: Inter (Google Fonts) — geométrica, limpa, moderna.
"""
import streamlit as st

# ══════════════════════════════════════════════════════
# CORES OFICIAIS (Manual de Marca Tutory 2024)
# ══════════════════════════════════════════════════════
AZUL = "#334EFF"
LARANJA = "#EE5A24"
PRETO = "#000000"
BRANCO = "#FFFFFF"

# ── Cores derivadas para UI (dark mode) ──
BG_DARK = "#060610"       # fundo principal (quase preto, fiel ao manual)
CARD_BG = "#0e0e1a"       # fundo de cards
CARD_BG_HOVER = "#16162a"  # hover de cards
DIM = "#b0b0c8"            # texto secundário (mais legível)
MUTED = "#6a6a82"          # texto terciário
BORDER = "#1e1e34"         # bordas sutis

# ── Cores de status ──
GREEN = "#00d68f"
RED = "#ff6b6b"
YELLOW = "#ff9500"
PURPLE = "#9b51e0"

# ── Cores dos times (Gamificação) ──
COR_ALFA = "#e74c3c"
COR_BRAVO = "#0693e3"
COR_CHARLIE = "#f39c12"

# ── Azul/Laranja com opacidade (para fundos) ──
AZUL_10 = "#334EFF1A"     # 10% opacity
AZUL_20 = "#334EFF33"     # 20%
LARANJA_10 = "#EE5A241A"  # 10%
LARANJA_20 = "#EE5A2433"  # 20%


def inject_custom_css():
    """Injeta CSS customizado para branding Tutory no Streamlit.
    Fiel ao Manual de Marca 2024: cores, tipografia, espaçamento."""
    st.markdown(f"""
    <style>
    /* ══ Google Fonts — Inter (substituto de Fieldwork) ══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* ══ Reset de fonte global ══ */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* ══ Cards de métricas nativos ══ */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, {CARD_BG}, {CARD_BG_HOVER});
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 22px;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 28px;
        font-weight: 800;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: {DIM};
        font-weight: 600;
    }}

    /* ══ Sidebar — fundo escuro alinhado à marca ══ */
    [data-testid="stSidebar"] {{
        background: #060610;
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* ══ Esconde menu hamburguer e footer do Streamlit ══ */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* ══ Botão primário — Azul Tutory ══ */
    .stButton > button[kind="primary"],
    .stButton > button {{
        background: {AZUL} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: #2a40dd !important;
        transform: translateY(-1px);
    }}

    /* ══ Tabs ══ */
    .stTabs [data-baseweb="tab-panel"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 16px;
        background: {CARD_BG};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
    }}

    /* ══ Inputs de formulário (login, filtros) ══ */
    .stTextInput input, .stSelectbox select, .stNumberInput input {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
        border: 1px solid {BORDER} !important;
        background: {CARD_BG} !important;
    }}
    .stTextInput input:focus {{
        border-color: {AZUL} !important;
        box-shadow: 0 0 0 2px {AZUL_20} !important;
    }}

    /* ══ Divisores ══ */
    hr {{
        border-color: {BORDER};
    }}

    /* ══ Logo na sidebar ══ */
    .sidebar-logo {{
        padding: 20px 16px;
        text-align: center;
    }}
    .sidebar-logo img {{
        max-width: 180px;
    }}

    /* ══ Tela de login customizada ══ */
    .login-container {{
        max-width: 420px;
        margin: 0 auto;
        padding: 40px;
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
    }}
    .login-header {{
        text-align: center;
        margin-bottom: 30px;
    }}
    .login-header img {{
        max-width: 200px;
        margin-bottom: 16px;
    }}
    .login-header h2 {{
        color: {BRANCO};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 22px;
        letter-spacing: -0.3px;
    }}

    /* ══ Scrollbar customizada ══ */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {BG_DARK};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {BORDER};
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {MUTED};
    }}

    /* ══ Expander (acordeão) ══ */
    .streamlit-expanderHeader {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: {DIM} !important;
    }}

    /* ══ Tooltip / popover ══ */
    [data-testid="stTooltipIcon"] {{
        color: {MUTED};
    }}
    </style>
    """, unsafe_allow_html=True)
