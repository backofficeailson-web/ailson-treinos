import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from database import execute_query
from utils import extrair_dia_vencimento, cached_execute_query
from config import VERDE_HULK, AMARELO_ALERTA, VERMELHO, CINZA_MEDIO

def mostrar_dashboard():
    st.title("📊 Dashboard Financeiro")
    # Usando cache
    dados = cached_execute_query("SELECT id, nome, telefone, mensalidade, vencimento, nivel, objetivo FROM clientes WHERE ativo = 1 ORDER BY nome")
    df = pd.DataFrame(dados, columns=['id','nome','telefone','mensalidade','vencimento','nivel','objetivo'])
    
    total_alunos = len(df)
    faturamento = df['mensalidade'].sum() if not df.empty else 0
    media_mensal = df['mensalidade'].mean() if not df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos", total_alunos)
    col2.metric("Faturamento Mensal", f"R$ {faturamento:,.2f}")
    col3.metric("Mensalidade Média", f"R$ {media_mensal:,.2f}")

    if not df.empty:
        status_list, prox_datas, dias_rest = [], [], []
        for _, row in df.iterrows():
            dia = extrair_dia_vencimento(row['vencimento'])
            if dia is None:
                status_list.append("data_invalida")
                prox_datas.append("Indefinido")
                dias_rest.append("?")
            else:
                hoje = date.today()
                try:
                    prox_data = date(hoje.year, hoje.month, dia)
                    if prox_data < hoje:
                        prox_data = date(hoje.year, hoje.month+1, dia) if hoje.month<12 else date(hoje.year+1,1,dia)
                except:
                    status_list.append("data_invalida")
                    prox_datas.append("Inválido")
                    dias_rest.append("?")
                    continue
                dias = (prox_data - hoje).days
                if dias < 0: status = "vencido"
                elif dias <= 5: status = "proximo"
                else: status = "em_dia"
                status_list.append(status)
                prox_datas.append(prox_data.strftime('%d/%m/%Y'))
                dias_rest.append(dias)
        df['status'] = status_list
        df['prox_venc'] = prox_datas
        df['dias_rest'] = dias_rest
        
        vencidos = len(df[df['status']=='vencido'])
        proximos = len(df[df['status']=='proximo'])
        em_dia = len(df[df['status']=='em_dia'])
        invalidos = len(df[df['status']=='data_invalida'])
        
        st.subheader("🚨 Alertas de Vencimento")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🔴 Vencidos", vencidos)
        c2.metric("🟡 Próximos (5 dias)", proximos)
        c3.metric("🟢 Em dia", em_dia)
        c4.metric("❌ Data inválida", invalidos)
        
        st.dataframe(df[['nome','mensalidade','vencimento','prox_venc','dias_rest','status']], use_container_width=True)
        
        status_df = pd.DataFrame({'Status':['Vencido','Próximo (5 dias)','Em dia','Data inválida'],
                                  'Quantidade':[vencidos, proximos, em_dia, invalidos]})
        fig = px.bar(status_df, x='Status', y='Quantidade', color='Status',
                     color_discrete_map={'Vencido':VERMELHO, 'Próximo (5 dias)':AMARELO_ALERTA,
                                         'Em dia':VERDE_HULK, 'Data inválida':CINZA_MEDIO})
        st.plotly_chart(fig, use_container_width=True)