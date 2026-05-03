import hashlib
import streamlit as st
from database import execute_query
from datetime import datetime, timedelta

def autenticar(usuario, senha):
    usuario_data = execute_query(
        "SELECT id, senha_hash FROM usuarios WHERE username = ? AND ativo = 1",
        (usuario,), fetchone=True)
    if usuario_data:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        return usuario_data[1] == senha_hash
    return False

def logout():
    st.session_state.logado = False
    st.session_state.usuario = None
    st.rerun()

def tela_login():
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0A0A0A 0%, #0D3B0D 100%); }
        h1, p, label { color: #7CFC00 !important; }
        .stButton > button {
            background: linear-gradient(135deg, #2ECC40 0%, #0D3B0D 100%);
            color: white !important; border: 2px solid #7CFC00; border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        import os
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=250)
        elif os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        else:
            st.markdown("<h1 style='text-align:center;color:#7CFC00;'>🟢 AILSON PERSONAL</h1>", unsafe_allow_html=True)
        st.title("AILSON PERSONAL")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.ultima_atividade = datetime.now()
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

# Timeout de sessão (30 min)
def verificar_timeout():
    if "ultima_atividade" in st.session_state:
        if datetime.now() - st.session_state.ultima_atividade > timedelta(minutes=30):
            logout()