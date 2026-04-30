import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
import random

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

def init_db():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    idade INTEGER,
                    nivel TEXT,
                    objetivo TEXT,
                    agachamento_1rm REAL,
                    supino_1rm REAL,
                    terra_1rm REAL,
                    pegada_direita REAL,
                    pegada_esquerda REAL,
                    historico TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos (
                    id INTEGER PRIMARY KEY,
                    cliente_id INTEGER,
                    data TEXT,
                    foto_frente BLOB,
                    foto_costas BLOB,
                    foto_perfil BLOB
                )''')
    conn.commit()
    conn.close()

init_db()

def salvar_cliente(nome, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome,idade,nivel,objetivo,agachamento_1rm,supino_1rm,terra_1rm,pegada_direita,pegada_esquerda,historico) VALUES (?,?,?,?,?,?,?,?,?,?)",
              (nome, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq, ""))
    conn.commit()
    conn.close()

def carregar_clientes():
    conn = sqlite3.connect('clientes.db')
    df = pd.read_sql("SELECT id, nome, nivel, objetivo FROM clientes", conn)
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

EXERCICIOS = {
    "Agachamento": ["Agachamento Livre (barra alta)", "Agachamento Frontal", "Agachamento Pausado", "Box Squat"],
    "Supino": ["Supino Reto", "Supino Fechado", "Supino Pausado", "Board Press"],
    "Terra": ["Levantamento Terra Tradicional", "Terra Sumô", "Terra Déficit", "Terra Pausado"],
    "Desenvolvimento": ["Desenvolvimento Militar", "Desenvolvimento com Halteres"],
    "Remada": ["Remada Curvada", "Remada Nórdica", "Remada Alta"],
    "Acessórios": ["Stiff", "Good Morning", "Avanço com Barra", "Afundo"],
    "Braços": ["Rosca Direta", "Tríceps Testa", "Tríceps Corda (Cross)"],
    "Torre Única": ["Puxada Alta", "Crucifixo Unilateral", "Remada Baixa", "Rosca Polia"],
    "Barra Fixa / Paralela": ["Barra Fixa com Peso", "Dips (Paralela)"],
    "Pegada": ["Esmagamento (Gripper)", "Pinça (Anilhas)", "Sustentação (Barra)"]
}

EQUIPAMENTOS = ["Correntes", "Elásticos", "Caixas"]

def gerar_planilha(cliente, semanas=4, frequencia=3):
    objetivo = cliente['objetivo']
    agach = cliente['agachamento_1rm']
    sup = cliente['supino_1rm']
    terra = cliente['terra_1rm']

    if objetivo == "Hipertrofia":
        rep_schemes_base = [
            {'series':3, 'reps':10, 'intensidade':0.65},
            {'series':4, 'reps':8, 'intensidade':0.70},
            {'series':5, 'reps':5, 'intensidade':0.78},
            {'series':3, 'reps':12, 'intensidade':0.60}
        ]
    elif objetivo == "Força Máxima":
        rep_schemes_base = [
            {'series':4, 'reps':6, 'intensidade':0.80},
            {'series':5, 'reps':4, 'intensidade':0.85},
            {'series':3, 'reps':3, 'intensidade':0.90},
            {'series':5, 'reps':2, 'intensidade':0.93}
        ]
    else:  # Potência
        rep_schemes_base = [
            {'series':6, 'reps':3, 'intensidade':0.50},
            {'series':8, 'reps':2, 'intensidade':0.55},
            {'series':5, 'reps':3, 'intensidade':0.60},
            {'series':10, 'reps':1, 'intensidade':0.70}
        ]

    planilha = []
    for semana in range(1, semanas+1):
        # Calcular ciclo atual (0-based)
        ciclo = (semana - 1) // 4
        indice_semana = (semana - 1) % 4
        scheme_base = rep_schemes_base[indice_semana]

        # Progressão: aumentar intensidade em 2% por ciclo
        fator_progressao = 1 + (ciclo * 0.02)
        intensidade = round(scheme_base['intensidade'] * fator_progressao, 2)

        for dia in range(1, frequencia+1):
            if dia == 1:
                ex_principais = list(EXERCICIOS['Agachamento'] + EXERCICIOS['Supino'])
            elif dia == 2:
                ex_principais = list(EXERCICIOS['Terra'] + EXERCICIOS['Desenvolvimento'])
            else:
                ex_principais = list(EXERCICIOS['Remada'] + EXERCICIOS['Acessórios'])

            if dia == 3:
                ex_principais += EXERCICIOS['Braços']
            else:
                ex_principais += EXERCICIOS['Torre Única'] + EXERCICIOS['Barra Fixa / Paralela']

            for ex in ex_principais[:4]:
                if "Agachamento" in ex:
                    carga_base = agach
                elif "Supino" in ex:
                    carga_base = sup
                elif "Terra" in ex:
                    carga_base = terra
                else:
                    carga_base = agach * 0.5

                carga = round(carga_base * intensidade, 2)
                planilha.append({
                    'Semana': semana,
                    'Dia': dia,
                    'Exercício': ex,
                    'Séries': scheme_base['series'],
                    'Repetições': scheme_base['reps'],
                    '% 1RM': int(intensidade*100),
                    'Carga (kg)': carga
                })

    df = pd.DataFrame(planilha)

def get_table_download_link(df):
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="treino_{datetime.now().strftime("%Y%m%d")}.xlsx">📥 Baixar Planilha Excel</a>'
    return href

menu = st.sidebar.selectbox("Menu", ["Cadastro de Cliente", "Avaliação & Fotos", "Geração de Treino", "Histórico & Evolução"])

if menu == "Cadastro de Cliente":
    st.header("➕ Novo Cliente")
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome completo")
        idade = col2.number_input("Idade", 12, 100, 30)
        nivel = st.selectbox("Nível de experiência", [
            "Iniciante (Nível 1)",
            "Básico (Nível 2)",
            "Intermediário (Nível 3)",
            "Avançado (Nível 4)",
            "Elite (Nível 5)",
            "Competitivo (Nível 6)"
        ])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência"])
        st.subheader("Testes de Força (1RM ou Estimado)")
        agach = st.number_input("Agachamento (kg)", 0.0, 500.0, 80.0)
        sup = st.number_input("Supino (kg)", 0.0, 500.0, 60.0)
        terra = st.number_input("Terra (kg)", 0.0, 500.0, 100.0)
        peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, 40.0)
        peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, 38.0)
        submitted = st.form_submit_button("Salvar Cliente")
        if submitted:
            salvar_cliente(nome, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq)
            st.success(f"Cliente {nome} cadastrado com sucesso!")

elif menu == "Avaliação & Fotos":
    st.header("📸 Fotos Avaliativas")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Nenhum cliente cadastrado. Cadastre primeiro.")
    else:
        cliente_selecionado = st.selectbox("Selecione o cliente", clientes_df['nome'].tolist())
        id_cliente = clientes_df[clientes_df['nome'] == cliente_selecionado]['id'].values[0]
        data_foto = st.date_input("Data da foto", datetime.now())
        col1, col2, col3 = st.columns(3)
        frente = col1.file_uploader("Frente", type=['jpg','jpeg','png'])
        costas = col2.file_uploader("Costas", type=['jpg','jpeg','png'])
        perfil = col3.file_uploader("Perfil", type=['jpg','jpeg','png'])
        if st.button("Salvar Fotos"):
            if not os.path.exists("fotos"):
                os.makedirs("fotos")
            for img, tipo in [(frente, "frente"), (costas, "costas"), (perfil, "perfil")]:
                if img:
                    img_pil = Image.open(img)
                    img_pil.save(f"fotos/{cliente_selecionado}_{data_foto}_{tipo}.png")
            st.success("Fotos salvas com sucesso!")

elif menu == "Geração de Treino":
    st.header("📋 Gerar Planilha Ondulatória")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Escolha o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        if cliente is not None:
            st.write(f"**Objetivo:** {cliente['objetivo']} | **Nível:** {cliente['nivel']}")
            semanas = st.slider("Semanas de treino", 4, 12, 4, step=4)
            freq = st.radio("Dias por semana", [3, 4, 5])
            if st.button("Gerar Treino"):
                df = gerar_planilha(cliente, semanas=semanas, frequencia=freq)
                st.dataframe(df)
                st.markdown(get_table_download_link(df), unsafe_allow_html=True)

elif menu == "Histórico & Evolução":
    st.header("📈 Histórico do Cliente")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        nome = st.selectbox("Cliente", clientes_df['nome'])
        cliente = carregar_cliente(int(clientes_df[clientes_df['nome']==nome]['id'].values[0]))
        col1, col2, col3 = st.columns(3)
        col1.metric("Agachamento 1RM", f"{cliente['agachamento_1rm']} kg")
        col2.metric("Supino 1RM", f"{cliente['supino_1rm']} kg")
        col3.metric("Terra 1RM", f"{cliente['terra_1rm']} kg")
        st.info("Gráficos de evolução serão disponibilizados em breve.")

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Ailson Personal Trainer")
