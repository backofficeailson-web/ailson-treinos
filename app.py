import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(
    page_title="AILSON PERSONAL TRAINNER",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

AZUL = "#1E3A8A"      # Ajuste para o tom exato da sua logo
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

# Logomarca
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
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    sexo TEXT DEFAULT "Masculino",
                    idade INTEGER,
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
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
def salvar_cliente(nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome,sexo,idade,nivel,objetivo,modalidade,agachamento_1rm,supino_1rm,terra_1rm,pegada_direita,pegada_esquerda) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
              (nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq))
    conn.commit()
    conn.close()

def atualizar_cliente(id_cliente, nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("UPDATE clientes SET nome=?, sexo=?, idade=?, nivel=?, objetivo=?, modalidade=?, agachamento_1rm=?, supino_1rm=?, terra_1rm=?, pegada_direita=?, pegada_esquerda=? WHERE id=?",
              (nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq, id_cliente))
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
    df = pd.read_sql("SELECT id, nome, nivel, objetivo, modalidade, sexo FROM clientes", conn)
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
# EXERCÍCIOS PADRÃO (customizável)
# -----------------------------
if 'EXERCICIOS' not in st.session_state:
    st.session_state.EXERCICIOS = {
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

EXERCICIOS = st.session_state.EXERCICIOS

# -----------------------------
# GERADOR DE PLANILHA ONDULATÓRIA
# -----------------------------
def gerar_planilha(cliente, semanas=4, frequencia=3):
    objetivo = cliente['objetivo']
    modalidade = cliente.get('modalidade', 'Geral')
    agach = cliente['agachamento_1rm']
    sup = cliente['supino_1rm']
    terra = cliente['terra_1rm']

    postural = carregar_ultima_postural(cliente['id'])
    desvios = {
        'cabeca': postural['cabeca'] if postural is not None else 'Normal',
        'ombros': postural['ombros'] if postural is not None else 'Normal',
        'coluna': postural['coluna'] if postural is not None else 'Normal',
        'quadril': postural['quadril'] if postural is not None else 'Normal',
        'joelhos': postural['joelhos'] if postural is not None else 'Normal',
        'pes': postural['pes'] if postural is not None else 'Normal'
    }

    corretivos = []
    if desvios['cabeca'] != 'Normal':
        corretivos += ["Alongamento de esternocleidomastóideo", "Fortalecimento de flexores profundos do pescoço"]
    if desvios['ombros'] != 'Normal':
        corretivos += ["Fortalecimento de romboides (remada baixa)", "Alongamento de peitoral menor"]
    if desvios['coluna'] != 'Normal':
        corretivos += ["Mobilidade torácica (extensão sobre rolo)", "Fortalecimento de eretores espinhais"]
    if desvios['quadril'] != 'Normal':
        corretivos += ["Alongamento de flexores do quadril", "Fortalecimento de glúteo médio"]
    if desvios['joelhos'] != 'Normal':
        corretivos += ["Fortalecimento de vasto medial", "Alongamento de isquiotibiais"]
    if desvios['pes'] != 'Normal':
        corretivos += ["Fortalecimento intrínseco do pé", "Massagem plantar"]

    # Ajustes por modalidade
    if modalidade == "Beach Tennis":
        ex_extra = ["Rotação com Medicine Ball", "Salto Lateral", "Agachamento Unilateral"]
        freq = max(frequencia, 3)
    elif modalidade == "Futebol":
        ex_extra = ["Sprint Resistido (elástico)", "Agachamento Búlgaro", "Salto Vertical"]
        freq = max(frequencia, 3)
    elif modalidade == "Gestante":
        ex_extra = ["Agachamento com Peso Corporal", "Remada Baixa (elástico)", "Alongamento Ativo"]
        freq = 3
    elif modalidade == "Criança/Adolescente":
        ex_extra = ["Agachamento com Bastão", "Supino com Halteres Leves", "Barra Fixa Assistida"]
        freq = 2
    elif modalidade == "Powerlifting":
        ex_extra = ["Agachamento Pausado", "Supino Fechado", "Board Press", "Terra Sumô", "Terra Déficit", "Lockout Terra"]
        freq = 4
    elif modalidade == "Fisiculturismo":
        ex_extra = ["Elevação Lateral", "Crucifixo Inclinado", "Rosca Scott", "Tríceps Francês", "Cadeira Extensora", "Mesa Flexora", "Panturrilha em Pé"]
        freq = 6
    elif modalidade == "Musculação Convencional":
        ex_extra = ["Supino Inclinado com Halteres", "Remada Cavalinho", "Desenvolvimento Arnold", "Rosca Martelo", "Tríceps Testa", "Cadeira Extensora", "Mesa Flexora", "Abdominal"]
        freq = max(frequencia, 3)
    elif modalidade == "V-Taper":
        ex_extra = ["Desenvolvimento Arnold", "Elevação Lateral", "Remada Alta", "Pullover", "Crucifixo Inverso"]
        freq = 5
    elif modalidade == "Bikini":
        ex_extra = ["Glúteo no Cabo", "Abdutora com Elástico", "Stiff Unilateral", "Agachamento Búlgaro", "Ponte Pélvica com Barra"]
        freq = 5
    else:
        ex_extra = []
        freq = frequencia

    # Esquema de séries/reps
    if modalidade == "Powerlifting":
        rep_schemes_base = [
            {'series':5, 'reps':3, 'intensidade':0.85},
            {'series':4, 'reps':2, 'intensidade':0.90},
            {'series':3, 'reps':1, 'intensidade':0.95},
            {'series':5, 'reps':2, 'intensidade':0.88}
        ]
    elif modalidade in ["Fisiculturismo", "V-Taper", "Bikini"]:
        rep_schemes_base = [
            {'series':4, 'reps':12, 'intensidade':0.60},
            {'series':3, 'reps':10, 'intensidade':0.65},
            {'series':5, 'reps':8, 'intensidade':0.70},
            {'series':3, 'reps':15, 'intensidade':0.55}
        ]
    else:
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
        ciclo = (semana - 1) // 4
        indice_semana = (semana - 1) % 4
        scheme_base = rep_schemes_base[indice_semana]
        fator_progressao = 1 + (ciclo * 0.02)
        intensidade = round(scheme_base['intensidade'] * fator_progressao, 2)

        for dia in range(1, freq+1):
            # Escolha dos exercícios do dia conforme modalidade
            if modalidade == "Powerlifting":
                if dia == 1:
                    ex_principais = ["Agachamento Livre (barra alta)", "Agachamento Pausado", "Box Squat"]
                elif dia == 2:
                    ex_principais = ["Supino Reto", "Supino Fechado", "Board Press"]
                elif dia == 3:
                    ex_principais = ["Levantamento Terra Tradicional", "Terra Sumô", "Terra Déficit"]
                else:
                    ex_principais = ["Rosca Direta", "Tríceps Testa", "Barra Fixa com Peso", "Dips (Paralela)", "Lockout Terra"]

            elif modalidade == "Fisiculturismo":
                if dia == 1:  # Peito + Tríceps
                    ex_principais = ["Supino Reto", "Supino Fechado", "Crucifixo Inclinado", "Tríceps Francês", "Tríceps Corda (Cross)"]
                elif dia == 2:  # Costas + Bíceps
                    ex_principais = ["Remada Curvada", "Remada Nórdica", "Levantamento Terra Tradicional", "Rosca Direta", "Rosca Scott"]
                elif dia == 3:  # Pernas
                    ex_principais = ["Agachamento Livre (barra alta)", "Stiff", "Cadeira Extensora", "Mesa Flexora", "Panturrilha em Pé"]
                elif dia == 4:  # Ombros + Abdômen
                    ex_principais = ["Desenvolvimento Militar", "Elevação Lateral", "Abdominal"]
                elif dia == 5:  # Pernas posterior
                    ex_principais = ["Stiff", "Good Morning", "Mesa Flexora"]
                else:
                    ex_principais = ["Rosca Direta", "Tríceps Francês", "Rosca Scott"]

            elif modalidade == "V-Taper":
                if dia == 1:  # Ombros
                    ex_principais = ["Desenvolvimento Arnold", "Elevação Lateral", "Remada Alta", "Pullover"]
                elif dia == 2:  # Costas
                    ex_principais = ["Remada Curvada", "Remada Nórdica", "Pullover"]
                elif dia == 3:  # Peito (menos ênfase)
                    ex_principais = ["Supino Reto", "Crucifixo Inclinado"]
                elif dia == 4:  # Pernas (manutenção)
                    ex_principais = ["Agachamento Livre (barra alta)", "Stiff"]
                else:  # Braços + Abdômen
                    ex_principais = ["Rosca Direta", "Tríceps Testa", "Abdominal"]

            elif modalidade == "Bikini":
                if dia == 1:  # Glúteos e posteriores
                    ex_principais = ["Agachamento Búlgaro", "Stiff Unilateral", "Ponte Pélvica com Barra", "Abdutora com Elástico"]
                elif dia == 2:  # Quadríceps e panturrilhas
                    ex_principais = ["Agachamento Livre (barra alta)", "Cadeira Extensora", "Panturrilha em Pé"]
                elif dia == 3:  # Superiores (manutenção)
                    ex_principais = ["Supino Reto", "Remada Curvada"]
                elif dia == 4:  # Glúteos e isquiotibiais novamente
                    ex_principais = ["Glúteo no Cabo", "Mesa Flexora", "Afundo", "Ponte Pélvica com Barra"]
                else:
                    ex_principais = ["Alongamento Ativo", "Mobilidade de Quadril"]

            elif modalidade == "Musculação Convencional":
                if dia == 1:
                    ex_principais = ["Agachamento Livre (barra alta)", "Supino Reto", "Desenvolvimento Arnold"]
                elif dia == 2:
                    ex_principais = ["Levantamento Terra Tradicional", "Remada Curvada", "Rosca Martelo"]
                else:
                    ex_principais = ["Stiff", "Tríceps Testa", "Cadeira Extensora", "Mesa Flexora", "Abdominal"]

            else:  # Geral / Beach Tennis / Futebol / Gestante / Criança etc.
                if dia == 1:
                    ex_principais = list(EXERCICIOS['Agachamento'][:2]) + list(EXERCICIOS['Supino'][:2])
                elif dia == 2:
                    ex_principais = list(EXERCICIOS['Terra'][:2]) + list(EXERCICIOS['Desenvolvimento'][:2])
                else:
                    ex_principais = list(EXERCICIOS['Remada'][:2]) + list(EXERCICIOS['Acessórios'][:2])

                if ex_extra and dia <= 2:
                    ex_principais += ex_extra

                if dia == freq:
                    ex_principais += list(EXERCICIOS['Braços'])
                else:
                    ex_principais += list(EXERCICIOS['Torre Única'][:2]) + list(EXERCICIOS['Barra Fixa / Paralela'][:2])

            # Adiciona corretivos no primeiro dia da semana
            if dia == 1 and corretivos:
                ex_principais += corretivos

            for ex in ex_principais[:6]:
                # Determinação da carga base (resumido)
                ex_lower = ex.lower()
                if "agachamento" in ex_lower or "búlgaro" in ex_lower or "salto" in ex_lower or "sprint" in ex_lower:
                    carga_base = agach
                elif "supino" in ex_lower or "board" in ex_lower or "crucifixo" in ex_lower or "inclinado" in ex_lower:
                    carga_base = sup
                elif "terra" in ex_lower or "sumô" in ex_lower or "déficit" in ex_lower or "deficit" in ex_lower or "lockout" in ex_lower or "stiff" in ex_lower or "good morning" in ex_lower:
                    carga_base = terra
                elif "rosca" in ex_lower or "tríceps" in ex_lower or "testa" in ex_lower:
                    carga_base = agach * 0.3
                elif "puxada" in ex_lower or "pulley" in ex_lower:
                    carga_base = sup * 0.5
                elif "remada" in ex_lower:
                    carga_base = sup * 0.7
                elif "elevação" in ex_lower or "desenvolvimento" in ex_lower or "arnold" in ex_lower or "militar" in ex_lower:
                    carga_base = sup * 0.4
                elif "cadeira" in ex_lower or "mesa" in ex_lower or "panturrilha" in ex_lower:
                    carga_base = agach * 0.4
                elif "glúteo" in ex_lower or "abdutora" in ex_lower or "ponte" in ex_lower:
                    carga_base = agach * 0.3
                elif "abdominal" in ex_lower or "alongamento" in ex_lower or "mobilidade" in ex_lower or "fortalecimento" in ex_lower or "massagem" in ex_lower:
                    carga_base = 0
                else:
                    carga_base = agach * 0.5

                carga = round(carga_base * intensidade, 2) if carga_base > 0 else 0
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

    # Adiciona nome do ciclo (onda)
    def nome_ciclo(s):
        onda = (s - 1) % 4
        if onda == 0:
            return "Volume"
        elif onda == 1:
            return "Transição"
        elif onda == 2:
            return "Força"
        else:
            return "Recuperação"

    df['Ciclo'] = df['Semana'].apply(nome_ciclo)
    df = df[['Semana', 'Ciclo', 'Dia', 'Exercício', 'Séries', 'Repetições', '% 1RM', 'Carga (kg)']]
    return df

def get_table_download_link(df):
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="treino_{datetime.now().strftime("%Y%m%d")}.xlsx">📥 Baixar Planilha Excel</a>'
    return href

# -----------------------------
# INTERFACE STREAMLIT
# -----------------------------
menu = st.sidebar.selectbox("Menu", [
    "Cadastro de Cliente",
    "Editar / Excluir Clientes",
    "Avaliação & Fotos",
    "Geração de Treino",
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
        nivel = st.selectbox("Nível de experiência", [
            "Iniciante (Nível 1)",
            "Básico (Nível 2)",
            "Intermediário (Nível 3)",
            "Avançado (Nível 4)",
            "Elite (Nível 5)",
            "Competitivo (Nível 6)"
        ])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência"])
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
            salvar_cliente(nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
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
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], index=0 if cliente.get('sexo','Masculino')=='Masculino' else 1)
                idade = st.number_input("Idade", 6, 100, cliente['idade'])
                nivel_atual = cliente['nivel']
                niveis_lista = ["Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
                                "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"]
                try:
                    idx_nivel = niveis_lista.index(nivel_atual)
                except:
                    idx_nivel = 0
                nivel = st.selectbox("Nível de experiência", niveis_lista, index=idx_nivel)
                objetivo_atual = cliente['objetivo']
                obj_lista = ["Hipertrofia", "Força Máxima", "Potência"]
                try:
                    idx_obj = obj_lista.index(objetivo_atual)
                except:
                    idx_obj = 0
                objetivo = st.selectbox("Objetivo principal", obj_lista, index=idx_obj)
                modalidade_atual = cliente.get('modalidade', 'Geral')
                mod_lista = ["Geral", "Beach Tennis", "Futebol", "Criança/Adolescente", "Gestante",
                             "Powerlifting", "Fisiculturismo", "Musculação Convencional", "V-Taper", "Bikini"]
                try:
                    idx_mod = mod_lista.index(modalidade_atual)
                except:
                    idx_mod = 0
                modalidade = st.selectbox("Modalidade esportiva", mod_lista, index=idx_mod)
                agach = st.number_input("Agachamento (kg)", 0.0, 500.0, cliente['agachamento_1rm'])
                sup = st.number_input("Supino (kg)", 0.0, 500.0, cliente['supino_1rm'])
                terra = st.number_input("Terra (kg)", 0.0, 500.0, cliente['terra_1rm'])
                peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, cliente['pegada_direita'])
                peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, cliente['pegada_esquerda'])
                atualizar = st.form_submit_button("Atualizar Cliente")
                if atualizar:
                    atualizar_cliente(id_cliente, nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
                    st.success(f"Cliente {nome} atualizado com sucesso!")
        with tab2:
            if st.button("Excluir Cliente Permanentemente", type="primary"):
                excluir_cliente(id_cliente)
                st.success(f"Cliente {cliente['nome']} excluído.")
                st.rerun()

elif menu == "Avaliação & Fotos":
    st.header("📸 Fotos Avaliativas e Análise Postural")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        cliente_selecionado = st.selectbox("Selecione o cliente", clientes_df['nome'])
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
            st.success("Fotos salvas! Agora preencha a avaliação postural abaixo.")
            st.session_state.mostrar_postural = True

        if st.session_state.get('mostrar_postural', False):
            st.subheader("🔍 Avaliação Postural")
            with st.form("form_postural"):
                st.write("Marque os desvios observados em cada segmento:")
                cabeca = st.selectbox("Cabeça", ["Normal", "Anteriorizada", "Inclinada D", "Inclinada E"])
                ombros = st.selectbox("Ombros", ["Normal", "Protrusos", "Elevado D", "Elevado E", "Desnivelados", "Escápula Alada D", "Escápula Alada E"])
                coluna = st.selectbox("Coluna", ["Normal", "Cifose", "Hiperlordose", "Escoliose"])
                quadril = st.selectbox("Quadril", ["Normal", "Anteroversão", "Retroversão", "Inclinação D", "Inclinação E"])
                joelhos = st.selectbox("Joelhos", ["Normal", "Valgo D", "Valgo E", "Varo D", "Varo E", "Recurvado"])
                pes = st.selectbox("Pés", ["Normal", "Pronado", "Supinado", "Cavo", "Plano"])
                salvar_avaliacao = st.form_submit_button("Salvar Avaliação")
                if salvar_avaliacao:
                    salvar_avaliacao_postural(id_cliente, data_foto.strftime("%Y-%m-%d"), cabeca, ombros, coluna, quadril, joelhos, pes)
                    st.success("Avaliação postural registrada!")
                    st.session_state.mostrar_postural = False
                    st.rerun()

        # Comparação de fotos
        st.subheader("📊 Comparação de Fotos")
        fotos_df = carregar_fotos(id_cliente)
        if not fotos_df.empty:
            datas = fotos_df['data'].unique()
            if len(datas) >= 2:
                data1 = st.selectbox("Data 1", datas, key="data1")
                data2 = st.selectbox("Data 2", [d for d in datas if d != data1], key="data2")
                if data1 and data2:
                    c1, c2, c3 = st.columns(3)
                    for col, tipo in [(c1, 'frente'), (c2, 'costas'), (c3, 'perfil')]:
                        img1 = fotos_df[(fotos_df['data']==data1)][f'foto_{tipo}'].iloc[0] if not fotos_df[(fotos_df['data']==data1)].empty else None
                        img2 = fotos_df[(fotos_df['data']==data2)][f'foto_{tipo}'].iloc[0] if not fotos_df[(fotos_df['data']==data2)].empty else None
                        if img1:
                            col.image(img1, caption=f"{data1} - {tipo}", use_column_width=True)
                        if img2:
                            col.image(img2, caption=f"{data2} - {tipo}", use_column_width=True)

elif menu == "Geração de Treino":
    st.header("📋 Gerar Planilha Ondulatória Personalizada")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Escolha o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        if cliente is not None:
            st.write(f"**{cliente['nome']}** | Sexo: {cliente.get('sexo','Masculino')} | Objetivo: {cliente['objetivo']} | Modalidade: {cliente.get('modalidade', 'Geral')} | Nível: {cliente['nivel']}")
            postural = carregar_ultima_postural(id_cliente)
            if postural is not None:
                st.info(f"📌 Última avaliação postural: {postural['data']} – O treino incluirá corretivos.")
            else:
                st.warning("Nenhuma avaliação postural registrada. O treino será gerado sem corretivos.")

            semanas = st.slider("Semanas de treino", 4, 12, 4, step=4)
            freq = st.radio("Dias por semana (sugestão automática será usada se diferente)", [3, 4, 5])
            if st.button("Gerar Treino"):
                df = gerar_planilha(cliente, semanas=semanas, frequencia=freq)
                # Exibição por semanas
                for semana in sorted(df['Semana'].unique()):
                    with st.expander(f"🗓️ Semana {semana} – {df[df['Semana']==semana]['Ciclo'].iloc[0]}"):
                        st.dataframe(df[df['Semana']==semana].drop(columns=['Semana','Ciclo']), use_container_width=True)
                st.markdown(get_table_download_link(df), unsafe_allow_html=True)

elif menu == "Histórico & Evolução":
    st.header("📈 Histórico do Cliente")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Nenhum cliente cadastrado.")
    else:
        nome = st.selectbox("Cliente", clientes_df['nome'])
        id_cliente = int(clientes_df[clientes_df['nome']==nome]['id'].values[0])
        cliente = carregar_cliente(id_cliente)

        col1, col2, col3 = st.columns(3)
        col1.metric("Agachamento 1RM", f"{cliente['agachamento_1rm']} kg")
        col2.metric("Supino 1RM", f"{cliente['supino_1rm']} kg")
        col3.metric("Terra 1RM", f"{cliente['terra_1rm']} kg")

        st.subheader("✍️ Registrar Treino Realizado")
        with st.form("registrar_treino"):
            data = st.date_input("Data", datetime.now())
            exercicio = st.text_input("Exercício")
            series = st.number_input("Séries", 1, 20, 3)
            reps = st.number_input("Repetições", 1, 50, 10)
            carga = st.number_input("Carga (kg)", 0.0, 500.0, 60.0)
            obs = st.text_area("Observações")
            if st.form_submit_button("Registrar"):
                salvar_treino(id_cliente, data.strftime("%Y-%m-%d"), exercicio, series, reps, carga, obs)
                st.success("Treino registrado!")

        st.subheader("📊 Evolução de Cargas")
        historico = carregar_historico_treinos(id_cliente)
        if not historico.empty:
            exercicio_filtro = st.selectbox("Exercício", historico['exercicio'].unique())
            df_filtrado = historico[historico['exercicio'] == exercicio_filtro]
            if not df_filtrado.empty:
                fig, ax = plt.subplots()
                ax.plot(pd.to_datetime(df_filtrado['data']), df_filtrado['carga'], marker='o', color=AZUL)
                ax.set_title(f"Progresso - {exercicio_filtro}", color=BRANCO)
                ax.set_xlabel("Data", color=BRANCO)
                ax.set_ylabel("Carga (kg)", color=BRANCO)
                ax.tick_params(colors=BRANCO)
                ax.set_facecolor(PRETO)
                fig.patch.set_facecolor(PRETO)
                st.pyplot(fig)
        else:
            st.info("Nenhum treino registrado ainda.")

elif menu == "Personalizar Exercícios":
    st.header("🔧 Personalizar Banco de Exercícios")
    st.write("Adicione ou remova exercícios das categorias abaixo.")

    with st.form("add_exercicio"):
        categoria = st.selectbox("Categoria", list(EXERCICIOS.keys()))
        novo_ex = st.text_input("Nome do novo exercício")
        adicionar = st.form_submit_button("Adicionar")
        if adicionar and novo_ex:
            st.session_state.EXERCICIOS[categoria].append(novo_ex)
            st.success(f"Exercício '{novo_ex}' adicionado à categoria '{categoria}'.")
            st.rerun()

    st.subheader("Exercícios atuais")
    for cat, exs in st.session_state.EXERCICIOS.items():
        with st.expander(f"{cat} ({len(exs)} exercícios)"):
            for ex in exs:
                col1, col2 = st.columns([4,1])
                col1.write(ex)
                if col2.button("🗑️", key=f"del_{cat}_{ex}"):
                    st.session_state.EXERCICIOS[cat].remove(ex)
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Ailson Personal Trainer")