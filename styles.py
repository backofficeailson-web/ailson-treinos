# styles.py
import streamlit as st
from config import VERDE_ESCURO, VERDE_HULK, VERDE_CLARO, PRETO, BRANCO, AMARELO_ALERTA

def aplicar_css():
    st.markdown(f"""
    <style>
        .stApp {{ background: linear-gradient(135deg, {PRETO} 0%, {VERDE_ESCURO} 100%); }}
        section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {PRETO} 0%, #3D0F5C 100%); }}
        h1, h2, h3 {{ color: {VERDE_CLARO} !important; }}
        .stButton>button {{
            background: linear-gradient(135deg, {VERDE_HULK} 0%, {VERDE_ESCURO} 100%);
            color: white; border-radius: 10px; border: 2px solid {VERDE_CLARO};
        }}
    </style>
    """, unsafe_allow_html=True)

def card(titulo, valor, cor="#1E1E1E"):
    st.markdown(f"""
    <div style="background:{cor}; padding:15px; border-radius:10px; border:2px solid {VERDE_HULK}; margin-bottom:10px;">
        <h4 style="color:{VERDE_CLARO};">{titulo}</h4>
        <p style="color:white; font-size:1.5rem;">{valor}</p>
    </div>
    """, unsafe_allow_html=True)

def logo_sidebar():
    import os
    if os.path.exists("assets/logo.png"):
        st.sidebar.image("assets/logo.png", width=180)
    else:
        st.sidebar.markdown(f"<h2 style='color:{VERDE_CLARO};'>🟢 AILSON PERSONAL</h2>", unsafe_allow_html=True)

def rodape():
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="background:linear-gradient(135deg, {VERDE_ESCURO} 0%, {PRETO} 100%); padding:20px;
                border-radius:10px; border:2px solid {VERDE_HULK}; text-align:center; margin-top:20px;">
        <p style="color:{VERDE_CLARO};">🟢</p>
        <p style="color:{VERDE_HULK}; font-weight:bold;">AILSON PERSONAL TRAINNER</p>
        <p style="color:{BRANCO}; font-size:0.8rem;">© 2026 - Todos os direitos reservados</p>
        <p style="color:{AMARELO_ALERTA}; font-style:italic;">"QUANTO MAIS RAIVA, MAIS FORTE FICA!"</p>
    </div>
    """, unsafe_allow_html=True)