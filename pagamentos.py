import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import execute_query
from alunos import pagina_lista_ativos

def pagina_pagamentos():
    st.header("💰 Pagamentos")
    clientes = pagina_lista_ativos()
    if not clientes:
        st.warning("Nenhum aluno ativo.")
        return
    df_clientes = pd.DataFrame(clientes, columns=['id','nome'])
    
    tab = st.radio("Ação", ["Registrar Pagamento", "Histórico de Pagamentos"], horizontal=True)
    
    if tab == "Registrar Pagamento":
        with st.form("form_pag"):
            cliente_nome = st.selectbox("Aluno", df_clientes['nome'])
            id_cliente = int(df_clientes[df_clientes['nome']==cliente_nome]['id'].values[0])
            data_pag = st.date_input("Data do Pagamento", datetime.now())
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, value=100.0)
            status = st.selectbox("Situação", ["Pago", "Pendente", "Atrasado"])
            forma = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão", "Transferência"])
            obs = st.text_area("Observação")
            if st.form_submit_button("Registrar"):
                execute_query("INSERT INTO pagamentos (cliente_id, data, valor, status, forma, observacao) VALUES (?,?,?,?,?,?)",
                              (id_cliente, str(data_pag), valor, status, forma, obs))
                st.success("Pagamento registrado!")
    else:
        cliente_nome = st.selectbox("Filtrar por aluno (opcional)", ["Todos"] + list(df_clientes['nome']))
        if cliente_nome == "Todos":
            pagamentos = execute_query("""
                SELECT p.id, c.nome, p.data, p.valor, p.status, p.forma, p.observacao
                FROM pagamentos p JOIN clientes c ON p.cliente_id = c.id
                ORDER BY p.data DESC
            """, fetch=True)
        else:
            id_cliente = int(df_clientes[df_clientes['nome']==cliente_nome]['id'].values[0])
            pagamentos = execute_query("""
                SELECT p.id, c.nome, p.data, p.valor, p.status, p.forma, p.observacao
                FROM pagamentos p JOIN clientes c ON p.cliente_id = c.id
                WHERE p.cliente_id = ?
                ORDER BY p.data DESC
            """, (id_cliente,), fetch=True)
        if pagamentos:
            df_pag = pd.DataFrame(pagamentos, columns=['ID','Aluno','Data','Valor','Status','Forma','Observação'])
            st.dataframe(df_pag, use_container_width=True)
        else:
            st.info("Nenhum pagamento registrado.")
