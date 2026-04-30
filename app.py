import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
import random
from io import BytesIO

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

def gerar_planilha_ondulatoria(cliente, semanas=4, frequencia=3):
    objetivo = cliente['objetivo']
    agach = cliente['agachamento_1rm']
    sup = cliente['supino_1rm']
    terra = cliente['terra_1rm']
    nivel_str = cliente['nivel']
    
    try:
        nivel_num = int(nivel_str.split('Nível ')[1].split(')')[0])
    except:
        nivel_num = 3
    
    fator_volume = {1: 0.7, 2: 0.85, 3: 1.0, 4: 1.15, 5: 1.3, 6: 1.5}.get(nivel_num, 1.0)
    
    if objetivo == "Hipertrofia":
        fases = [
            {'foco': 'Resistencia Muscular', 'series_base': 3, 'rep_range': '12-15', 'intensidade': 0.60, 'descanso': '45-60s'},
            {'foco': 'Hipertrofia Tensional', 'series_base': 4, 'rep_range': '8-10', 'intensidade': 0.70, 'descanso': '60-90s'},
            {'foco': 'Hipertrofia Metabolica', 'series_base': 4, 'rep_range': '10-12', 'intensidade': 0.65, 'descanso': '45-60s'},
            {'foco': 'Choque/Densidade', 'series_base': 5, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '90s'}
        ]
    elif objetivo == "Força Máxima":
        fases = [
            {'foco': 'Preparacao/Volume', 'series_base': 4, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '2-3min'},
            {'foco': 'Forca Pura', 'series_base': 5, 'rep_range': '4-5', 'intensidade': 0.85, 'descanso': '3-4min'},
            {'foco': 'Forca Maxima', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.92, 'descanso': '4-5min'},
            {'foco': 'Descarga Tecnica', 'series_base': 3, 'rep_range': '3-4', 'intensidade': 0.80, 'descanso': '2-3min'}
        ]
    else:
        fases = [
            {'foco': 'Forca-Velocidade', 'series_base': 5, 'rep_range': '3-5', 'intensidade': 0.50, 'descanso': '2min'},
            {'foco': 'Velocidade-Forca', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.60, 'descanso': '2-3min'},
            {'foco': 'Pico de Potencia', 'series_base': 4, 'rep_range': '3-4', 'intensidade': 0.55, 'descanso': '2min'},
            {'foco': 'Transferencia', 'series_base': 5, 'rep_range': '5-6', 'intensidade': 0.45, 'descanso': '90s'}
        ]

    dias_treino = {
        1: {
            'nome': 'Dia 1 - Membros Inferiores (Foco Agachamento)',
            'exercicios': [
                {'nome': 'Agachamento Livre (barra alta)', 'tipo': 'Principal', 'base': 'agach', 'fator': 1.0},
                {'nome': 'Agachamento Frontal', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.80},
                {'nome': 'Avanco com Barra', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.50},
                {'nome': 'Stiff', 'tipo': 'Acessorio', 'base': 'terra', 'fator': 0.60},
                {'nome': 'Good Morning', 'tipo': 'Acessorio', 'base': 'terra', 'fator': 0.45},
                {'nome': 'Esmagamento (Gripper)', 'tipo': 'Finalizador', 'base': 'pegada', 'fator': 0.0},
            ]
        },
        2: {
            'nome': 'Dia 2 - Membros Superiores (Foco Supino)',
            'exercicios': [
                {'nome': 'Supino Reto', 'tipo': 'Principal', 'base': 'sup', 'fator': 1.0},
                {'nome': 'Supino Fechado', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.80},
                {'nome': 'Desenvolvimento Militar', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.55},
                {'nome': 'Triceps Testa', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.30},
                {'nome': 'Triceps Corda (Cross)', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.20},
                {'nome': 'Pinca (Anilhas)', 'tipo': 'Finalizador', 'base': 'pegada', 'fator': 0.0},
            ]
        },
        3: {
            'nome': 'Dia 3 - Dorsais/Posterior (Foco Terra)',
            'exercicios': [
                {'nome': 'Levantamento Terra Tradicional', 'tipo': 'Principal', 'base': 'terra', 'fator': 1.0},
                {'nome': 'Terra Sumo', 'tipo': 'Acessorio', 'base': 'terra', 'fator': 0.85},
                {'nome': 'Remada Curvada', 'tipo': 'Acessorio', 'base': 'terra', 'fator': 0.50},
                {'nome': 'Barra Fixa com Peso', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.30},
                {'nome': 'Rosca Direta', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.15},
                {'nome': 'Sustentacao (Barra)', 'tipo': 'Finalizador', 'base': 'pegada', 'fator': 0.0},
            ]
        }
    }

    if frequencia >= 4:
        dias_treino[4] = {
            'nome': 'Dia 4 - Variacao Inferior (Terra/Agachamento)',
            'exercicios': [
                {'nome': 'Terra Deficit', 'tipo': 'Principal', 'base': 'terra', 'fator': 0.90},
                {'nome': 'Box Squat', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.85},
                {'nome': 'Agachamento Pausado', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.75},
                {'nome': 'Remada Nordica', 'tipo': 'Acessorio', 'base': 'terra', 'fator': 0.40},
                {'nome': 'Afundo', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.45},
                {'nome': 'Dips (Paralela)', 'tipo': 'Finalizador', 'base': 'agach', 'fator': 0.25},
            ]
        }
    if frequencia == 5:
        dias_treino[5] = {
            'nome': 'Dia 5 - Isolamento/Especializacao',
            'exercicios': [
                {'nome': 'Board Press', 'tipo': 'Principal', 'base': 'sup', 'fator': 0.85},
                {'nome': 'Supino Pausado', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.75},
                {'nome': 'Puxada Alta', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.30},
                {'nome': 'Remada Baixa', 'tipo': 'Acessorio', 'base': 'agach', 'fator': 0.25},
                {'nome': 'Crucifixo Unilateral', 'tipo': 'Acessorio', 'base': 'sup', 'fator': 0.15},
                {'nome': 'Remada Alta', 'tipo': 'Finalizador', 'base': 'agach', 'fator': 0.20},
            ]
        }
    
    if objetivo == "Força Máxima":
        for dia in dias_treino:
            dias_treino[dia]['exercicios'] = [ex for ex in dias_treino[dia]['exercicios'] if ex['tipo'] in ['Principal', 'Acessorio']][:4]

    planilhas_por_semana = {}

    for semana in range(1, semanas + 1):
        idx_fase = (semana - 1) % 4
        fase = fases[idx_fase]
        
        ciclo = (semana - 1) // 4
        fator_progressao = 1.0 + (ciclo * 0.025)
        
        registros_semana = []
        
        for dia in range(1, frequencia + 1):
            dia_info = dias_treino.get(dia, dias_treino[1])
            
            for ex in dia_info['exercicios']:
                nome_ex = ex['nome']
                tipo = ex['tipo']
                base = ex['base']
                fator = ex['fator']
                
                if base == 'agach':
                    carga_base = agach
                elif base == 'sup':
                    carga_base = sup
                elif base == 'terra':
                    carga_base = terra
                elif base == 'pegada':
                    carga_base = 0
                else:
                    carga_base = agach * 0.5
                
                if tipo == 'Principal':
                    intensidade_final = fase['intensidade']
                    series = max(2, int(fase['series_base'] * fator_volume))
                    repeticoes = fase['rep_range']
                    descanso = fase['descanso']
                elif tipo == 'Acessorio':
                    intensidade_final = fase['intensidade'] * 0.85
                    series = max(2, int((fase['series_base'] - 1) * fator_volume))
                    rep_range_split = fase['rep_range'].split('-')
                    if len(rep_range_split) == 2:
                        repeticoes = f"{int(rep_range_split[0]) + 2}-{int(rep_range_split[1]) + 2}"
                    else:
                        repeticoes = str(int(fase['rep_range']) + 2)
                    descanso = '60-90s'
                else:
                    intensidade_final = fase['intensidade'] * 0.6
                    series = 3
                    repeticoes = '12-15'
                    descanso = '45-60s'
                
                if carga_base > 0:
                    carga = round(carga_base * fator * intensidade_final * fator_progressao, 1)
                    carga = max(carga, 1.0)
                else:
                    carga = 'Peso Corporal'
                
                registros_semana.append({
                    'Dia': dia,
                    'Tipo': tipo,
                    'Exercicio': nome_ex,
                    'Series': series,
                    'Repeticoes': repeticoes,
                    '% 1RM': f"{int(intensidade_final * 100)}%",
                    'Carga (kg)': carga if isinstance(carga, str) else f"{carga:.1f}",
                    'Descanso': descanso,
                    'Observacao': ''
                })
        
        df_semana = pd.DataFrame(registros_semana)
        planilhas_por_semana[f'Semana {semana}'] = df_semana

    return planilhas_por_semana


def get_table_download_link(planilhas_dict, nome_cliente="cliente"):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in planilhas_dict.items():
            aba_nome = nome_aba.replace(' ', '_')[:31]
            df.to_excel(writer, sheet_name=aba_nome, index=False)
            
            worksheet = writer.sheets[aba_nome]
            
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + i)].width = min(max_length + 2, 40)
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    data_formatada = datetime.now().strftime("%d-%m-%Y")
    nome_arquivo = f"Treino_{nome_cliente}_{data_formatada}.xlsx"
    
    href = f'''
    <div style="text-align: center; padding: 20px;">
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
           download="{nome_arquivo}"
           style="
               background-color: #1E3A8A;
               color: white;
               padding: 15px 30px;
               text-decoration: none;
               border-radius: 8px;
               font-size: 18px;
               font-weight: bold;
               display: inline-block;
               margin: 10px;
           ">
            📥 BAIXAR PLANILHA COMPLETA (COM ABAS POR SEMANA)
        </a>
        <br><small style="color: #aaa;">Arquivo Excel com {len(planilhas_dict)} abas - Uma para cada semana</small>
    </div>
    '''
    return href


# -----------------------------
# MENU PRINCIPAL
# -----------------------------
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
    st.header("📋 Gerar Planilha de Periodização Ondulatória")
    st.markdown("---")
    
    clientes_df = carregar_clientes()
    if clientes_df.empty:
        st.warning("⚠️ Nenhum cliente cadastrado. Vá ao menu 'Cadastro de Cliente' primeiro.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            cliente_nome = st.selectbox("👤 Escolha o cliente", clientes_df['nome'])
        
        id_cliente = clientes_df[clientes_df['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        
        if cliente is not None:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🎯 Objetivo", cliente['objetivo'])
            col2.metric("📊 Nível", cliente['nivel'].split('(')[0].strip())
            col3.metric("🏋️ Agachamento", f"{cliente['agachamento_1rm']} kg")
            col4.metric("🏋️ Supino", f"{cliente['supino_1rm']} kg")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                semanas = st.select_slider(
                    "📅 Semanas de treino",
                    options=[4, 8, 12, 16],
                    value=4,
                    help="Período total do programa"
                )
            with col2:
                freq = st.radio(
                    "📆 Dias por semana",
                    options=[3, 4, 5],
                    horizontal=True,
                    help="Frequência semanal de treinos"
                )
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                gerar = st.button("🚀 GERAR PLANILHA", use_container_width=True, type="primary")
            
            if gerar:
                with st.spinner(f"Gerando periodização para {semanas} semanas..."):
                    planilhas = gerar_planilha_ondulatoria(cliente, semanas=semanas, frequencia=freq)
                
                st.success(f"✅ Planilha gerada com sucesso! {len(planilhas)} semanas programadas.")
                
                st.markdown(get_table_download_link(planilhas, cliente_nome), unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("📊 Visualização Prévia")
                
                tabs = st.tabs(list(planilhas.keys()))
                
                for i, (nome_semana, df_semana) in enumerate(planilhas.items()):
                    with tabs[i]:
                        st.markdown(f"### {nome_semana}")
                        
                        for dia in df_semana['Dia'].unique():
                            if dia != '':
                                df_dia = df_semana[df_semana['Dia'] == dia]
                                with st.expander(f"📍 Dia {int(dia)}", expanded=True):
                                    st.dataframe(
                                        df_dia,
                                        use_container_width=True,
                                        hide_index=True
                                    )

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
st.sidebar.markdown("© 2026 Ailson Personal Trainer")
