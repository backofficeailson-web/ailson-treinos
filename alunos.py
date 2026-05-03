import streamlit as st
import pandas as pd
from database import execute_query

def pagina_cadastro():
    st.title("➕ Cadastro de Aluno")
    with st.form("cadastro"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome completo")
        telefone = col2.text_input("Telefone")
        col1, col2 = st.columns(2)
        mensalidade = col1.number_input("Mensalidade (R$)", min_value=0.0, step=10.0, value=100.0)
        vencimento = col2.text_input("Vencimento (ex: dia 10)")
        idade = st.number_input("Idade", 12, 100, 30)
        nivel = st.selectbox("Nível de experiência", [
            "Iniciante (Nível 1)","Básico (Nível 2)","Intermediário (Nível 3)",
            "Avançado (Nível 4)","Elite (Nível 5)","Competitivo (Nível 6)"])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia","Força Máxima","Potência"])
        st.subheader("Testes de Força (1RM)")
        col1,col2,col3 = st.columns(3)
        agach = col1.number_input("Agachamento (kg)", 0.0, 500.0, 80.0)
        sup = col2.number_input("Supino (kg)", 0.0, 500.0, 60.0)
        terra = col3.number_input("Terra (kg)", 0.0, 500.0, 100.0)
        peg_dir = st.number_input("Pegada Mão Direita (kg)", 0.0, 200.0, 40.0)
        peg_esq = st.number_input("Pegada Mão Esquerda (kg)", 0.0, 200.0, 38.0)
        if st.form_submit_button("💾 SALVAR"):
            if nome.strip() == "":
                st.warning("Informe o nome")
            else:
                execute_query(
                    "INSERT INTO clientes (nome,telefone,mensalidade,vencimento,idade,nivel,objetivo,agachamento_1rm,supino_1rm,terra_1rm,pegada_direita,pegada_esquerda,historico) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (nome, telefone, mensalidade, vencimento, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq, ""))
                st.success(f"Aluno {nome} cadastrado!")

def pagina_gerenciar():
    st.title("📋 Gerenciar Alunos")
    # Mostra apenas ativos
    dados = execute_query("SELECT id, nome, telefone, mensalidade, vencimento, nivel, objetivo FROM clientes WHERE ativo = 1 ORDER BY nome", fetch=True)
    if not dados:
        st.info("Nenhum aluno.")
        return
    df = pd.DataFrame(dados, columns=['id','nome','telefone','mensalidade','vencimento','nivel','objetivo'])
    st.dataframe(df, use_container_width=True)
    aluno_id = st.number_input("ID do aluno a desativar/reativar", min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Desativar (soft delete)"):
            execute_query("UPDATE clientes SET ativo = 0 WHERE id = ?", (aluno_id,))
            st.success("Aluno desativado!")
            st.rerun()
    with col2:
        if st.button("✅ Reativar"):
            execute_query("UPDATE clientes SET ativo = 1 WHERE id = ?", (aluno_id,))
            st.success("Aluno reativado!")
            st.rerun()

def pagina_lista_ativos():
    """Função auxiliar para carregar lista de alunos ativos para selects em outros módulos."""
    return execute_query("SELECT id, nome FROM clientes WHERE ativo = 1 ORDER BY nome", fetch=True)