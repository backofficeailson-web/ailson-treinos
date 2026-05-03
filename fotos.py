import streamlit as st
import pandas as pd
from datetime import datetime
from database import execute_query
from alunos import pagina_lista_ativos
from config import UPLOAD_DIR
import os
from PIL import Image

def pagina_fotos():
    st.header("📸 FOTOS AVALIATIVAS")
    clientes = pagina_lista_ativos()
    if not clientes:
        st.warning("Nenhum aluno ativo.")
        return
    df_clientes = pd.DataFrame(clientes, columns=['id','nome'])
    cliente_nome = st.selectbox("👤 Aluno", df_clientes['nome'])
    id_cliente = int(df_clientes[df_clientes['nome']==cliente_nome]['id'].values[0])
    tab = st.radio("Ação", ["Nova Foto","Galeria"], horizontal=True)
    if tab == "Nova Foto":
        data_foto = st.date_input("Data", datetime.now())
        col1, col2, col3 = st.columns(3)
        with col1:
            frente = st.file_uploader("Frente", type=['jpg','jpeg','png'], key="frente")
            if frente: st.image(frente, width=200)
        with col2:
            costas = st.file_uploader("Costas", type=['jpg','jpeg','png'], key="costas")
            if costas: st.image(costas, width=200)
        with col3:
            perfil = st.file_uploader("Perfil", type=['jpg','jpeg','png'], key="perfil")
            if perfil: st.image(perfil, width=200)
        if st.button("Salvar Fotos"):
            for img, tipo in [(frente,"Frente"),(costas,"Costas"),(perfil,"Perfil")]:
                if img:
                    # Cria pasta do aluno
                    aluno_dir = os.path.join(UPLOAD_DIR, str(id_cliente))
                    os.makedirs(aluno_dir, exist_ok=True)
                    # Salva arquivo com nome único
                    file_name = f"{tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    file_path = os.path.join(aluno_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(img.read())
                    # Salva path no banco
                    execute_query("INSERT INTO fotos (cliente_id, data, tipo, foto_path) VALUES (?,?,?,?)",
                                  (id_cliente, str(data_foto), tipo, file_path))
            st.success("Fotos salvas!")
    else:
        fotos = execute_query("SELECT * FROM fotos WHERE cliente_id=? ORDER BY data DESC", (id_cliente,), fetch=True)
        if not fotos:
            st.info("Nenhuma foto.")
        else:
            datas = list(set(f[3] for f in fotos))
            for data in datas:
                with st.expander(data):
                    cols = st.columns(3)
                    fotos_data = [f for f in fotos if f[3]==data]
                    for i, f in enumerate(fotos_data):
                        with cols[i % 3]:
                            if os.path.exists(f[4]):
                                st.image(f[4], caption=f[3], width=250)
                            else:
                                st.warning(f"Foto não encontrada: {f[4]}")