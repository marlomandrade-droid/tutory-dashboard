"""
Conexões com os bancos de dados da Tutory.
- MENTORIA: SQL Server (AWS RDS)
- HUB: PostgreSQL (AWS RDS)

Usa st.secrets para credenciais (nunca hardcoded).
Reconexão automática em caso de falha.
"""
import streamlit as st
import pandas as pd


def _create_hub_connection():
    """Cria nova conexão com o HUB (PostgreSQL)."""
    import psycopg2
    cfg = st.secrets["hub"]
    conn = psycopg2.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["database"],
        port=int(cfg["port"]),
        connect_timeout=15,
    )
    conn.autocommit = True
    return conn


def _create_mentoria_connection():
    """Cria nova conexão com a MENTORIA (SQL Server)."""
    import pymssql
    cfg = st.secrets["mentoria"]
    conn = pymssql.connect(
        server=cfg["server"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=int(cfg["port"]),
        login_timeout=15,
        timeout=60,
    )
    return conn


@st.cache_resource(ttl=3600)
def get_hub_connection():
    """Retorna conexão com o HUB (PostgreSQL).
    Cached por 1 hora. Reconecta automaticamente se cair."""
    try:
        return _create_hub_connection()
    except Exception as e:
        st.error(f"❌ Erro ao conectar no HUB (PostgreSQL): {e}")
        return None


@st.cache_resource(ttl=3600)
def get_mentoria_connection():
    """Retorna conexão com a MENTORIA (SQL Server).
    Cached por 1 hora. Reconecta automaticamente se cair."""
    try:
        return _create_mentoria_connection()
    except Exception as e:
        st.error(f"❌ Erro ao conectar na Mentoria (SQL Server): {e}")
        st.info("💡 Verifique se o IP está liberado no Security Group da AWS.")
        return None


def _is_hub_alive(conn):
    """Testa se a conexão PostgreSQL está viva."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True
    except Exception:
        return False


def _is_mentoria_alive(conn):
    """Testa se a conexão SQL Server está viva."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True
    except Exception:
        return False


def run_query(conn, query, params=None, db_name=""):
    """Executa uma query SQL e retorna um pandas DataFrame.
    Se a conexão estiver morta, tenta reconectar UMA vez."""
    if conn is None:
        return pd.DataFrame()

    try:
        return pd.read_sql(query, conn, params=params)
    except Exception as e:
        # Tentativa de reconexão
        try:
            if db_name == "HUB":
                get_hub_connection.clear()
                new_conn = _create_hub_connection()
                # Atualiza cache
                result = pd.read_sql(query, new_conn, params=params)
                return result
            elif db_name == "Mentoria":
                get_mentoria_connection.clear()
                new_conn = _create_mentoria_connection()
                result = pd.read_sql(query, new_conn, params=params)
                return result
        except Exception as retry_err:
            st.warning(f"⚠️ Erro na query ({db_name}): {retry_err}")
            get_hub_connection.clear()
            get_mentoria_connection.clear()
            return pd.DataFrame()

        st.warning(f"⚠️ Erro na query ({db_name}): {e}")
        get_hub_connection.clear()
        get_mentoria_connection.clear()
        return pd.DataFrame()
