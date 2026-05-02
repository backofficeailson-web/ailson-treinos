# auth.py
import hashlib
import streamlit as st
from config import USUARIO_VALIDO, SENHA_HASH

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(usuario, senha):
    return usuario == USUARIO_VALIDO and hash_senha(senha) == SENHA_HASH

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
        else:
            st.markdown("<h1 style='text-align:center;color:#7CFC00;'>🟢 AILSON PERSONAL</h1>", unsafe_allow_html=True)
        st.title("AILSON PERSONAL")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")