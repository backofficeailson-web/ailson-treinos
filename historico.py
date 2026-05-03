import streamlit as st
import pandas as pd
from database import execute_query
from alunos import pagina_lista_ativos
from utils import classificar_gordura

def pagina_historico():
    st.header("📈 HISTÓRICO DO CLIENTE")
    clientes = pagina_lista_ativos()
    if not clientes:
        st.warning("Nenhum aluno.")
        return
    df_clientes = pd.DataFrame(clientes, columns=['id','nome'])
    nome = st.selectbox("👤 Selecione o aluno", df_clientes['nome'])
    id_cliente = int(df_clientes[df_clientes['nome']==nome]['id'].values[0])
    cliente_data = execute_query("SELECT * FROM clientes WHERE id = ? AND ativo = 1", (id_cliente,), fetchone=True)
    if not cliente_data:
        st.error("Cliente não encontrado.")
        return
    colunas = ['id','nome','telefone','mensalidade','vencimento','idade','nivel','objetivo','agachamento_1rm','supino_1rm','terra_1rm','pegada_direita','pegada_esquerda','historico','ativo']
    cliente = dict(zip(colunas, cliente_data))
    st.markdown("### 🏋️ Força Máxima (1RM)")
    col1,col2,col3 = st.columns(3)
    col1.metric("Agachamento", f"{cliente['agachamento_1rm']} kg")
    col2.metric("Supino", f"{cliente['supino_1rm']} kg")
    col3.metric("Terra", f"{cliente['terra_1rm']} kg")
    
    # Evolução das avaliações (gráfico)
    avs = execute_query("SELECT data, peso, cintura, abdomen, quadril FROM avaliacao_fisica WHERE cliente_id = ? ORDER BY data ASC", (id_cliente,), fetch=True)
    if avs:
        df_av = pd.DataFrame(avs, columns=['data','peso','cintura','abdomen','quadril'])
        st.subheader("📊 Evolução das Medidas")
        fig = px.line(df_av, x='data', y=['peso','cintura','abdomen','quadril'], markers=True)
        st.plotly_chart(fig, use_container_width=True)