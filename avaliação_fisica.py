import streamlit as st
import pandas as pd
from datetime import datetime
from database import execute_query
from utils import calcular_imc, calcular_rcq, calcular_percentual_gordura, classificar_gordura, classificar_imc, classificar_rcq
from alunos import pagina_lista_ativos  # reutiliza para selecionar apenas ativos
import plotly.express as px

def pagina_avaliacao_fisica():
    st.header("📏 AVALIAÇÃO FÍSICA COMPLETA")
    clientes = pagina_lista_ativos()
    if not clientes:
        st.warning("Nenhum aluno ativo.")
        return
    df_clientes = pd.DataFrame(clientes, columns=['id','nome'])
    cliente_nome = st.selectbox("👤 Aluno", df_clientes['nome'])
    id_cliente = int(df_clientes[df_clientes['nome']==cliente_nome]['id'].values[0])
    cliente_data = execute_query("SELECT * FROM clientes WHERE id = ? AND ativo = 1", (id_cliente,), fetchone=True)
    if not cliente_data:
        st.error("Cliente não encontrado ou inativo.")
        return
    colunas_cliente = ['id','nome','telefone','mensalidade','vencimento','idade','nivel','objetivo','agachamento_1rm','supino_1rm','terra_1rm','pegada_direita','pegada_esquerda','historico','ativo']
    cliente = dict(zip(colunas_cliente, cliente_data))
    tab = st.radio("Ação", ["Nova Avaliação","Histórico"], horizontal=True)
    if tab == "Nova Avaliação":
        with st.form("form_av"):
            data_av = st.date_input("Data", datetime.now())
            st.markdown("### Dados Básicos")
            peso = st.number_input("Peso (kg)", 30.0, 300.0, 80.0, 0.1)
            altura = st.number_input("Altura (m)", 1.20, 2.50, 1.75, 0.01)
            st.markdown("### Circunferências (cm)")
            torax = st.number_input("Tórax", 30.0, 200.0, 95.0, 0.1, key='torax')
            cintura = st.number_input("Cintura", 30.0, 200.0, 80.0, 0.1, key='cintura')
            abdomen = st.number_input("Abdômen", 30.0, 200.0, 85.0, 0.1, key='abdomen')
            quadril = st.number_input("Quadril", 30.0, 200.0, 95.0, 0.1, key='quadril')
            braco_dir = st.number_input("Braço Direito", 10.0, 80.0, 35.0, 0.1, key='bdir')
            braco_esq = st.number_input("Braço Esquerdo", 10.0, 80.0, 35.0, 0.1, key='besq')
            coxa_dir = st.number_input("Coxa Direita", 20.0, 120.0, 55.0, 0.1, key='coxa_dir')
            coxa_esq = st.number_input("Coxa Esquerda", 20.0, 120.0, 55.0, 0.1, key='coxa_esq')
            pant_dir = st.number_input("Panturrilha Direita", 10.0, 60.0, 37.0, 0.1, key='pant_dir')
            pant_esq = st.number_input("Panturrilha Esquerda", 10.0, 60.0, 37.0, 0.1, key='pant_esq')
            st.markdown("### Dobras Cutâneas (mm)")
            triceps = st.number_input("Tríceps", 1.0, 80.0, 15.0, 0.1, key='tri')
            subescapular = st.number_input("Subescapular", 1.0, 80.0, 15.0, 0.1, key='sub')
            peitoral = st.number_input("Peitoral", 1.0, 80.0, 12.0, 0.1, key='peito')
            axilar_media = st.number_input("Axilar Média", 1.0, 80.0, 12.0, 0.1, key='axi')
            suprailiaca = st.number_input("Supra-ilíaca", 1.0, 80.0, 15.0, 0.1, key='suprail')
            abdominal = st.number_input("Abdominal", 1.0, 80.0, 20.0, 0.1, key='abdom')
            coxa = st.number_input("Coxa", 1.0, 80.0, 18.0, 0.1, key='coxa_dobra')
            biceps = st.number_input("Bíceps", 1.0, 80.0, 10.0, 0.1, key='bic')
            perna = st.number_input("Perna", 1.0, 80.0, 15.0, 0.1, key='perna')
            obs = st.text_area("Observações")
            if st.form_submit_button("Salvar"):
                execute_query('''INSERT INTO avaliacao_fisica 
                    (cliente_id, data, peso, altura, torax, cintura, abdomen, quadril,
                     braco_direito, braco_esquerdo, coxa_direita, coxa_esquerda,
                     panturrilha_direita, panturrilha_esquerda, triceps, subescapular,
                     peitoral, axilar_media, suprailiaca, abdominal, coxa, biceps, perna, observacoes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (id_cliente, str(data_av), peso, altura, torax, cintura, abdomen, quadril,
                     braco_dir, braco_esq, coxa_dir, coxa_esq, pant_dir, pant_esq,
                     triceps, subescapular, peitoral, axilar_media, suprailiaca, abdominal, coxa,
                     biceps, perna, obs))
                dados_calc = {'idade':cliente['idade'],'sexo':'M','peso':peso,'altura':altura,
                              'cintura':cintura,'quadril':quadril,'triceps':triceps,'subescapular':subescapular,
                              'peitoral':peitoral,'axilar_media':axilar_media,'suprailiaca':suprailiaca,
                              'abdominal':abdominal,'coxa':coxa}
                imc = calcular_imc(peso, altura)
                rcq = calcular_rcq(cintura, quadril)
                resultados = calcular_percentual_gordura(dados_calc)
                col1,col2,col3 = st.columns(3)
                col1.metric("IMC", f"{imc:.1f}", classificar_imc(imc))
                col2.metric("RCQ", f"{rcq:.2f}", classificar_rcq(rcq))
                primeiro = list(resultados.keys())[0]
                col3.metric(primeiro, f"{resultados[primeiro]:.1f}%", classificar_gordura(resultados[primeiro],'M',cliente['idade']))
                st.dataframe(pd.DataFrame([{'Protocolo':k, '% Gordura':v, 'Classificação':classificar_gordura(v,'M',cliente['idade'])} for k,v in resultados.items()]), use_container_width=True, hide_index=True)
    else:
        avs = execute_query("SELECT * FROM avaliacao_fisica WHERE cliente_id=? ORDER BY data DESC", (id_cliente,), fetch=True)
        if not avs:
            st.info("Nenhuma avaliação encontrada.")
        else:
            colunas_av = ['id','cliente_id','data','peso','altura','torax','cintura','abdomen','quadril','braco_direito','braco_esquerdo','coxa_direita','coxa_esquerda','panturrilha_direita','panturrilha_esquerda','triceps','subescapular','peitoral','axilar_media','suprailiaca','abdominal','coxa','biceps','perna','observacoes']
            df_av = pd.DataFrame(avs, columns=colunas_av)
            # Gráfico de evolução
            st.subheader("📈 Evolução das Medidas")
            fig = px.line(df_av, x='data', y=['peso','cintura','abdomen','quadril'], markers=True)
            st.plotly_chart(fig, use_container_width=True)
            for _, av in df_av.iterrows():
                with st.expander(f"{av['data']} - {av['peso']}kg"):
                    st.write(f"Cintura: {av['cintura']}cm | Abdômen: {av['abdomen']}cm | Quadril: {av['quadril']}cm")
                    st.write(f"Tríceps: {av['triceps']}mm | Peitoral: {av['peitoral']}mm | Abdominal: {av['abdominal']}mm | Coxa: {av['coxa']}mm")