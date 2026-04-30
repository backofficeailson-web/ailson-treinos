import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
from io import BytesIO

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(
    page_title="HULK PERSONAL TRAINER",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores Hulk
VERDE_HULK = "#2ECC40"
VERDE_ESCURO = "#1B5E20"
VERDE_CLARO = "#7CFC00"
ROXO_HULK = "#6A1B9A"
ROXO_ESCURO = "#4A148C"
PRETO = "#0A0A0A"
CINZA_ESCURO = "#1A1A1A"
BRANCO = "#F0F0F0"
AMARELO_ALERTA = "#FFD700"

# CSS Tema Hulk
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {PRETO} 0%, {VERDE_ESCURO} 100%);
        background-attachment: fixed;
    }}
    
    .stSidebar {{
        background: linear-gradient(180deg, {PRETO} 0%, {ROXO_ESCURO} 100%);
        border-right: 3px solid {VERDE_HULK};
    }}
    
    h1, h2, h3 {{
        color: {VERDE_CLARO} !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    
    h1 {{
        font-size: 3rem !important;
        border-bottom: 3px solid {VERDE_HULK};
        padding-bottom: 10px;
    }}
    
    h2 {{
        border-left: 5px solid {VERDE_HULK};
        padding-left: 15px;
    }}
    
    p, label, .stMarkdown {{
        color: {BRANCO} !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {VERDE_HULK} 0%, {VERDE_ESCURO} 100%);
        color: white !important;
        border-radius: 10px !important;
        border: 2px solid {VERDE_CLARO} !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46, 204, 64, 0.3);
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {VERDE_CLARO} 0%, {VERDE_HULK} 100%);
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(46, 204, 64, 0.5) !important;
        border-color: {BRANCO} !important;
    }}
    
    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, {ROXO_HULK} 0%, {VERDE_HULK} 100%) !important;
        border: 2px solid {VERDE_CLARO} !important;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(46, 204, 64, 0.7); }}
        70% {{ box-shadow: 0 0 0 15px rgba(46, 204, 64, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(46, 204, 64, 0); }}
    }}
    
    .stMetric {{
        background: linear-gradient(135deg, {CINZA_ESCURO} 0%, {VERDE_ESCURO} 100%);
        padding: 15px !important;
        border-radius: 10px !important;
        border: 2px solid {VERDE_HULK} !important;
        box-shadow: 0 4px 15px rgba(46, 204, 64, 0.2);
    }}
    
    .stMetric label {{
        color: {VERDE_CLARO} !important;
        font-weight: bold !important;
    }}
    
    .stMetric [data-testid="stMetricValue"] {{
        color: {BRANCO} !important;
        font-size: 2rem !important;
    }}
    
    .stDataFrame {{
        background: {CINZA_ESCURO} !important;
        border: 1px solid {VERDE_HULK} !important;
        border-radius: 10px !important;
        overflow: hidden;
    }}
    
    .stTextInput input, .stNumberInput input, .stSelectbox div {{
        background-color: {CINZA_ESCURO} !important;
        color: {BRANCO} !important;
        border: 2px solid {VERDE_ESCURO} !important;
        border-radius: 8px !important;
    }}
    
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {VERDE_HULK} !important;
        box-shadow: 0 0 10px rgba(46, 204, 64, 0.3) !important;
    }}
    
    .stSelectbox [data-baseweb="select"] {{
        background-color: {CINZA_ESCURO} !important;
    }}
    
    .stSlider [data-baseweb="slider"] {{
        background: {VERDE_HULK} !important;
    }}
    
    .stRadio [role="radiogroup"] label {{
        color: {BRANCO} !important;
    }}
    
    .stRadio [data-baseweb="radio"] {{
        background-color: {VERDE_HULK} !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {CINZA_ESCURO} !important;
        border-radius: 10px 10px 0 0 !important;
        border: 1px solid {VERDE_HULK} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {BRANCO} !important;
        font-weight: bold !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {VERDE_HULK} !important;
        color: {PRETO} !important;
        border-radius: 8px 8px 0 0 !important;
    }}
    
    .streamlit-expanderHeader {{
        background: linear-gradient(135deg, {ROXO_ESCURO} 0%, {VERDE_ESCURO} 100%) !important;
        color: {VERDE_CLARO} !important;
        border: 1px solid {VERDE_HULK} !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }}
    
    .stSuccess {{
        background-color: {VERDE_ESCURO} !important;
        color: {VERDE_CLARO} !important;
        border-left: 5px solid {VERDE_HULK} !important;
    }}
    
    .stWarning {{
        background-color: {ROXO_ESCURO} !important;
        color: {AMARELO_ALERTA} !important;
        border-left: 5px solid {AMARELO_ALERTA} !important;
    }}
    
    .stInfo {{
        background-color: {CINZA_ESCURO} !important;
        color: {VERDE_CLARO} !important;
        border-left: 5px solid {VERDE_HULK} !important;
    }}
    
    .stForm {{
        background: linear-gradient(135deg, {CINZA_ESCURO} 0%, {PRETO} 100%);
        padding: 20px !important;
        border-radius: 15px !important;
        border: 2px solid {VERDE_HULK} !important;
        box-shadow: 0 8px 32px rgba(46, 204, 64, 0.15);
    }}
    
    .stFileUploader {{
        background: {CINZA_ESCURO} !important;
        border: 2px dashed {VERDE_HULK} !important;
        border-radius: 10px !important;
    }}
    
    hr {{
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, {VERDE_HULK}, transparent) !important;
        margin: 20px 0 !important;
    }}
    
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {PRETO};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {VERDE_HULK};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {VERDE_CLARO};
    }}
    
    .stSidebar .stSelectbox label, 
    .stSidebar .stTextInput label {{
        color: {VERDE_CLARO} !important;
    }}
    
    .stMetric:hover {{
        border-color: {VERDE_CLARO} !important;
        box-shadow: 0 0 25px rgba(124, 252, 0, 0.5) !important;
        transform: scale(1.02) !important;
        transition: all 0.3s ease !important;
    }}
</style>
""", unsafe_allow_html=True)

# Logo e sidebar
LOGO_PATH = "logo.png"

if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=180)
else:
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: {VERDE_CLARO}; font-size: 2rem; margin: 0;">🟢 HULK</h1>
        <h2 style="color: {VERDE_HULK}; font-size: 1.2rem; margin: 0;">PERSONAL TRAINER</h2>
        <p style="color: {ROXO_HULK}; font-style: italic; margin-top: 10px;">"HULK ESMAGA!" 💪</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="
    background: linear-gradient(135deg, {VERDE_ESCURO} 0%, {ROXO_ESCURO} 100%);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid {VERDE_HULK};
    margin: 20px 0;
">
    <p style="color: {VERDE_CLARO}; text-align: center; margin: 0;">
        🟢 NÍVEL DE FORÇA 🟢
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# BANCO DE DADOS
# -----------------------------
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

# -----------------------------
# FUNÇÕES DE GERAÇÃO DE TREINO
# -----------------------------
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
            {'foco': 'Resistência Muscular', 'series_base': 3, 'rep_range': '12-15', 'intensidade': 0.60, 'descanso': '45-60s'},
            {'foco': 'Hipertrofia Tensional', 'series_base': 4, 'rep_range': '8-10', 'intensidade': 0.70, 'descanso': '60-90s'},
            {'foco': 'Hipertrofia Metabólica', 'series_base': 4, 'rep_range': '10-12', 'intensidade': 0.65, 'descanso': '45-60s'},
            {'foco': 'Choque/Densidade', 'series_base': 5, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '90s'}
        ]
    elif objetivo == "Força Máxima":
        fases = [
            {'foco': 'Preparação/Volume', 'series_base': 4, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '2-3min'},
            {'foco': 'Força Pura', 'series_base': 5, 'rep_range': '4-5', 'intensidade': 0.85, 'descanso': '3-4min'},
            {'foco': 'Força Máxima', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.92, 'descanso': '4-5min'},
            {'foco': 'Descarga Técnica', 'series_base': 3, 'rep_range': '3-4', 'intensidade': 0.80, 'descanso': '2-3min'}
        ]
    else:
        fases = [
            {'foco': 'Força-Velocidade', 'series_base': 5, 'rep_range': '3-5', 'intensidade': 0.50, 'descanso': '2min'},
            {'foco': 'Velocidade-Força', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.60, 'descanso': '2-3min'},
            {'foco': 'Pico de Potência', 'series_base': 4, 'rep_range': '3-4', 'intensidade': 0.55, 'descanso': '2min'},
            {'foco': 'Transferência', 'series_base': 5, 'rep_range': '5-6', 'intensidade': 0.45, 'descanso': '90s'}
        ]

    dias_treino = {
        1: {
            'nome': 'DIA 1 - MEMBROS INFERIORES (FOCO AGACHAMENTO)',
            'exercicios': [
                {'nome': 'Agachamento Livre (barra alta)', 'tipo': 'PRINCIPAL', 'base': 'agach', 'fator': 1.0},
                {'nome': 'Agachamento Frontal', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.80},
                {'nome': 'Avanço com Barra', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.50},
                {'nome': 'Stiff', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.60},
                {'nome': 'Good Morning', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.45},
                {'nome': 'Esmagamento (Gripper)', 'tipo': 'FINALIZADOR', 'base': 'pegada', 'fator': 0.0},
            ]
        },
        2: {
            'nome': 'DIA 2 - MEMBROS SUPERIORES (FOCO SUPINO)',
            'exercicios': [
                {'nome': 'Supino Reto', 'tipo': 'PRINCIPAL', 'base': 'sup', 'fator': 1.0},
                {'nome': 'Supino Fechado', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.80},
                {'nome': 'Desenvolvimento Militar', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.55},
                {'nome': 'Tríceps Testa', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.30},
                {'nome': 'Tríceps Corda (Cross)', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.20},
                {'nome': 'Pinça (Anilhas)', 'tipo': 'FINALIZADOR', 'base': 'pegada', 'fator': 0.0},
            ]
        },
        3: {
            'nome': 'DIA 3 - DORSAIS/POSTERIOR (FOCO TERRA)',
            'exercicios': [
                {'nome': 'Levantamento Terra Tradicional', 'tipo': 'PRINCIPAL', 'base': 'terra', 'fator': 1.0},
                {'nome': 'Terra Sumô', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.85},
                {'nome': 'Remada Curvada', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.50},
                {'nome': 'Barra Fixa com Peso', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.30},
                {'nome': 'Rosca Direta', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.15},
                {'nome': 'Sustentação (Barra)', 'tipo': 'FINALIZADOR', 'base': 'pegada', 'fator': 0.0},
            ]
        }
    }

    if frequencia >= 4:
        dias_treino[4] = {
            'nome': 'DIA 4 - VARIAÇÃO INFERIOR (TERRA/AGACHAMENTO)',
            'exercicios': [
                {'nome': 'Terra Déficit', 'tipo': 'PRINCIPAL', 'base': 'terra', 'fator': 0.90},
                {'nome': 'Box Squat', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.85},
                {'nome': 'Agachamento Pausado', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.75},
                {'nome': 'Remada Nórdica', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.40},
                {'nome': 'Afundo', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.45},
                {'nome': 'Dips (Paralela)', 'tipo': 'FINALIZADOR', 'base': 'agach', 'fator': 0.25},
            ]
        }
    if frequencia == 5:
        dias_treino[5] = {
            'nome': 'DIA 5 - ISOLAMENTO/ESPECIALIZAÇÃO',
            'exercicios': [
                {'nome': 'Board Press', 'tipo': 'PRINCIPAL', 'base': 'sup', 'fator': 0.85},
                {'nome': 'Supino Pausado', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.75},
                {'nome': 'Puxada Alta', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.30},
                {'nome': 'Remada Baixa', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.25},
                {'nome': 'Crucifixo Unilateral', 'tipo': 'ACESSÓRIO', 'base': 'sup', 'fator': 0.15},
                {'nome': 'Remada Alta', 'tipo': 'FINALIZADOR', 'base': 'agach', 'fator': 0.20},
            ]
        }
    
    if objetivo == "Força Máxima":
        for dia in dias_treino:
            dias_treino[dia]['exercicios'] = [ex for ex in dias_treino[dia]['exercicios'] if ex['tipo'] in ['PRINCIPAL', 'ACESSÓRIO']][:4]

    planilhas_por_semana = {}

    for semana in range(1, semanas + 1):
        idx_fase = (semana - 1) % 4
        fase = fases[idx_fase]
        
        ciclo = (semana - 1) // 4
        fator_progressao = 1.0 + (ciclo * 0.025)
        
        registros_semana = []
        
        for dia in range(1, frequencia + 1):
            dia_info = dias_treino.get(dia, dias_treino[1])
            
            # Cabeçalho do dia
            registros_semana.append({
                'ORDEM': '',
                'DIA': f'▶ DIA {dia}',
                'TIPO': '',
                'EXERCÍCIO': dia_info['nome'],
                'SÉRIES': '',
                'REPETIÇÕES': '',
                '% 1RM': f'FASE: {fase["foco"].upper()}',
                'CARGA (kg)': '',
                'DESCANSO': '',
                'OBSERVAÇÃO': ''
            })
            
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
                
                if tipo == 'PRINCIPAL':
                    intensidade_final = fase['intensidade']
                    series = max(2, int(fase['series_base'] * fator_volume))
                    repeticoes = fase['rep_range']
                    descanso = fase['descanso']
                elif tipo == 'ACESSÓRIO':
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
                    carga_str = f"{carga:.1f}"
                else:
                    carga_str = 'PESO CORPORAL'
                
                registros_semana.append({
                    'ORDEM': '',
                    'DIA': f'  {dia}',
                    'TIPO': tipo,
                    'EXERCÍCIO': nome_ex,
                    'SÉRIES': series,
                    'REPETIÇÕES': repeticoes,
                    '% 1RM': f"{int(intensidade_final * 100)}%",
                    'CARGA (kg)': carga_str,
                    'DESCANSO': descanso,
                    'OBSERVAÇÃO': ''
                })
            
            # Separador entre dias
            registros_semana.append({
                'ORDEM': '',
                'DIA': '',
                'TIPO': '',
                'EXERCÍCIO': '─' * 60,
                'SÉRIES': '',
                'REPETIÇÕES': '',
                '% 1RM': '',
                'CARGA (kg)': '',
                'DESCANSO': '',
                'OBSERVAÇÃO': ''
            })
        
        df_semana = pd.DataFrame(registros_semana)
        planilhas_por_semana[f'Semana {semana:02d}'] = df_semana

    return planilhas_por_semana


def get_table_download_link(planilhas_dict, nome_cliente="cliente"):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in planilhas_dict.items():
            aba_nome = nome_aba.replace(' ', '_')[:31]
            df.to_excel(writer, sheet_name=aba_nome, index=False)
            
            worksheet = writer.sheets[aba_nome]
            
            # Formatação das colunas
            col_widths = {
                'A': 8,   # ORDEM
                'B': 10,  # DIA
                'C': 18,  # TIPO
                'D': 40,  # EXERCÍCIO
                'E': 10,  # SÉRIES
                'F': 14,  # REPETIÇÕES
                'G': 12,  # % 1RM
                'H': 14,  # CARGA (kg)
                'I': 14,  # DESCANSO
                'J': 20   # OBSERVAÇÃO
            }
            
            for col_letter, width in col_widths.items():
                worksheet.column_dimensions[col_letter].width = width
            
            # Destacar cabeçalhos dos dias
            from openpyxl.styles import PatternFill, Font, Alignment
            green_fill = PatternFill(start_color='2ECC40', end_color='2ECC40', fill_type='solid')
            purple_fill = PatternFill(start_color='6A1B9A', end_color='6A1B9A', fill_type='solid')
            dark_fill = PatternFill(start_color='1A1A1A', end_color='1A1A1A', fill_type='solid')
            
            for row in range(2, len(df) + 2):
                cell_value = worksheet.cell(row=row, column=2).value
                if cell_value and str(cell_value).startswith('▶'):
                    for col in range(1, 11):
                        cell = worksheet.cell(row=row, column=col)
                        cell.fill = purple_fill
                        cell.font = Font(color='7CFC00', bold=True, size=11)
                elif cell_value and str(cell_value).startswith('  '):
                    for col in range(1, 11):
                        cell = worksheet.cell(row=row, column=col)
                        cell.fill = dark_fill
                        cell.font = Font(color='F0F0F0')
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    data_formatada = datetime.now().strftime("%d-%m-%Y")
    nome_arquivo = f"TREINO_HULK_{nome_cliente}_{data_formatada}.xlsx"
    
    href = f'''
    <div style="text-align: center; padding: 20px;">
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
           download="{nome_arquivo}"
           style="
               background: linear-gradient(135deg, #6A1B9A 0%, #2ECC40 100%);
               color: white;
               padding: 15px 30px;
               text-decoration: none;
               border-radius: 10px;
               font-size: 18px;
               font-weight: bold;
               display: inline-block;
               margin: 10px;
               border: 2px solid #7CFC00;
               box-shadow: 0 4px 15px rgba(46, 204, 64, 0.5);
           ">
            🟢 BAIXAR PLANILHA COMPLETA 🟢
        </a>
        <br><small style="color: #7CFC00;">Arquivo Excel com {len(planilhas_dict)} abas - Uma para cada semana</small>
    </div>
    '''
    return href


# -----------------------------
# MENU PRINCIPAL
# -----------------------------
menu = st.sidebar.selectbox("📋 MENU", ["Cadastro de Cliente", "Avaliação & Fotos", "Geração de Treino", "Histórico & Evolução"])

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
    st.header("📋 GERAR PLANILHA DE PERIODIZAÇÃO ONDULATÓRIA")
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
                st.subheader("📊 VISUALIZAÇÃO PRÉVIA POR SEMANA")
                
                tabs = st.tabs(list(planilhas.keys()))
                
                for i, (nome_semana, df_semana) in enumerate(planilhas.items()):
                    with tabs[i]:
                        st.markdown(f"### 🟢 {nome_semana.upper()}")
                        
                        # Filtra apenas linhas com exercícios (remove separadores)
                        df_display = df_semana[df_semana['EXERCÍCIO'].str.contains('─') == False]
                        
                        # Agrupa por dia
                        dias_unicos = df_display[df_display['DIA'].str.startswith('▶', na=False)]['DIA'].tolist()
                        
                        for dia_header in dias_unicos:
                            dia_num = dia_header.split('DIA ')[1]
                            dia_nome = df_display[df_display['DIA'] == dia_header]['EXERCÍCIO'].values[0]
                            
                            with st.expander(f"📍 {dia_header} - {dia_nome}", expanded=True):
                                # Pega exercícios deste dia
                                idx_inicio = df_display[df_display['DIA'] == dia_header].index[0]
                                idx_dias_seguintes = df_display[df_display['DIA'].str.startswith('▶', na=False)].index
                                idx_fim = idx_dias_seguintes[idx_dias_seguintes > idx_inicio].min() if any(idx_dias_seguintes > idx_inicio) else len(df_display)
                                
                                df_dia = df_display.iloc[idx_inicio+1:idx_fim]
                                df_dia = df_dia[df_dia['EXERCÍCIO'] != '']
                                
                                if not df_dia.empty:
                                    st.dataframe(
                                        df_dia[['TIPO', 'EXERCÍCIO', 'SÉRIES', 'REPETIÇÕES', '% 1RM', 'CARGA (kg)', 'DESCANSO']],
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

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="
    background: linear-gradient(135deg, {VERDE_ESCURO} 0%, {PRETO} 100%);
    padding: 20px;
    border-radius: 10px;
    border: 2px solid {VERDE_HULK};
    text-align: center;
    margin-top: 20px;
">
    <p style="color: {VERDE_CLARO}; font-size: 1.5rem; margin: 0;">🟢</p>
    <p style="color: {VERDE_HULK}; font-weight: bold; margin: 10px 0;">HULK PERSONAL TRAINER</p>
    <p style="color: {BRANCO}; font-size: 0.8rem; margin: 5px 0;">© 2026 - Todos os direitos reservados</p>
    <p style="color: {AMARELO_ALERTA}; font-style: italic; font-size: 0.9rem; margin-top: 10px;">"QUANTO MAIS RAIVA, MAIS FORTE FICA!"</p>
</div>
""", unsafe_allow_html=True)
