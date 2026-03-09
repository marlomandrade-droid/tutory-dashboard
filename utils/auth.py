"""
Sistema de autenticação do Dashboard Tutory.
Usa streamlit-authenticator com senhas bcrypt e cookies de sessão.
"""
import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml


def _load_users_config():
    """Carrega configuração de usuários do arquivo YAML."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "users.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_authenticator():
    """Cria e retorna o objeto de autenticação."""
    config = _load_users_config()

    cookie_name = st.secrets.get("auth", {}).get("cookie_name", "tutory_dash")
    cookie_key = st.secrets.get("auth", {}).get("cookie_key", "tutory_secret_key_2026")
    cookie_expiry = st.secrets.get("auth", {}).get("cookie_expiry_days", 7)

    authenticator = stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=cookie_name,
        cookie_key=cookie_key,
        cookie_expiry_days=cookie_expiry,
    )
    return authenticator


def require_login():
    """
    Exibe a tela de login se o usuário não estiver autenticado.
    Retorna True se autenticado, caso contrário para a execução (st.stop).
    """
    authenticator = get_authenticator()

    # Renderiza o formulário de login
    authenticator.login(
        location="main",
        fields={
            "Form name": "Acesse o Dashboard",
            "Username": "Usuário",
            "Password": "Senha",
            "Login": "Entrar",
        },
        clear_on_submit=True,
    )

    if st.session_state.get("authentication_status"):
        # Usuário logado — exibe botão de logout na sidebar
        with st.sidebar:
            st.markdown(f"**{st.session_state.get('name', '')}**")
            authenticator.logout("Sair", location="main", key="sidebar_logout")
        return True

    elif st.session_state.get("authentication_status") is False:
        st.error("Usuário ou senha incorretos.")
        st.stop()
        return False

    else:
        # Nenhuma tentativa ainda
        st.stop()
        return False
