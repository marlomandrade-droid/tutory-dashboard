"""
Formatadores para o Dashboard Tutory.
Converte valores para formato brasileiro (BRL, datas, números).
"""


def brl(value, decimals=2):
    """Formata número como Real brasileiro.
    brl(1234.5) -> 'R$ 1.234,50'"""
    if value is None or value == 0:
        return "R$ 0,00"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "R$ 0,00"
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def brl_compact(value):
    """Formato compacto para valores grandes.
    brl_compact(1234567) -> 'R$ 1,2M'"""
    if value is None:
        return "R$ 0"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "R$ 0"
    if abs(value) >= 1_000_000:
        v = f"{value / 1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        v = f"{value / 1_000:,.1f}K"
    else:
        v = f"{value:,.0f}"
    v = v.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v}"


def num_br(value):
    """Formata inteiro com separadores de milhar brasileiros.
    num_br(191003) -> '191.003'"""
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", ".")


def pct(value, decimals=1):
    """Formata porcentagem.
    pct(0.143) -> '14,3%'"""
    if value is None:
        return "0,0%"
    v = f"{value * 100:,.{decimals}f}"
    v = v.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{v}%"


def centavos_to_brl(centavos):
    """Converte centavos do HUB para R$.
    centavos_to_brl(49900) -> 499.0"""
    return (centavos or 0) / 100.0


def delta_pct(atual, anterior):
    """Calcula variação percentual entre dois valores.
    Retorna string formatada: '+12,5%' ou '-3,2%'."""
    if anterior is None or anterior == 0:
        return "—"
    var = (atual - anterior) / anterior
    sinal = "+" if var >= 0 else ""
    return f"{sinal}{var * 100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
