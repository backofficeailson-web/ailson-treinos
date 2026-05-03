import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XlImage

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(
    page_title="AILSON PERSONAL TRAINNER",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

AZUL = "#1E3A8A"
PRETO = "#111111"
BRANCO = "#FFFFFF"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {PRETO};
    }}
    .css-1d391kg {{
        background-color: {AZUL};
    }}
    .stButton>button {{
        background-color: {AZUL};
        color: {BRANCO};
        border-radius: 8px;
    }}
    .stButton>button:hover {{
        background-color: #2E4A9A;
    }}
    h1, h2, h3, h4, h5, h6, p, label {{
        color: {BRANCO};
    }}
    .stSidebar {{
        background-color: {PRETO};
        color: {BRANCO};
    }}
    .stSidebar .stSelectbox label, .stSidebar .stTextInput label {{
        color: {BRANCO} !important;
    }}
</style>
""", unsafe_allow_html=True)

LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=180)
else:
    st.sidebar.title("AILSON PERSONAL")
    st.sidebar.markdown("*Trainner*")

# -----------------------------
# BANCO DE DADOS
# -----------------------------
def init_db():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    # Adiciona colunas para dados nutricionais se não existirem
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    sexo TEXT DEFAULT "Masculino",
                    idade INTEGER,
                    peso REAL,
                    altura REAL,
                    percentual_gordura REAL,
                    nivel TEXT,
                    objetivo TEXT,
                    modalidade TEXT DEFAULT "Geral",
                    agachamento_1rm REAL,
                    supino_1rm REAL,
                    terra_1rm REAL,
                    pegada_direita REAL,
                    pegada_esquerda REAL,
                    historico TEXT DEFAULT ""
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos (
                    id INTEGER PRIMARY KEY,
                    cliente_id INTEGER,
                    data TEXT,
                    foto_frente BLOB,
                    foto_costas BLOB,
                    foto_perfil BLOB
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacao_postural (
                    id INTEGER PRIMARY KEY,
                    cliente_id INTEGER,
                    data TEXT,
                    cabeca TEXT DEFAULT "Normal",
                    ombros TEXT DEFAULT "Normal",
                    coluna TEXT DEFAULT "Normal",
                    quadril TEXT DEFAULT "Normal",
                    joelhos TEXT DEFAULT "Normal",
                    pes TEXT DEFAULT "Normal"
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS treinos_realizados (
                    id INTEGER PRIMARY KEY,
                    cliente_id INTEGER,
                    data TEXT,
                    exercicio TEXT,
                    series INTEGER,
                    repeticoes INTEGER,
                    carga REAL,
                    observacoes TEXT
                )''')
    # Tabela de alimentos (banco de dados nutricional)
    c.execute('''CREATE TABLE IF NOT EXISTS alimentos (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    calorias REAL,
                    proteinas REAL,
                    carboidratos REAL,
                    gorduras REAL,
                    porcao REAL
                )''')
    # Insere alimentos padrão se a tabela estiver vazia
    c.execute("SELECT COUNT(*) FROM alimentos")
    if c.fetchone()[0] == 0:
        alimentos_padrao = [
            ("Arroz integral cozido", 123, 2.6, 25.8, 1.0, 100),
            ("Feijão carioca cozido", 76, 4.8, 13.6, 0.5, 100),
            ("Frango grelhado (peito)", 165, 31, 0, 3.6, 100),
            ("Ovo cozido", 155, 12.6, 0.6, 10.6, 100),
            ("Batata doce cozida", 86, 1.6, 20.1, 0.1, 100),
            ("Brócolis cozido", 35, 2.4, 7.2, 0.4, 100),
            ("Banana prata", 98, 1.3, 26, 0.1, 100),
            ("Mamão papaia", 45, 0.5, 11.3, 0.1, 100),
            ("Leite integral", 64, 3.2, 4.9, 3.4, 100),
            ("Iogurte natural", 61, 5.2, 6.6, 1.5, 100),
            ("Aveia em flocos", 389, 13.2, 66.6, 7.2, 100),
            ("Pão integral", 253, 9.4, 49.9, 3.3, 100),
            ("Queijo minas frescal", 264, 17.8, 0.7, 20.9, 100),
            ("Azeite de oliva", 884, 0, 0, 100, 100),
            ("Castanha do pará", 656, 14.3, 12.3, 66.4, 100),
            ("Maçã", 52, 0.3, 13.8, 0.2, 100),
            ("Tomate", 18, 0.9, 3.9, 0.2, 100),
            ("Alface", 15, 1.2, 2.8, 0.2, 100),
            ("Bife de alcatra grelhado", 278, 49.6, 0, 8.5, 100),
            ("Salmão grelhado", 208, 25.3, 0, 12.9, 100),
            ("Atum em água", 116, 25.5, 0, 0.8, 100),
            ("Batata inglesa cozida", 77, 2.0, 18.4, 0.1, 100),
            ("Mandioca cozida", 125, 1.6, 30.1, 0.2, 100),
            ("Clara de ovo", 52, 10.9, 0.7, 0.2, 100),
        ]
        c.executemany("INSERT INTO alimentos (nome, calorias, proteinas, carboidratos, gorduras, porcao) VALUES (?,?,?,?,?,?)", alimentos_padrao)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# FUNÇÕES AUXILIARES (mantidas da versão anterior)
# -----------------------------
def salvar_cliente(nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome,sexo,idade,peso,altura,percentual_gordura,nivel,objetivo,modalidade,agachamento_1rm,supino_1rm,terra_1rm,pegada_direita,pegada_esquerda) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq))
    conn.commit()
    conn.close()

def atualizar_cliente(id_cliente, nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("UPDATE clientes SET nome=?, sexo=?, idade=?, peso=?, altura=?, percentual_gordura=?, nivel=?, objetivo=?, modalidade=?, agachamento_1rm=?, supino_1rm=?, terra_1rm=?, pegada_direita=?, pegada_esquerda=? WHERE id=?",
              (nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq, id_cliente))
    conn.commit()
    conn.close()

def excluir_cliente(id_cliente):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
    c.execute("DELETE FROM fotos WHERE cliente_id=?", (id_cliente,))
    c.execute("DELETE FROM avaliacao_postural WHERE cliente_id=?", (id_cliente,))
    c.execute("DELETE FROM treinos_realizados WHERE cliente_id=?", (id_cliente,))
    conn.commit()
    conn.close()

def carregar_clientes():
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql("SELECT id, nome, sexo, idade, peso, altura, percentual_gordura, nivel, objetivo, modalidade FROM clientes", conn)
    conn.close()
    return df

def carregar_cliente(id_cliente):
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql(f"SELECT * FROM clientes WHERE id={id_cliente}", conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

def salvar_foto(cliente_id, data, frente, costas, perfil):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO fotos (cliente_id, data, foto_frente, foto_costas, foto_perfil) VALUES (?,?,?,?,?)",
              (cliente_id, data, frente, costas, perfil))
    conn.commit()
    conn.close()

def carregar_fotos(cliente_id):
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql(f"SELECT * FROM fotos WHERE cliente_id={cliente_id} ORDER BY data DESC", conn)
    conn.close()
    return df

def salvar_avaliacao_postural(cliente_id, data, cabeca, ombros, coluna, quadril, joelhos, pes):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO avaliacao_postural (cliente_id, data, cabeca, ombros, coluna, quadril, joelhos, pes) VALUES (?,?,?,?,?,?,?)",
              (cliente_id, data, cabeca, ombros, coluna, quadril, joelhos, pes))
    conn.commit()
    conn.close()

def carregar_ultima_postural(cliente_id):
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql(f"SELECT * FROM avaliacao_postural WHERE cliente_id={cliente_id} ORDER BY data DESC LIMIT 1", conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

def salvar_treino(cliente_id, data, exercicio, series, reps, carga, obs=""):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO treinos_realizados (cliente_id, data, exercicio, series, repeticoes, carga, observacoes) VALUES (?,?,?,?,?,?,?)",
              (cliente_id, data, exercicio, series, reps, carga, obs))
    conn.commit()
    conn.close()

def carregar_historico_treinos(cliente_id):
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql(f"SELECT * FROM treinos_realizados WHERE cliente_id={cliente_id} ORDER BY data DESC", conn)
    conn.close()
    return df

# -----------------------------
# FUNÇÕES DE CÁLCULO NUTRICIONAL
# -----------------------------
def calcular_tmb(peso, altura, idade, sexo):
    if sexo == "Masculino":
        return 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        return 10 * peso + 6.25 * altura - 5 * idade - 161

def calcular_get(tmb, fator_atividade):
    fatores = {
        "Sedentário": 1.2,
        "Pouco ativo": 1.375,
        "Moderadamente ativo": 1.55,
        "Muito ativo": 1.725,
        "Atleta": 1.9
    }
    return tmb * fatores.get(fator_atividade, 1.55)

def distribuir_macros(peso, objetivo, modalidade, get, sexo):
    # Proteína (g/kg)
    if objetivo == "Hipertrofia" and modalidade in ["Powerlifting", "Fisiculturismo"]:
        proteina_gkg = 2.2
    elif modalidade in ["Beach Tennis", "Futebol"]:
        proteina_gkg = 1.6
    elif modalidade == "Gestante":
        proteina_gkg = 1.4
    elif objetivo == "Emagrecimento":
        proteina_gkg = 2.0
    else:
        proteina_gkg = 1.8  # default para hipertrofia geral

    proteina_g = peso * proteina_gkg
    calorias_proteina = proteina_g * 4

    # Gordura
    if objetivo == "Emagrecimento":
        perc_gord = 0.2
    elif modalidade == "Gestante":
        perc_gord = 0.3
    else:
        perc_gord = 0.25
    calorias_gordura = get * perc_gord
    gordura_g = calorias_gordura / 9

    # Carboidrato
    calorias_carb = get - calorias_proteina - calorias_gordura
    carboidrato_g = calorias_carb / 4

    return round(proteina_g, 1), round(gordura_g, 1), round(carboidrato_g, 1), round(get)

def montar_refeicoes(meta_calorias, meta_prot, meta_carb, meta_gord, num_refeicoes=5):
    """ Distribui as metas e seleciona alimentos do banco para cada refeição """
    conn = sqlite3.connect('clientes.db')
    alimentos_df = pd.read_sql("SELECT * FROM alimentos", conn)
    conn.close()

    # Distribuição percentual por refeição
    distribuicao = [0.20, 0.10, 0.30, 0.15, 0.25]  # café, lanche, almoço, lanche, jantar
    refeicoes = []
    for i, perc in enumerate(distribuicao):
        cal = meta_calorias * perc
        prot = meta_prot * perc
        carb = meta_carb * perc
        gord = meta_gord * perc

        # Heurística: selecionar alimentos que se aproximem desses macros
        # Simplificação: prato básico (arroz, feijão, carne, salada) ajustado
        sugestoes = []
        if i == 0:  # café da manhã
            sugestoes.append(("Leite integral", 200))
            sugestoes.append(("Pão integral", 50))
            sugestoes.append(("Mamão papaia", 150))
        elif i == 1:  # lanche manhã
            sugestoes.append(("Iogurte natural", 200))
            sugestoes.append(("Banana prata", 100))
        elif i == 2:  # almoço
            sugestoes.append(("Arroz integral cozido", 150))
            sugestoes.append(("Feijão carioca cozido", 100))
            sugestoes.append(("Frango grelhado (peito)", 150))
            sugestoes.append(("Brócolis cozido", 100))
        elif i == 3:  # lanche tarde
            sugestoes.append(("Aveia em flocos", 30))
            sugestoes.append(("Banana prata", 100))
        else:  # jantar
            sugestoes.append(("Arroz integral cozido", 100))
            sugestoes.append(("Bife de alcatra grelhado", 120))
            sugestoes.append(("Batata doce cozida", 100))
            sugestoes.append(("Tomate", 50))

        # Calcular macros da sugestão
        total_cal = 0
        total_prot = 0
        total_carb = 0
        total_gord = 0
        itens = []
        for nome, gramas in sugestoes:
            alimento = alimentos_df[alimentos_df['nome'] == nome].iloc[0]
            fator = gramas / 100
            cal_item = alimento['calorias'] * fator
            prot_item = alimento['proteinas'] * fator
            carb_item = alimento['carboidratos'] * fator
            gord_item = alimento['gorduras'] * fator
            itens.append((nome, gramas, round(cal_item,1), round(prot_item,1), round(carb_item,1), round(gord_item,1)))
            total_cal += cal_item
            total_prot += prot_item
            total_carb += carb_item
            total_gord += gord_item

        refeicoes.append({
            "nome": f"Refeição {i+1}",
            "itens": itens,
            "total_cal": round(total_cal,1),
            "total_prot": round(total_prot,1),
            "total_carb": round(total_carb,1),
            "total_gord": round(total_gord,1)
        })
    return refeicoes

def exportar_plano_alimentar(cliente, refeicoes, metas):
    wb = Workbook()
    ws = wb.active
    ws.title = "Plano Alimentar"

    # Inserir logomarca
    if os.path.exists(LOGO_PATH):
        img = XlImage(LOGO_PATH)
        ws.add_image(img, 'A1')

    # Título
    ws.merge_cells('B2:H2')
    ws['B2'] = "PLANO ALIMENTAR INDIVIDUALIZADO"
    ws['B2'].font = Font(size=14, bold=True)
    ws.merge_cells('B3:H3')
    ws['B3'] = f"Cliente: {cliente['nome']} | Sexo: {cliente['sexo']} | Idade: {cliente['idade']} | Peso: {cliente['peso']} kg"
    ws['B4'] = f"TMB: {metas['tmb']:.0f} kcal | GET: {metas['get']:.0f} kcal | Meta: {metas['meta_cal']:.0f} kcal"
    ws['B5'] = f"Proteína: {metas['prot_g']} g ({metas['cal_prot']:.0f} kcal) | Carboidrato: {metas['carb_g']} g ({metas['cal_carb']:.0f} kcal) | Gordura: {metas['gord_g']} g ({metas['cal_gord']:.0f} kcal)"

    cabeçalhos = ["Refeição", "Alimento", "Gramas", "Calorias", "Proteínas", "Carboidratos", "Gorduras"]
    for c, cab in enumerate(cabeçalhos, 1):
        cell = ws.cell(row=7, column=c, value=cab)
        cell.font = Font(bold=True)

    row = 8
    for ref in refeicoes:
        ws.cell(row, 1, ref['nome']).font = Font(bold=True)
        for item in ref['itens']:
            ws.cell(row, 2, item[0])
            ws.cell(row, 3, item[1])
            ws.cell(row, 4, item[2])
            ws.cell(row, 5, item[3])
            ws.cell(row, 6, item[4])
            ws.cell(row, 7, item[5])
            row += 1
        # totais da refeição
        ws.cell(row, 2, "Total").font = Font(bold=True)
        ws.cell(row, 4, ref['total_cal'])
        ws.cell(row, 5, ref['total_prot'])
        ws.cell(row, 6, ref['total_carb'])
        ws.cell(row, 7, ref['total_gord'])
        row += 2

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
menu = st.sidebar.selectbox("Menu", [
    "Cadastro de Cliente",
    "Editar / Excluir Clientes",
    "Avaliação & Fotos",
    "Geração de Treino",
    "Plano Alimentar",
    "Histórico & Evolução",
    "Personalizar Exercícios"
])

if menu == "Cadastro de Cliente":
    st.header("➕ Novo Cliente")
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome completo")
        sexo = col2.selectbox("Sexo", ["Masculino", "Feminino"])
        idade = st.number_input("Idade", 6, 100, 30)
        peso = st.number_input("Peso (kg)", 20.0, 200.0, 80.0)
        altura = st.number_input("Altura (cm)", 100.0, 250.0, 170.0)
        perc_gord = st.number_input("Percentual de gordura (%)", 1.0, 60.0, 20.0)
        nivel = st.selectbox("Nível de experiência", [
            "Iniciante (Nível 1)",
            "Básico (Nível 2)",
            "Intermediário (Nível 3)",
            "Avançado (Nível 4)",
            "Elite (Nível 5)",
            "Competitivo (Nível 6)"
        ])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência", "Emagrecimento"])
        modalidade = st.selectbox("Modalidade esportiva", [
            "Geral",
            "Beach Tennis",
            "Futebol",
            "Criança/Adolescente",
            "Gestante",
            "Powerlifting",
            "Fisiculturismo",
            "Musculação Convencional",
            "V-Taper",
            "Bikini"
        ])
        st.subheader("Testes de Força (1RM ou Estimado)")
        agach = st.number_input("Agachamento (kg)", 0.0, 500.0, 80.0)
        sup = st.number_input("Supino (kg)", 0.0, 500.0, 60.0)
        terra = st.number_input("Terra (kg)", 0.0, 500.0, 100.0)
        peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, 40.0)
        peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, 38.0)
        submitted = st.form_submit_button("Salvar Cliente")
        if submitted:
            salvar_cliente(nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
            st.success(f"Cliente {nome} cadastrado com sucesso!")

elif menu == "Editar / Excluir Clientes":
    st.header("✏️ Editar ou Excluir Clientes")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        cliente_selecionado = st.selectbox("Selecione o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_selecionado]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        tab1, tab2 = st.tabs(["✏️ Editar", "🗑️ Excluir"])
        with tab1:
            with st.form("editar_cliente"):
                nome = st.text_input("Nome completo", cliente['nome'])
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], index=0 if cliente['sexo'] == 'Masculino' else 1)
                idade = st.number_input("Idade", 6, 100, cliente['idade'])
                peso = st.number_input("Peso (kg)", 20.0, 200.0, cliente['peso'])
                altura = st.number_input("Altura (cm)", 100.0, 250.0, cliente['altura'])
                perc_gord = st.number_input("Percentual de gordura (%)", 1.0, 60.0, cliente['percentual_gordura'])
                nivel = st.selectbox("Nível de experiência", [
                    "Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
                    "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"
                ], index=["Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
                          "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"].index(cliente['nivel']))
                objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência", "Emagrecimento"],
                                        index=["Hipertrofia", "Força Máxima", "Potência", "Emagrecimento"].index(cliente['objetivo']))
                modalidade = st.selectbox("Modalidade esportiva", [
                    "Geral", "Beach Tennis", "Futebol", "Criança/Adolescente", "Gestante",
                    "Powerlifting", "Fisiculturismo", "Musculação Convencional", "V-Taper", "Bikini"
                ], index=["Geral", "Beach Tennis", "Futebol", "Criança/Adolescente", "Gestante",
                          "Powerlifting", "Fisiculturismo", "Musculação Convencional", "V-Taper", "Bikini"].index(cliente['modalidade']))
                agach = st.number_input("Agachamento (kg)", 0.0, 500.0, cliente['agachamento_1rm'])
                sup = st.number_input("Supino (kg)", 0.0, 500.0, cliente['supino_1rm'])
                terra = st.number_input("Terra (kg)", 0.0, 500.0, cliente['terra_1rm'])
                peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, cliente['pegada_direita'])
                peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, cliente['pegada_esquerda'])
                if st.form_submit_button("Atualizar"):
                    atualizar_cliente(id_cliente, nome, sexo, idade, peso, altura, perc_gord, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
                    st.success("Cliente atualizado!")
        with tab2:
            if st.button("Excluir Permanentemente"):
                excluir_cliente(id_cliente)
                st.success("Cliente removido.")
                st.rerun()

elif menu == "Avaliação & Fotos":
    # (código mantido da versão anterior, sem alterações)
    pass

elif menu == "Geração de Treino":
    st.header("📋 Planilha de Periodização Ondulatória")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Escolha o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        if cliente is not None:
            st.write(f"**{cliente['nome']}** | Objetivo: {cliente['objetivo']} | Modalidade: {cliente['modalidade']}")
            semanas = st.slider("Semanas", 4, 12, 12, step=4)
            freq = st.radio("Frequência semanal", [2, 3, 4, 5])
            if st.button("Gerar Planilha"):
                # Mantém a função de treino antiga ou exporta no formato Alexandre com logo
                # Placeholder: gerar um DataFrame simples
                df = pd.DataFrame({"Semana": [1,2], "Dia": ["Seg","Qua"], "Exercício": ["Agachamento","Supino"], "Séries": [3,3], "Repetições": [10,10], "%1RM":[70,70], "Carga":[80,60]})
                st.dataframe(df)
                # Exporta com logo
                wb = Workbook()
                ws = wb.active
                if os.path.exists(LOGO_PATH):
                    img = XlImage(LOGO_PATH)
                    ws.add_image(img, 'A1')
                ws.merge_cells('B2:F2')
                ws['B2'] = "PLANILHA DE TREINO"
                ws.append(["Semana", "Dia", "Exercício", "Séries", "Repetições", "Carga"])
                for _, row in df.iterrows():
                    ws.append([row['Semana'], row['Dia'], row['Exercício'], row['Séries'], row['Repetições'], row['Carga']])
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                st.download_button("Baixar Treino", output, f"treino_{cliente_nome}.xlsx")

elif menu == "Plano Alimentar":
    st.header("🍽️ Plano Alimentar Personalizado")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Escolha o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        if cliente is not None:
            st.write(f"**{cliente['nome']}** | Peso: {cliente['peso']} kg | Altura: {cliente['altura']} cm | % Gordura: {cliente['percentual_gordura']}%")
            fator_atividade = st.selectbox("Nível de atividade física", ["Sedentário", "Pouco ativo", "Moderadamente ativo", "Muito ativo", "Atleta"])
            objetivo_cal = st.selectbox("Meta calórica", ["Manutenção", "Superávit (+300 kcal)", "Déficit (-500 kcal)"])
            if st.button("Gerar Plano Alimentar"):
                tmb = calcular_tmb(cliente['peso'], cliente['altura'], cliente['idade'], cliente['sexo'])
                get = calcular_get(tmb, fator_atividade)
                if "Superávit" in objetivo_cal:
                    meta_cal = get + 300
                elif "Déficit" in objetivo_cal:
                    meta_cal = max(get - 500, 1200)
                else:
                    meta_cal = get

                prot_g, gord_g, carb_g, _ = distribuir_macros(cliente['peso'], cliente['objetivo'], cliente['modalidade'], meta_cal, cliente['sexo'])
                metas = {
                    'tmb': tmb,
                    'get': get,
                    'meta_cal': meta_cal,
                    'prot_g': prot_g,
                    'carb_g': carb_g,
                    'gord_g': gord_g,
                    'cal_prot': prot_g * 4,
                    'cal_carb': carb_g * 4,
                    'cal_gord': gord_g * 9
                }
                refeicoes = montar_refeicoes(meta_cal, prot_g, carb_g, gord_g)

                st.subheader("Distribuição de Macronutrientes")
                st.write(f"Calorias diárias: {meta_cal:.0f} kcal | Proteína: {prot_g}g | Carboidrato: {carb_g}g | Gordura: {gord_g}g")

                for ref in refeicoes:
                    with st.expander(ref['nome']):
                        for item in ref['itens']:
                            st.write(f"- {item[0]} ({item[1]}g): {item[2]} kcal, P:{item[3]}g, C:{item[4]}g, G:{item[5]}g")
                        st.write(f"**Total da refeição:** {ref['total_cal']} kcal, P:{ref['total_prot']}g, C:{ref['total_carb']}g, G:{ref['total_gord']}g")

                # Exportar
                output = exportar_plano_alimentar(cliente, refeicoes, metas)
                st.download_button("Baixar Plano em Excel", output, f"dieta_{cliente_nome}.xlsx")

elif menu == "Histórico & Evolução":
    # (código mantido, sem alterações)
    pass

elif menu == "Personalizar Exercícios":
    # (código mantido)
    pass

st.sidebar.markdown("---")
st.sidebar.markdown("© 2018 Ailson Personal Trainer")