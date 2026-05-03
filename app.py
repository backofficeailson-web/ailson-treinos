import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
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
# FUNÇÕES AUXILIARES (mantidas da versão anterior)
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
# GERADOR DE PLANILHA ONDULATÓRIA (formato PDF)
# -----------------------------
def gerar_planilha(cliente, semanas=12, frequencia=3):
    nivel = cliente['nivel'].split("(")[0].strip()
    agach = cliente['agachamento_1rm']
    sup = cliente['supino_1rm']
    terra = cliente['terra_1rm']

    # Faixas de RM por nível e frequência (baseadas no PDF)
    if nivel == "Iniciante":
        if frequencia == 2:
            rep_schemes = [
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None}
            ]
        elif frequencia == 3:
            rep_schemes = [{'Seg': (12,15), 'Qua': (18,20), 'Sex': (22,25)}] * 12
        else:
            rep_schemes = [
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)}
            ]
    elif nivel == "Intermediário":
        if frequencia == 2:
            rep_schemes = [
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None},
                {'Seg': (12,15), 'Qua': (18,20), 'Sex': None},
                {'Seg': (22,25), 'Qua': (12,15), 'Sex': None},
                {'Seg': (18,20), 'Qua': (22,25), 'Sex': None}
            ]
        else:
            rep_schemes = [{'Seg': (12,15), 'Qua': (18,20), 'Sex': (22,25)}] * 12
    else:  # Avançado
        if frequencia == 4:
            rep_schemes = [
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)},
                {'Seg': (4,6), 'Qua': (8,10), 'Sex': (4,6), 'Sab': (8,10)},
                {'Seg': (8,10), 'Qua': (8,10), 'Sex': (8,10), 'Sab': (8,10)},
                {'Seg': (12,15), 'Qua': (8,10), 'Sex': (12,15), 'Sab': (8,10)}
            ]
        else:
            rep_schemes = [{'Seg': (8,10), 'Qua': (12,15), 'Sex': (22,25)}] * 12

    def exercicios_do_dia(dia_semana):
        if dia_semana == "Seg":
            return ["Agachamento Livre (barra alta)", "Supino Reto", "Remada Curvada"]
        elif dia_semana == "Qua":
            return ["Levantamento Terra Tradicional", "Desenvolvimento Militar", "Stiff"]
        else:
            return ["Rosca Direta", "Tríceps Testa", "Puxada Alta", "Dips (Paralela)"]

    dados = []
    for semana in range(1, semanas+1):
        esquema = rep_schemes[semana-1]
        for dia_nome, faixa in esquema.items():
            if faixa is None:
                continue
            rep_min, rep_max = faixa
            intensidade = max(0.4, min(1.0, round((100 - 2.5 * rep_max) / 100, 2)))
            exs = exercicios_do_dia(dia_nome)
            for ex in exs:
                ex_lower = ex.lower()
                if "agachamento" in ex_lower:
                    base = agach
                elif "supino" in ex_lower:
                    base = sup
                elif "terra" in ex_lower or "stiff" in ex_lower:
                    base = terra
                elif "desenvolvimento" in ex_lower or "militar" in ex_lower:
                    base = sup * 0.7
                elif "remada" in ex_lower:
                    base = sup * 0.8
                elif "rosca" in ex_lower or "tríceps" in ex_lower or "testa" in ex_lower:
                    base = agach * 0.25
                elif "puxada" in ex_lower:
                    base = sup * 0.5
                elif "dips" in ex_lower or "barra fixa" in ex_lower:
                    base = 20.0
                else:
                    base = agach * 0.4

                carga = round(base * intensidade, 1)
                series = 3
                reps = rep_max
                volume = series * reps * carga
                dados.append([semana, f"Semana {semana}", dia_nome, ex, series, reps, carga, volume])

    df = pd.DataFrame(dados, columns=["Semana", "Microciclo", "Dia", "Exercício", "Séries", "Repetições", "Carga (kg)", "Volume Load"])
    # Totais por sessão
    df_total = df.groupby(["Semana", "Dia"])["Volume Load"].sum().reset_index()
    df_total["Exercício"] = "TOTAL"
    df_total["Séries"] = ""
    df_total["Repetições"] = ""
    df_total["Carga (kg)"] = ""
    df = pd.concat([df, df_total], ignore_index=True).sort_values(["Semana", "Dia"])
    return df

def get_table_download_link(df):
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="treino_{datetime.now().strftime("%Y%m%d")}.xlsx">📥 Baixar Planilha Excel</a>'
    return href

# -----------------------------
# INTERFACE STREAMLIT (completa)
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
            "Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
            "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"
        ])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência"])
        modalidade = st.selectbox("Modalidade esportiva", [
            "Geral", "Beach Tennis", "Futebol", "Criança/Adolescente", "Gestante",
            "Powerlifting", "Fisiculturismo", "Musculação Convencional", "V-Taper", "Bikini"
        ])
        st.subheader("Testes de Força (1RM ou Estimado)")
        agach = st.number_input("Agachamento (kg)", 0.0, 500.0, 80.0)
        sup = st.number_input("Supino (kg)", 0.0, 500.0, 60.0)
        terra = st.number_input("Terra (kg)", 0.0, 500.0, 100.0)
        peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, 40.0)
        peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, 38.0)
        if st.form_submit_button("Salvar Cliente"):
            salvar_cliente(nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
            st.success(f"Cliente {nome} cadastrado!")

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
                # índices para os selects
                niveis_lista = ["Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
                                "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"]
                idx_nivel = niveis_lista.index(cliente['nivel']) if cliente['nivel'] in niveis_lista else 0
                nivel = st.selectbox("Nível de experiência", niveis_lista, index=idx_nivel)
                obj_lista = ["Hipertrofia", "Força Máxima", "Potência"]
                idx_obj = obj_lista.index(cliente['objetivo']) if cliente['objetivo'] in obj_lista else 0
                objetivo = st.selectbox("Objetivo principal", obj_lista, index=idx_obj)
                mod_lista = ["Geral", "Beach Tennis", "Futebol", "Criança/Adolescente", "Gestante",
                             "Powerlifting", "Fisiculturismo", "Musculação Convencional", "V-Taper", "Bikini"]
                idx_mod = mod_lista.index(cliente.get('modalidade','Geral')) if cliente.get('modalidade','Geral') in mod_lista else 0
                modalidade = st.selectbox("Modalidade esportiva", mod_lista, index=idx_mod)
                agach = st.number_input("Agachamento (kg)", 0.0, 500.0, cliente['agachamento_1rm'])
                sup = st.number_input("Supino (kg)", 0.0, 500.0, cliente['supino_1rm'])
                terra = st.number_input("Terra (kg)", 0.0, 500.0, cliente['terra_1rm'])
                peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, cliente['pegada_direita'])
                peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, cliente['pegada_esquerda'])
                if st.form_submit_button("Atualizar Cliente"):
                    atualizar_cliente(id_cliente, nome, sexo, idade, nivel, objetivo, modalidade, agach, sup, terra, peg_dir, peg_esq)
                    st.success(f"Cliente {nome} atualizado!")
        with tab2:
            if st.button("Excluir Cliente Permanentemente"):
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
            st.success("Fotos salvas! Preencha a avaliação postural abaixo.")
            st.session_state.mostrar_postural = True

        if st.session_state.get('mostrar_postural', False):
            st.subheader("🔍 Avaliação Postural")
            with st.form("form_postural"):
                cabeca = st.selectbox("Cabeça", ["Normal", "Anteriorizada", "Inclinada D", "Inclinada E"])
                ombros = st.selectbox("Ombros", ["Normal", "Protrusos", "Elevado D", "Elevado E", "Desnivelados", "Escápula Alada D", "Escápula Alada E"])
                coluna = st.selectbox("Coluna", ["Normal", "Cifose", "Hiperlordose", "Escoliose"])
                quadril = st.selectbox("Quadril", ["Normal", "Anteroversão", "Retroversão", "Inclinação D", "Inclinação E"])
                joelhos = st.selectbox("Joelhos", ["Normal", "Valgo D", "Valgo E", "Varo D", "Varo E", "Recurvado"])
                pes = st.selectbox("Pés", ["Normal", "Pronado", "Supinado", "Cavo", "Plano"])
                if st.form_submit_button("Salvar Avaliação"):
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
    st.header("📋 Planilha de Periodização Ondulatória")
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_nome = st.selectbox("Escolha o cliente", clientes_df['nome'])
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        if cliente is not None:
            st.write(f"**{cliente['nome']}** | Sexo: {cliente.get('sexo','Masculino')} | Nível: {cliente['nivel']}")
            semanas = st.slider("Semanas", 4, 12, 12, step=4)
            freq = st.radio("Frequência semanal", [2, 3, 4])
            if st.button("Gerar Planilha"):
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

elif menu == "Personalizar Exercícios":
    st.header("🔧 Personalizar Banco de Exercícios")
    with st.form("add_exercicio"):
        categoria = st.selectbox("Categoria", list(EXERCICIOS.keys()))
        novo_ex = st.text_input("Nome do novo exercício")
        if st.form_submit_button("Adicionar") and novo_ex:
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
st.sidebar.markdown("© 2018 Ailson Personal Trainer")