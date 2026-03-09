"""
Queries financeiras do Dashboard Tutory.
Cada função encapsula uma query SQL com cache via st.cache_data.

Regras de negócio (REGRAS_E_CONTEXTO.md):
- Valores HUB em CENTAVOS (÷100 para R$)
- Receita Tutory HUB = taxa_percentual + taxa_fixa + taxa_juros (NUNCA GMV bruto)
- Alunos separados por plataforma (Mentoria ≠ HUB)
- Vendas Mentoria: usar LINKS_PAGAMENTO_ADM
- Platinum (Estratégia Concursos): professor_id = 12481, 40% fica pra Tutory
"""
import streamlit as st
import pandas as pd
from utils.db import get_hub_connection, get_mentoria_connection, run_query


# ══════════════════════════════════════════════════════
# HUB (PostgreSQL) — Receita, GMV, Platinum
# ══════════════════════════════════════════════════════

ESTRATEGIA_PROFESSOR_ID = 12481  # Estratégia Concursos (Platinum)


@st.cache_data(ttl=900)
def hub_gmv_acumulado_por_ano():
    """GMV e receita acumulados por ano (todos os anos)."""
    conn = get_hub_connection()
    query = """
        SELECT EXTRACT(YEAR FROM data)::int AS ano,
               COUNT(*) AS transacoes,
               SUM(valor) / 100.0 AS gmv,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS receita_tutory
        FROM transacoes
        WHERE status = 'paid'
        GROUP BY EXTRACT(YEAR FROM data)
        ORDER BY ano
    """
    return run_query(conn, query, db_name="HUB")


@st.cache_data(ttl=900)
def hub_receita_mensal(ano, mes):
    """Receita HUB de um mês específico com breakdown."""
    conn = get_hub_connection()
    query = """
        SELECT COUNT(*) AS transacoes,
               SUM(valor) / 100.0 AS gmv,
               SUM(taxa_percentual) / 100.0 AS taxa_pct,
               SUM(taxa_fixa) / 100.0 AS taxa_fixa,
               SUM(taxa_juros) / 100.0 AS juros,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS receita_total
        FROM transacoes
        WHERE EXTRACT(YEAR FROM data) = %s
          AND EXTRACT(MONTH FROM data) = %s
          AND status = 'paid'
    """
    return run_query(conn, query, params=(ano, mes), db_name="HUB")


@st.cache_data(ttl=900)
def hub_receita_ultimos_meses(n_meses=4):
    """Receita HUB mês a mês para os últimos N meses."""
    conn = get_hub_connection()
    query = f"""
        SELECT EXTRACT(YEAR FROM data)::int AS ano,
               EXTRACT(MONTH FROM data)::int AS mes,
               SUM(valor) / 100.0 AS gmv,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS receita_tutory,
               COUNT(*) AS transacoes
        FROM transacoes
        WHERE status = 'paid'
          AND data >= (CURRENT_DATE - INTERVAL '{n_meses} months')
        GROUP BY EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data)
        ORDER BY ano, mes
    """
    return run_query(conn, query, db_name="HUB")


@st.cache_data(ttl=900)
def hub_receita_breakdown_mensal(n_meses=4):
    """Breakdown da receita HUB: comissão, taxa fixa, juros — por mês.
    Exclui Platinum (professor_id 12481) para evitar dupla contagem."""
    conn = get_hub_connection()
    query = f"""
        SELECT EXTRACT(YEAR FROM data)::int AS ano,
               EXTRACT(MONTH FROM data)::int AS mes,
               SUM(taxa_percentual) / 100.0 AS comissao,
               SUM(taxa_fixa) / 100.0 AS taxa_fixa,
               SUM(taxa_juros) / 100.0 AS juros,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS receita_total,
               SUM(valor) / 100.0 AS gmv,
               COUNT(*) AS transacoes
        FROM transacoes
        WHERE status = 'paid'
          AND data >= (CURRENT_DATE - INTERVAL '{n_meses} months')
        GROUP BY EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data)
        ORDER BY ano, mes
    """
    return run_query(conn, query, db_name="HUB")


@st.cache_data(ttl=900)
def hub_gmv_mes_atual():
    """GMV e receita do mês corrente."""
    conn = get_hub_connection()
    query = """
        SELECT COUNT(*) AS transacoes,
               SUM(valor) / 100.0 AS gmv,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS receita_tutory
        FROM transacoes
        WHERE EXTRACT(YEAR FROM data) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND EXTRACT(MONTH FROM data) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND status = 'paid'
    """
    return run_query(conn, query, db_name="HUB")


@st.cache_data(ttl=900)
def hub_platinum_mensal(n_meses=4):
    """Receita Platinum (Estratégia Concursos) — 40% do GMV fica pra Tutory."""
    conn = get_hub_connection()
    query = f"""
        SELECT EXTRACT(YEAR FROM data)::int AS ano,
               EXTRACT(MONTH FROM data)::int AS mes,
               COUNT(*) AS transacoes,
               SUM(valor) / 100.0 AS gmv,
               SUM(valor) / 100.0 * 0.4 AS receita_tutory_40pct,
               SUM(taxa_percentual + taxa_fixa + taxa_juros) / 100.0 AS comissao_plataforma
        FROM transacoes
        WHERE professor_id = {ESTRATEGIA_PROFESSOR_ID}
          AND status = 'paid'
          AND data >= (CURRENT_DATE - INTERVAL '{n_meses} months')
        GROUP BY EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data)
        ORDER BY ano, mes
    """
    return run_query(conn, query, db_name="HUB")


# ══════════════════════════════════════════════════════
# MENTORIA (SQL Server) — B2B, Renovações, Recorrência
# ══════════════════════════════════════════════════════

@st.cache_data(ttl=900)
def mentoria_receita_b2b_mensal(n_meses=4):
    """Receita B2B da Mentoria (PAGAMENTOS_ADM pagos)."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT YEAR(PAG_DT_GERACAO) AS ano,
               MONTH(PAG_DT_GERACAO) AS mes,
               COUNT(*) AS pagamentos,
               SUM(PAG_VALOR) AS receita
        FROM PAGAMENTOS_ADM
        WHERE PAG_STATUS = 'paid'
          AND PAG_DT_GERACAO >= DATEADD(MONTH, -%s, GETDATE())
        GROUP BY YEAR(PAG_DT_GERACAO), MONTH(PAG_DT_GERACAO)
        ORDER BY ano, mes
    """
    return run_query(conn, query, params=(n_meses,), db_name="Mentoria")


@st.cache_data(ttl=900)
def mentoria_receita_mes_atual():
    """Receita B2B do mês corrente com breakdown por tipo."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT PAG_TIPO, COUNT(*) AS pagamentos, SUM(PAG_VALOR) AS receita
        FROM PAGAMENTOS_ADM
        WHERE PAG_STATUS = 'paid'
          AND YEAR(PAG_DT_GERACAO) = YEAR(GETDATE())
          AND MONTH(PAG_DT_GERACAO) = MONTH(GETDATE())
        GROUP BY PAG_TIPO
    """
    return run_query(conn, query, db_name="Mentoria")


@st.cache_data(ttl=900)
def mentoria_renovacoes_mensal(n_meses=4):
    """Renovações via LINKS_PAGAMENTO_ADM."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT YEAR(LINK_DT_CRIACAO) AS ano,
               MONTH(LINK_DT_CRIACAO) AS mes,
               LINK_CATEGORIA AS categoria,
               COUNT(*) AS total,
               SUM(LINK_PAG_VALOR_CONTRATO) AS bruto,
               SUM(CASE WHEN LINK_STATUS = 'paid' THEN LINK_VALOR ELSE 0 END) AS recebido
        FROM LINKS_PAGAMENTO_ADM
        WHERE LINK_DT_CRIACAO >= DATEADD(MONTH, -%s, GETDATE())
        GROUP BY YEAR(LINK_DT_CRIACAO), MONTH(LINK_DT_CRIACAO), LINK_CATEGORIA
        ORDER BY ano, mes, LINK_CATEGORIA
    """
    return run_query(conn, query, params=(n_meses,), db_name="Mentoria")


@st.cache_data(ttl=1800)
def mentoria_recorrencia_mensal():
    """Receita recorrente: assinaturas mensais ativas (mês atual)."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT COUNT(*) AS pagamentos, SUM(PAG_VALOR) AS receita
        FROM PAGAMENTOS_ADM
        WHERE PAG_STATUS = 'paid'
          AND PAG_TIPO = 'fatura'
          AND YEAR(PAG_DT_GERACAO) = YEAR(GETDATE())
          AND MONTH(PAG_DT_GERACAO) = MONTH(GETDATE())
    """
    return run_query(conn, query, db_name="Mentoria")


@st.cache_data(ttl=1800)
def mentoria_planos_anuais_diferidos():
    """Planos anuais ativos com valor diferido mensal."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT p.PLANO_NOME,
               COUNT(*) AS contratos,
               SUM(c.CTR_PLN_ANU_VALOR) AS valor_total,
               SUM(c.CTR_PLN_ANU_VALOR) / 12.0 AS mensal_diferido
        FROM CTR_PLANOS_ANUAIS c
        JOIN PLANOS p ON c.CTR_PLN_ANU_PLANO_ID = p.PLANO_ID
        WHERE c.CTR_PLN_ANU_DT_FIM >= GETDATE()
          AND c.CTR_PLN_ANU_ATIVO = 1
        GROUP BY p.PLANO_NOME
        ORDER BY SUM(c.CTR_PLN_ANU_VALOR) DESC
    """
    return run_query(conn, query, db_name="Mentoria")


@st.cache_data(ttl=900)
def mentoria_renovacoes_clientes_mes(ano, mes):
    """Clientes que renovaram no mês (LINKS_PAGAMENTO_ADM com categoria='renovacao').
    Usa LINK_NOME diretamente (nome do cliente no link de pagamento)."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT LINK_NOME AS cliente,
               LINK_PAG_VALOR_CONTRATO AS valor_contrato,
               LINK_VALOR AS valor_pago,
               LINK_STATUS AS status,
               LINK_DT_CRIACAO AS data_criacao
        FROM LINKS_PAGAMENTO_ADM
        WHERE LINK_CATEGORIA = 'renovacao'
          AND YEAR(LINK_DT_CRIACAO) = %s
          AND MONTH(LINK_DT_CRIACAO) = %s
        ORDER BY LINK_DT_CRIACAO DESC
    """
    return run_query(conn, query, params=(ano, mes), db_name="Mentoria")


@st.cache_data(ttl=900)
def mentoria_clientes_vencendo_mes(ano, mes):
    """Clientes com planos anuais vencendo no mês — potenciais renovações.
    Cruza com LINKS_PAGAMENTO_ADM via email do admin para ver se já renovaram."""
    conn = get_mentoria_connection()
    if conn is None:
        return pd.DataFrame()
    query = """
        SELECT a.ADM_NOME AS cliente,
               p.PLANO_NOME AS plano,
               c.CTR_PLN_ANU_VALOR AS valor_anual,
               c.CTR_PLN_ANU_DT_FIM AS dt_vencimento,
               CASE
                   WHEN EXISTS (
                       SELECT 1 FROM LINKS_PAGAMENTO_ADM l
                       WHERE l.LINK_EMAIL = a.ADM_EMAIL
                         AND l.LINK_CATEGORIA = 'renovacao'
                         AND l.LINK_STATUS = 'paid'
                         AND YEAR(l.LINK_DT_CRIACAO) = %s
                         AND MONTH(l.LINK_DT_CRIACAO) = %s
                   ) THEN 'Renovado'
                   WHEN EXISTS (
                       SELECT 1 FROM LINKS_PAGAMENTO_ADM l
                       WHERE l.LINK_EMAIL = a.ADM_EMAIL
                         AND l.LINK_CATEGORIA = 'renovacao'
                         AND l.LINK_STATUS != 'paid'
                         AND YEAR(l.LINK_DT_CRIACAO) = %s
                         AND MONTH(l.LINK_DT_CRIACAO) = %s
                   ) THEN 'Pendente'
                   ELSE 'Sem link'
               END AS status_renovacao
        FROM CTR_PLANOS_ANUAIS c
        JOIN PLANOS p ON c.CTR_PLN_ANU_PLANO_ID = p.PLANO_ID
        JOIN ADMINISTRADORES a ON c.CTR_PLN_ANU_ADM_ID = a.ADM_ID
        WHERE YEAR(c.CTR_PLN_ANU_DT_FIM) = %s
          AND MONTH(c.CTR_PLN_ANU_DT_FIM) = %s
          AND c.CTR_PLN_ANU_ATIVO = 1
        ORDER BY c.CTR_PLN_ANU_DT_FIM ASC
    """
    return run_query(conn, query, params=(ano, mes, ano, mes, ano, mes), db_name="Mentoria")


# ══════════════════════════════════════════════════════
# ORÇAMENTO (Budget) — Leitura da planilha Excel
# ══════════════════════════════════════════════════════

@st.cache_data(ttl=86400)
def carregar_orcamento():
    """Carrega dados de orçamento da planilha Budget 2026.
    Retorna dict com valores mensais por categoria."""
    import os
    budget_path = os.path.join(os.path.dirname(__file__), "..", "config", "budget_2026.xlsx")
    if not os.path.exists(budget_path):
        return {}

    try:
        df = pd.read_excel(budget_path, sheet_name="BUDGET 2026", header=None)

        # Mapeamento: nome da linha -> índice da linha no DataFrame
        # Coluna 1 = nome, Colunas 3-14 = Jan-Dez
        budget = {}
        meses = list(range(1, 13))  # 1=Jan ... 12=Dez

        linhas_budget = {
            "venda_mentoria": 10,
            "plano_recorrencia": 11,
            "assinatura_anual": 12,
            "renovacao_plano_anual": 13,
            "venda_hub_gmv": 14,
            "hub_comissao": 15,
            "hub_taxa": 16,
            "hub_receita_financeira": 17,
            "venda_platinum": 18,
            "receita_mentoria": 25,
            "receita_recorrencia": 26,
            "receita_anual_diferida": 27,
            "receita_hub": 28,
            "receita_hub_comissao": 29,
            "receita_hub_taxa": 30,
            "receita_hub_financeira": 31,
            "receita_platinum": 32,
        }

        for nome, row_idx in linhas_budget.items():
            valores = {}
            for i, mes in enumerate(meses):
                col_idx = 3 + i  # Coluna 3 = Janeiro
                val = df.iloc[row_idx, col_idx]
                try:
                    valores[mes] = float(val) if pd.notna(val) else 0.0
                except (ValueError, TypeError):
                    valores[mes] = 0.0
            budget[nome] = valores

        return budget
    except Exception as e:
        st.warning(f"⚠️ Erro ao ler orçamento: {e}")
        return {}
