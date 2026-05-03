import streamlit as st
import pandas as pd
from datetime import datetime
from database import execute_query
from alunos import pagina_lista_ativos

def pagina_avaliacao_postural():
    st.header("🏥 AVALIAÇÃO POSTURAL")
    clientes = pagina_lista_ativos()
    if not clientes:
        st.warning("Nenhum aluno ativo.")
        return
    df_clientes = pd.DataFrame(clientes, columns=['id','nome'])
    cliente_nome = st.selectbox("👤 Aluno", df_clientes['nome'])
    id_cliente = int(df_clientes[df_clientes['nome']==cliente_nome]['id'].values[0])
    tab = st.radio("Ação", ["Nova Avaliação","Histórico"], horizontal=True)
    if tab == "Nova Avaliação":
        with st.form("form_post"):
            data_post = st.date_input("Data", datetime.now())
            col1, col2 = st.columns(2)
            vista_anterior = col1.selectbox("Vista Anterior", ["Normal","Cabeça inclinada D","Cabeça inclinada E","Ombro D elevado","Ombro E elevado","Escoliose aparente"])
            vista_posterior = col2.selectbox("Vista Posterior", ["Normal","Escápula alada D","Escápula alada E","Escoliose torácica","Escoliose lombar","Diferença altura quadril"])
            col1, col2 = st.columns(2)
            vista_lat_dir = col1.selectbox("Vista Lateral Direita", ["Normal","Cabeça anteriorizada","Hipercifose torácica","Hiperlordose lombar","Joelhos recurvatum"])
            vista_lat_esq = col2.selectbox("Vista Lateral Esquerda", ["Normal","Cabeça anteriorizada","Hipercifose torácica","Hiperlordose lombar","Joelhos recurvatum"])
            col1, col2 = st.columns(2)
            cabeca = col1.selectbox("Cabeça/Pescoço", ["Alinhada","Anteriorizada","Inclinada D","Inclinada E","Rotação D","Rotação E"])
            ombros = col2.selectbox("Ombros", ["Alinhados","Protusos","Elevado D","Elevado E","Desnível"])
            col1, col2 = st.columns(2)
            coluna = col1.selectbox("Coluna Vertebral", ["Alinhada","Hipercifose","Hiperlordose","Escoliose torácica D","Escoliose torácica E","Retificação"])
            quadril = col2.selectbox("Quadril", ["Alinhado","Anteversão","Retroversão","Elevado D","Elevado E"])
            col1, col2 = st.columns(2)
            joelhos = col1.selectbox("Joelhos", ["Alinhados","Valgo D","Valgo E","Varo D","Varo E","Recurvatum"])
            pes = col2.selectbox("Pés", ["Normais","Plano D","Plano E","Cavo D","Cavo E","Pronado","Supinado"])
            obs = st.text_area("Observações")
            if st.form_submit_button("Salvar"):
                execute_query('''INSERT INTO avaliacao_postural 
                    (cliente_id, data, vista_anterior, vista_posterior, vista_lateral_direita,
                     vista_lateral_esquerda, cabeca, ombros, coluna, quadril, joelhos, pes, observacoes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (id_cliente, str(data_post), vista_anterior, vista_posterior, vista_lat_dir, vista_lat_esq,
                     cabeca, ombros, coluna, quadril, joelhos, pes, obs))
                st.success("Avaliação postural salva!")
    else:
        posturais = execute_query("SELECT * FROM avaliacao_postural WHERE cliente_id=? ORDER BY data DESC", (id_cliente,), fetch=True)
        if not posturais:
            st.info("Nenhuma.")
        else:
            colunas = ['id','cliente_id','data','vista_anterior','vista_posterior','vista_lateral_direita','vista_lateral_esquerda','cabeca','ombros','coluna','quadril','joelhos','pes','observacoes']
            df_post = pd.DataFrame(posturais, columns=colunas)
            for _, av in df_post.iterrows():
                with st.expander(f"{av['data']}"):
                    st.write(f"Anterior: {av['vista_anterior']} | Posterior: {av['vista_posterior']}")
                    st.write(f"Cabeça: {av['cabeca']} | Ombros: {av['ombros']} | Coluna: {av['coluna']}")