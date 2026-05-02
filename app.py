# app.py - Hulk Personal Trainer (Versão Completa Integrada)
# Streamlit + SQLite + Plotly + OpenPyXL + Pillow
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, date, timedelta
from PIL import Image
import io
import base64
from io import BytesIO
import os

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="HULK PERSONAL TRAINER",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores Hulk
VERDE_HULK = "#2ECC40"
VERDE_ESCURO = "#0D3B0D"
VERDE_CLARO = "#7CFC00"
ROXO_HULK = "#6A1B9A"
ROXO_ESCURO = "#3D0F5C"
PRETO = "#0A0A0A"
CINZA_ESCURO = "#1E1E1E"
CINZA_MEDIO = "#2D2D2D"
BRANCO = "#FFFFFF"
AMARELO_ALERTA = "#FFD700"
VERMELHO = "#FF4136"

# =========================
# BANCO DE DADOS
# =========================
DB_NAME = "hulk_personal.db"

@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Tabela principal de alunos/clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    mensalidade REAL,
                    vencimento TEXT,
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

    # Tabela de avaliação física
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacao_fisica (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    data TEXT,
                    peso REAL,
                    altura REAL,
                    torax REAL,
                    cintura REAL,
                    abdomen REAL,
                    quadril REAL,
                    braco_direito REAL,
                    braco_esquerdo REAL,
                    coxa_direita REAL,
                    coxa_esquerda REAL,
                    panturrilha_direita REAL,
                    panturrilha_esquerda REAL,
                    triceps REAL,
                    subescapular REAL,
                    peitoral REAL,
                    axilar_media REAL,
                    suprailiaca REAL,
                    abdominal REAL,
                    coxa REAL,
                    biceps REAL,
                    perna REAL,
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )''')

    # Tabela de avaliação postural
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacao_postural (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    data TEXT,
                    vista_anterior TEXT,
                    vista_posterior TEXT,
                    vista_lateral_direita TEXT,
                    vista_lateral_esquerda TEXT,
                    cabeca TEXT,
                    ombros TEXT,
                    coluna TEXT,
                    quadril TEXT,
                    joelhos TEXT,
                    pes TEXT,
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )''')

    # Tabela de fotos
    c.execute('''CREATE TABLE IF NOT EXISTS fotos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    data TEXT,
                    tipo TEXT,
                    foto BLOB,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )''')

    conn.commit()

init_db()
conn = get_connection()

# =========================
# FUNÇÕES DE BANCO (adaptadas)
# =========================
def listar_alunos():
    query = "SELECT id, nome, telefone, mensalidade, vencimento, nivel, objetivo FROM clientes ORDER BY nome"
    return pd.read_sql_query(query, conn)

def adicionar_aluno(nome, telefone, mensalidade, vencimento, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq):
    query = """
        INSERT INTO clientes
        (nome, telefone, mensalidade, vencimento, idade, nivel, objetivo, agachamento_1rm, supino_1rm, terra_1rm, pegada_direita, pegada_esquerda, historico)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(query, (nome, telefone, mensalidade, vencimento, idade, nivel, objetivo, agach, sup, terra, peg_dir, peg_esq, ""))
    conn.commit()

def excluir_aluno(aluno_id):
    conn.execute("DELETE FROM avaliacao_fisica WHERE cliente_id = ?", (aluno_id,))
    conn.execute("DELETE FROM avaliacao_postural WHERE cliente_id = ?", (aluno_id,))
    conn.execute("DELETE FROM fotos WHERE cliente_id = ?", (aluno_id,))
    conn.execute("DELETE FROM clientes WHERE id = ?", (aluno_id,))
    conn.commit()

def carregar_cliente(id_cliente):
    df = pd.read_sql_query(f"SELECT * FROM clientes WHERE id = {id_cliente}", conn)
    return df.iloc[0] if not df.empty else None

def salvar_avaliacao_fisica(dados):
    query = '''INSERT INTO avaliacao_fisica 
        (cliente_id, data, peso, altura, torax, cintura, abdomen, quadril,
         braco_direito, braco_esquerdo, coxa_direita, coxa_esquerda,
         panturrilha_direita, panturrilha_esquerda, triceps, subescapular,
         peitoral, axilar_media, suprailiaca, abdominal, coxa, biceps, perna, observacoes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    conn.execute(query, dados)
    conn.commit()

def carregar_avaliacoes_fisicas(cliente_id):
    return pd.read_sql_query(f"SELECT * FROM avaliacao_fisica WHERE cliente_id = {cliente_id} ORDER BY data DESC", conn)

def salvar_avaliacao_postural(dados):
    query = '''INSERT INTO avaliacao_postural 
        (cliente_id, data, vista_anterior, vista_posterior, vista_lateral_direita,
         vista_lateral_esquerda, cabeca, ombros, coluna, quadril, joelhos, pes, observacoes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    conn.execute(query, dados)
    conn.commit()

def carregar_avaliacoes_posturais(cliente_id):
    return pd.read_sql_query(f"SELECT * FROM avaliacao_postural WHERE cliente_id = {cliente_id} ORDER BY data DESC", conn)

def salvar_foto_db(cliente_id, data, tipo, foto_bytes):
    conn.execute("INSERT INTO fotos (cliente_id, data, tipo, foto) VALUES (?,?,?,?)",
                 (cliente_id, data, tipo, foto_bytes))
    conn.commit()

def carregar_fotos(cliente_id):
    return pd.read_sql_query(f"SELECT * FROM fotos WHERE cliente_id = {cliente_id} ORDER BY data DESC", conn)

# =========================
# FUNÇÕES DE CÁLCULO (mantidas)
# =========================
def calcular_percentual_gordura(dados, sexo='M'):
    idade = dados.get('idade', 30)
    resultado = {}
    soma_7 = sum([dados.get(d, 0) for d in ['triceps', 'subescapular', 'peitoral', 
                                              'axilar_media', 'suprailiaca', 'abdominal', 'coxa']])
    soma_3_peitoral = sum([dados.get(d, 0) for d in ['peitoral', 'abdominal', 'coxa']])
    if sexo == 'M':
        dc_7 = 1.112 - (0.00043499 * soma_7) + (0.00000055 * soma_7**2) - (0.00028826 * idade)
        resultado['Pollock 7 Dobras'] = round((4.95 / dc_7 - 4.50) * 100, 2)
        dc_3 = 1.10938 - (0.0008267 * soma_3_peitoral) + (0.0000016 * soma_3_peitoral**2) - (0.0002574 * idade)
        resultado['Pollock 3 Dobras'] = round((4.95 / dc_3 - 4.50) * 100, 2)
        soma_guedes = sum([dados.get(d, 0) for d in ['triceps', 'suprailiaca', 'abdominal']])
        resultado['Guedes (3 Dobras)'] = round((0.187 * soma_guedes + 10.73), 2)
        soma_faulkner = sum([dados.get(d, 0) for d in ['triceps', 'subescapular', 'suprailiaca', 'abdominal']])
        resultado['Faulkner'] = round((0.153 * soma_faulkner + 5.783), 2)
    else:
        dc_7 = 1.097 - (0.00046971 * soma_7) + (0.00000056 * soma_7**2) - (0.00012828 * idade)
        resultado['Pollock 7 Dobras'] = round((5.01 / dc_7 - 4.57) * 100, 2)
        dc_3 = 1.089733 - (0.0009245 * soma_3_peitoral) + (0.0000025 * soma_3_peitoral**2) - (0.0000979 * idade)
        resultado['Pollock 3 Dobras'] = round((5.01 / dc_3 - 4.57) * 100, 2)
        soma_guedes = sum([dados.get(d, 0) for d in ['triceps', 'suprailiaca', 'abdominal']])
        resultado['Guedes (3 Dobras)'] = round((0.187 * soma_guedes + 10.73), 2)
    return resultado

def classificar_gordura(percentual, sexo='M', idade=30):
    if sexo == 'M':
        if idade < 30:
            faixas = [(6, "Excelente"), (10, "Bom"), (14, "Acima da Média"), (19, "Média"), (25, "Abaixo da Média"), (100, "Ruim")]
        elif idade < 40:
            faixas = [(8, "Excelente"), (12, "Bom"), (17, "Acima da Média"), (22, "Média"), (28, "Abaixo da Média"), (100, "Ruim")]
        elif idade < 50:
            faixas = [(10, "Excelente"), (15, "Bom"), (20, "Acima da Média"), (25, "Média"), (30, "Abaixo da Média"), (100, "Ruim")]
        else:
            faixas = [(12, "Excelente"), (17, "Bom"), (22, "Acima da Média"), (27, "Média"), (32, "Abaixo da Média"), (100, "Ruim")]
    else:
        if idade < 30:
            faixas = [(12, "Excelente"), (16, "Bom"), (20, "Acima da Média"), (25, "Média"), (31, "Abaixo da Média"), (100, "Ruim")]
        elif idade < 40:
            faixas = [(14, "Excelente"), (18, "Bom"), (23, "Acima da Média"), (28, "Média"), (33, "Abaixo da Média"), (100, "Ruim")]
        else:
            faixas = [(16, "Excelente"), (20, "Bom"), (25, "Acima da Média"), (30, "Média"), (35, "Abaixo da Média"), (100, "Ruim")]
    for limite, classificacao in faixas:
        if percentual <= limite:
            return classificacao
    return "Não classificado"

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2) if altura > 0 else 0

def classificar_imc(imc):
    if imc < 18.5: return "Abaixo do Peso"
    elif imc < 24.9: return "Peso Normal"
    elif imc < 29.9: return "Sobrepeso"
    elif imc < 34.9: return "Obesidade Grau I"
    elif imc < 39.9: return "Obesidade Grau II"
    else: return "Obesidade Grau III"

def calcular_rcq(cintura, quadril):
    return round(cintura / quadril, 2) if quadril > 0 else 0

def classificar_rcq(rcq, sexo='M'):
    if sexo == 'M':
        if rcq < 0.85: return "Risco Baixo"
        elif rcq < 0.90: return "Risco Moderado"
        elif rcq < 0.95: return "Risco Alto"
        else: return "Risco Muito Alto"
    else:
        if rcq < 0.75: return "Risco Baixo"
        elif rcq < 0.80: return "Risco Moderado"
        elif rcq < 0.85: return "Risco Alto"
        else: return "Risco Muito Alto"

# =========================
# GERAÇÃO DE TREINO (mantida)
# =========================
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
            registros_semana.append({
                'DIA': f'▶ DIA {dia}', 'TIPO': '', 'EXERCÍCIO': dia_info['nome'],
                'SÉRIES': '', 'REPETIÇÕES': '', '% 1RM': f'FASE: {fase["foco"].upper()}',
                'CARGA (kg)': '', 'DESCANSO': '', 'OBSERVAÇÃO': ''
            })
            for ex in dia_info['exercicios']:
                nome_ex = ex['nome']
                tipo = ex['tipo']
                base = ex['base']
                fator = ex['fator']
                if base == 'agach': carga_base = agach
                elif base == 'sup': carga_base = sup
                elif base == 'terra': carga_base = terra
                elif base == 'pegada': carga_base = 0
                else: carga_base = agach * 0.5
                if tipo == 'PRINCIPAL':
                    intensidade_final = fase['intensidade']
                    series = max(2, int(fase['series_base'] * fator_volume))
                    repeticoes = fase['rep_range']
                    descanso = fase['descanso']
                elif tipo == 'ACESSÓRIO':
                    intensidade_final = fase['intensidade'] * 0.85
                    series = max(2, int((fase['series_base'] - 1) * fator_volume))
                    rep_range_split = fase['rep_range'].split('-')
                    repeticoes = f"{int(rep_range_split[0]) + 2}-{int(rep_range_split[1]) + 2}" if len(rep_range_split) == 2 else str(int(fase['rep_range']) + 2)
                    descanso = '60-90s'
                else:
                    intensidade_final = fase['intensidade'] * 0.6
                    series = 3
                    repeticoes = '12-15'
                    descanso = '45-60s'
                carga_str = f"{max(round(carga_base * fator * intensidade_final * fator_progressao, 1), 1.0):.1f}" if carga_base > 0 else 'PESO CORPORAL'
                registros_semana.append({
                    'DIA': f'  {dia}', 'TIPO': tipo, 'EXERCÍCIO': nome_ex,
                    'SÉRIES': series, 'REPETIÇÕES': repeticoes,
                    '% 1RM': f"{int(intensidade_final * 100)}%",
                    'CARGA (kg)': carga_str, 'DESCANSO': descanso, 'OBSERVAÇÃO': ''
                })
            registros_semana.append({
                'DIA': '', 'TIPO': '', 'EXERCÍCIO': '─' * 60,
                'SÉRIES': '', 'REPETIÇÕES': '', '% 1RM': '',
                'CARGA (kg)': '', 'DESCANSO': '', 'OBSERVAÇÃO': ''
            })
        planilhas_por_semana[f'Semana {semana:02d}'] = pd.DataFrame(registros_semana)
    return planilhas_por_semana

def get_table_download_link(planilhas_dict, nome_cliente="cliente"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in planilhas_dict.items():
            aba_nome = nome_aba.replace(' ', '_')[:31]
            df.to_excel(writer, sheet_name=aba_nome, index=False)
            worksheet = writer.sheets[aba_nome]
            col_widths = {'A': 10, 'B': 18, 'C': 40, 'D': 10, 'E': 14, 'F': 12, 'G': 14, 'H': 14, 'I': 20}
            for col_letter, width in col_widths.items():
                worksheet.column_dimensions[col_letter].width = width
            from openpyxl.styles import PatternFill, Font
            purple_fill = PatternFill(start_color='6A1B9A', end_color='6A1B9A', fill_type='solid')
            dark_fill = PatternFill(start_color='1A1A1A', end_color='1A1A1A', fill_type='solid')
            for row in range(2, len(df) + 2):
                cell_value = worksheet.cell(row=row, column=1).value
                if cell_value and str(cell_value).startswith('▶'):
                    for col in range(1, 10):
                        cell = worksheet.cell(row=row, column=col)
                        cell.fill = purple_fill
                        cell.font = Font(color='7CFC00', bold=True, size=11)
                elif cell_value and str(cell_value).startswith('  '):
                    for col in range(1, 10):
                        cell = worksheet.cell(row=row, column=col)
                        cell.fill = dark_fill
                        cell.font = Font(color='FFFFFF')
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
           ">
            🟢 BAIXAR PLANILHA COMPLETA 🟢
        </a>
    </div>
    '''
    return href

# =========================
# FUNÇÕES DE ALERTA DE VENCIMENTO
# =========================
def extrair_dia_vencimento(vencimento_str):
    """Tenta extrair o dia do vencimento a partir de strings como 'dia 10', '10', 'todo dia 15'"""
    import re
    if not vencimento_str:
        return None
    numbers = re.findall(r'\d+', str(vencimento_str))
    if numbers:
        dia = int(numbers[0])
        if 1 <= dia <= 31:
            return dia
    return None

def calcular_status_vencimento(vencimento_str):
    dia = extrair_dia_vencimento(vencimento_str)
    if dia is None:
        return "data_invalida", None, "?"
    hoje = date.today()
    # Próximo vencimento no mês atual ou próximo mês
    try:
        prox_vencimento = date(hoje.year, hoje.month, dia)
    except ValueError:
        # dia inválido para o mês (ex: 31 em fevereiro)
        return "data_invalida", None, "?"
    if prox_vencimento < hoje:
        # já passou, considerar próximo mês
        mes = hoje.month + 1
        ano = hoje.year
        if mes > 12:
            mes = 1
            ano += 1
        try:
            prox_vencimento = date(ano, mes, dia)
        except ValueError:
            return "data_invalida", None, "?"
    dias_restantes = (prox_vencimento - hoje).days
    if dias_restantes < 0:
        status = "vencido"
    elif dias_restantes <= 5:
        status = "proximo"
    else:
        status = "em_dia"
    return status, prox_vencimento, dias_restantes

# =========================
# LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(135deg, #0A0A0A 0%, #0D3B0D 100%);
        }}
        h1, p, label {{
            color: #7CFC00 !important;
        }}
        .stButton > button {{
            background: linear-gradient(135deg, #2ECC40 0%, #0D3B0D 100%);
            color: white !important;
            border: 2px solid #7CFC00;
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://i.imgur.com/6QbxZqT.png" if os.path.exists("logo.png") else "https://i.imgur.com/6QbxZqT.png", width=200)
        st.title("HULK PERSONAL")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario == "admin" and senha == "123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

if not st.session_state.logado:
    tela_login()
    st.stop()

# =========================
# SIDEBAR E MENU
# =========================
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 10px 0;">
    <h2 style="color: {VERDE_CLARO};">🟢 HULK</h2>
    <p style="color: {VERDE_HULK};">PERSONAL TRAINER</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("📋 MENU", [
    "Dashboard Financeiro",
    "Cadastro de Aluno",
    "Avaliação Física",
    "Avaliação Postural",
    "Fotos Avaliativas",
    "Geração de Treino",
    "Histórico & Evolução",
    "Gerenciar Alunos"
])

# =========================
# DASHBOARD FINANCEIRO COM ALERTAS
# =========================
if menu == "Dashboard Financeiro":
    st.title("📊 Dashboard Financeiro")
    df = listar_alunos()
    
    total_alunos = len(df)
    faturamento = df["mensalidade"].sum() if not df.empty else 0
    media_mensal = df["mensalidade"].mean() if not df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos", total_alunos)
    col2.metric("Faturamento Mensal", f"R$ {faturamento:,.2f}")
    col3.metric("Mensalidade Média", f"R$ {media_mensal:,.2f}")
    
    if not df.empty:
        # Processar status de vencimento
        status_list = []
        datas_vencimento = []
        dias_restantes_list = []
        for _, row in df.iterrows():
            status, prox_data, dias = calcular_status_vencimento(row['vencimento'])
            status_list.append(status)
            datas_vencimento.append(prox_data.strftime('%d/%m/%Y') if prox_data else 'Indefinido')
            dias_restantes_list.append(dias if dias is not None else '?')
        df_status = df.copy()
        df_status['status'] = status_list
        df_status['proximo_vencimento'] = datas_vencimento
        df_status['dias_restantes'] = dias_restantes_list
        
        # Resumo de status
        vencidos = len(df_status[df_status['status'] == 'vencido'])
        proximos = len(df_status[df_status['status'] == 'proximo'])
        em_dia = len(df_status[df_status['status'] == 'em_dia'])
        invalidos = len(df_status[df_status['status'] == 'data_invalida'])
        
        st.subheader("🚨 Alertas de Vencimento")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 Vencidos", vencidos)
        col2.metric("🟡 Vencem em até 5 dias", proximos)
        col3.metric("🟢 Em dia", em_dia)
        col4.metric("❌ Data inválida", invalidos)
        
        # Tabela detalhada com formatação condicional
        st.subheader("📋 Situação dos Alunos")
        # Vamos criar um DataFrame para exibição com HTML customizado para cores
        def color_status(row):
            if row['status'] == 'vencido':
                return f'background-color: {VERMELHO}; color: white'
            elif row['status'] == 'proximo':
                return f'background-color: {AMARELO_ALERTA}; color: black'
            elif row['status'] == 'em_dia':
                return f'background-color: {VERDE_HULK}; color: white'
            else:
                return ''
        
        styled_df = df_status[['nome', 'mensalidade', 'vencimento', 'proximo_vencimento', 'dias_restantes', 'status']].copy()
        styled_df = styled_df.rename(columns={'proximo_vencimento': 'Próx. Venc.', 'dias_restantes': 'Dias Rest.'})
        # Aplicar estilo (não é possível usar applymap diretamente para exportar, mas podemos usar st.dataframe com highlight)
        st.dataframe(
            styled_df,
            use_container_width=True,
            column_config={
                "status": st.column_config.TextColumn(
                    "Status",
                    help="🔴 vencido | 🟡 próximo | 🟢 em dia"
                )
            }
        )
        
        # Gráfico de status
        st.subheader("📊 Distribuição de Status")
        status_counts = pd.DataFrame({
            'Status': ['Vencido', 'Próximo (5 dias)', 'Em dia', 'Data inválida'],
            'Quantidade': [vencidos, proximos, em_dia, invalidos]
        })
        fig_status = px.bar(status_counts, x='Status', y='Quantidade', 
                            color='Status', 
                            color_discrete_map={
                                'Vencido': VERMELHO,
                                'Próximo (5 dias)': AMARELO_ALERTA,
                                'Em dia': VERDE_HULK,
                                'Data inválida': CINZA_MEDIO
                            },
                            title="Status de Vencimento")
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Gráfico de faturamento por aluno
        st.subheader("💵 Mensalidades")
        fig = px.bar(df, x="nome", y="mensalidade", title="Mensalidade por Aluno",
                     labels={"nome": "Aluno", "mensalidade": "Mensalidade (R$)"},
                     color="mensalidade", color_continuous_scale="greens")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum aluno cadastrado.")

# =========================
# CADASTRO DE ALUNO (unificado)
# =========================
elif menu == "Cadastro de Aluno":
    st.title("➕ Cadastro de Aluno")
    with st.form("cadastro_unificado"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome completo")
        telefone = col2.text_input("Telefone")
        col1, col2 = st.columns(2)
        mensalidade = col1.number_input("Mensalidade (R$)", min_value=0.0, step=10.0, value=100.0)
        vencimento = col2.text_input("Data de Vencimento (ex: dia 10 ou 10)")
        idade = st.number_input("Idade", 12, 100, 30)
        nivel = st.selectbox("Nível de experiência", [
            "Iniciante (Nível 1)", "Básico (Nível 2)", "Intermediário (Nível 3)",
            "Avançado (Nível 4)", "Elite (Nível 5)", "Competitivo (Nível 6)"
        ])
        objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Força Máxima", "Potência"])
        st.subheader("Testes de Força (1RM ou Estimado)")
        col1, col2, col3 = st.columns(3)
        agach = col1.number_input("Agachamento (kg)", 0.0, 500.0, 80.0)
        sup = col2.number_input("Supino (kg)", 0.0, 500.0, 60.0)
        terra = col3.number_input("Terra (kg)", 0.0, 500.0, 100.0)
        peg_dir = st.number_input("Força de Pegada Mão Direita (kg)", 0.0, 200.0, 40.0)
        peg_esq = st.number_input("Força de Pegada Mão Esquerda (kg)", 0.0, 200.0, 38.0)
        submitted = st.form_submit_button("💾 SALVAR ALUNO")
        if submitted:
            if nome.strip() == "":
                st.warning("Informe o nome do aluno.")
            else:
                adicionar_aluno(nome, telefone, mensalidade, vencimento, idade, nivel, objetivo,
                                agach, sup, terra, peg_dir, peg_esq)
                st.success(f"Aluno {nome} cadastrado com sucesso!")

# =========================
# DEMAIS MÓDULOS (Avaliação Física, Postural, Fotos, Geração de Treino, Histórico)
# =========================
# (A mesma implementação anterior, omitida por brevidade, mas mantenha as funções existentes no seu código. Aqui apenas replico as chamadas principais.)

elif menu == "Avaliação Física":
    st.header("📏 AVALIAÇÃO FÍSICA COMPLETA")
    st.markdown("---")
    df_clientes = listar_alunos()
    if df_clientes.empty:
        st.warning("⚠️ Nenhum aluno cadastrado.")
    else:
        cliente_nome = st.selectbox("👤 Selecione o aluno", df_clientes['nome'])
        id_cliente = df_clientes[df_clientes['nome'] == cliente_nome]['id'].values[0]
        cliente = carregar_cliente(id_cliente)
        tab_avaliacao = st.radio("📋 Ação", ["Nova Avaliação", "Histórico"], horizontal=True)
        if tab_avaliacao == "Nova Avaliação":
            with st.form("form_avaliacao"):
                data_av = st.date_input("📅 Data da avaliação", datetime.now())
                st.markdown("### 📊 Dados Básicos")
                col1, col2 = st.columns(2)
                peso = col1.number_input("Peso (kg)", 30.0, 300.0, 80.0, 0.1)
                altura = col2.number_input("Altura (m)", 1.20, 2.50, 1.75, 0.01)
                st.markdown("### 📏 Circunferências (cm)")
                col1, col2, col3 = st.columns(3)
                torax = col1.number_input("Tórax", 30.0, 200.0, 95.0, 0.1)
                cintura = col2.number_input("Cintura", 30.0, 200.0, 80.0, 0.1)
                abdomen = col3.number_input("Abdômen", 30.0, 200.0, 85.0, 0.1)
                col1, col2, col3 = st.columns(3)
                quadril = col1.number_input("Quadril", 30.0, 200.0, 95.0, 0.1)
                braco_dir = col2.number_input("Braço Direito", 10.0, 80.0, 35.0, 0.1)
                braco_esq = col3.number_input("Braço Esquerdo", 10.0, 80.0, 35.0, 0.1)
                col1, col2, col3 = st.columns(3)
                coxa_dir = col1.number_input("Coxa Direita", 20.0, 120.0, 55.0, 0.1)
                coxa_esq = col2.number_input("Coxa Esquerda", 20.0, 120.0, 55.0, 0.1)
                pant_dir = col3.number_input("Panturrilha Direita", 10.0, 60.0, 37.0, 0.1)
                pant_esq = st.number_input("Panturrilha Esquerda", 10.0, 60.0, 37.0, 0.1)
                st.markdown("### 🏥 Dobras Cutâneas (mm)")
                col1, col2, col3 = st.columns(3)
                triceps = col1.number_input("Tríceps", 1.0, 80.0, 15.0, 0.1)
                subescapular = col2.number_input("Subescapular", 1.0, 80.0, 15.0, 0.1)
                peitoral = col3.number_input("Peitoral", 1.0, 80.0, 12.0, 0.1)
                col1, col2, col3 = st.columns(3)
                axilar_media = col1.number_input("Axilar Média", 1.0, 80.0, 12.0, 0.1)
                suprailiaca = col2.number_input("Supra-ilíaca", 1.0, 80.0, 15.0, 0.1)
                abdominal = col3.number_input("Abdominal", 1.0, 80.0, 20.0, 0.1)
                coxa = st.number_input("Coxa", 1.0, 80.0, 18.0, 0.1)
                col1, col2 = st.columns(2)
                biceps = col1.number_input("Bíceps", 1.0, 80.0, 10.0, 0.1)
                perna = col2.number_input("Perna", 1.0, 80.0, 15.0, 0.1)
                observacoes = st.text_area("Observações")
                if st.form_submit_button("💾 SALVAR"):
                    dados_av = (id_cliente, str(data_av), peso, altura, torax, cintura, abdomen, quadril,
                                braco_dir, braco_esq, coxa_dir, coxa_esq, pant_dir, pant_esq,
                                triceps, subescapular, peitoral, axilar_media, suprailiaca, abdominal, coxa,
                                biceps, perna, observacoes)
                    salvar_avaliacao_fisica(dados_av)
                    st.success("✅ Avaliação salva!")
                    dados_calc = {'idade': cliente['idade'], 'sexo': 'M', 'peso': peso, 'altura': altura,
                                  'cintura': cintura, 'quadril': quadril,
                                  'triceps': triceps, 'subescapular': subescapular,
                                  'peitoral': peitoral, 'axilar_media': axilar_media,
                                  'suprailiaca': suprailiaca, 'abdominal': abdominal, 'coxa': coxa}
                    imc = calcular_imc(peso, altura)
                    rcq = calcular_rcq(cintura, quadril)
                    resultados = calcular_percentual_gordura(dados_calc)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("IMC", f"{imc:.1f}", classificar_imc(imc))
                    col2.metric("RCQ", f"{rcq:.2f}", classificar_rcq(rcq))
                    primeiro = list(resultados.keys())[0]
                    col3.metric(primeiro, f"{resultados[primeiro]:.1f}%", classificar_gordura(resultados[primeiro], 'M', cliente['idade']))
                    st.dataframe(pd.DataFrame([{'Protocolo': k, '% Gordura': v, 'Classificação': classificar_gordura(v, 'M', cliente['idade'])} for k,v in resultados.items()]), use_container_width=True, hide_index=True)
        else:
            df_av = carregar_avaliacoes_fisicas(id_cliente)
            if df_av.empty:
                st.info("Nenhuma avaliação encontrada.")
            else:
                for _, av in df_av.iterrows():
                    with st.expander(f"📅 {av['data']} - Peso: {av['peso']}kg"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"Tórax: {av['torax']}cm | Cintura: {av['cintura']}cm")
                            st.write(f"Braço Dir: {av['braco_direito']}cm | Esq: {av['braco_esquerdo']}cm")
                            st.write(f"Quadril: {av['quadril']}cm")
                        with col2:
                            st.write(f"Tríceps: {av['triceps']}mm | Subescapular: {av['subescapular']}mm")
                            st.write(f"Peitoral: {av['peitoral']}mm | Abdominal: {av['abdominal']}mm | Coxa: {av['coxa']}mm")

elif menu == "Avaliação Postural":
    st.header("🏥 AVALIAÇÃO POSTURAL")
    st.markdown("---")
    df_clientes = listar_alunos()
    if df_clientes.empty:
        st.warning("⚠️ Nenhum aluno cadastrado.")
    else:
        cliente_nome = st.selectbox("👤 Selecione o aluno", df_clientes['nome'])
        id_cliente = df_clientes[df_clientes['nome'] == cliente_nome]['id'].values[0]
        tab_postural = st.radio("📋 Ação", ["Nova Avaliação", "Histórico"], horizontal=True)
        if tab_postural == "Nova Avaliação":
            with st.form("form_postural"):
                data_postural = st.date_input("📅 Data", datetime.now())
                st.markdown("### 👁️ Vistas")
                col1, col2 = st.columns(2)
                vista_anterior = col1.selectbox("Vista Anterior", ["Normal", "Cabeça inclinada D", "Cabeça inclinada E", "Ombro D elevado", "Ombro E elevado", "Escoliose aparente"])
                vista_posterior = col2.selectbox("Vista Posterior", ["Normal", "Escápula alada D", "Escápula alada E", "Escoliose torácica", "Escoliose lombar", "Diferença altura quadril"])
                col1, col2 = st.columns(2)
                vista_lat_dir = col1.selectbox("Vista Lateral Direita", ["Normal", "Cabeça anteriorizada", "Hipercifose torácica", "Hiperlordose lombar", "Joelhos recurvatum"])
                vista_lat_esq = col2.selectbox("Vista Lateral Esquerda", ["Normal", "Cabeça anteriorizada", "Hipercifose torácica", "Hiperlordose lombar", "Joelhos recurvatum"])
                st.markdown("### 🔍 Análise Segmentar")
                col1, col2 = st.columns(2)
                cabeca = col1.selectbox("Cabeça/Pescoço", ["Alinhada", "Anteriorizada", "Inclinada D", "Inclinada E", "Rotação D", "Rotação E"])
                ombros = col2.selectbox("Ombros", ["Alinhados", "Protusos", "Elevado D", "Elevado E", "Desnível"])
                col1, col2 = st.columns(2)
                coluna = col1.selectbox("Coluna Vertebral", ["Alinhada", "Hipercifose", "Hiperlordose", "Escoliose torácica D", "Escoliose torácica E", "Retificação"])
                quadril = col2.selectbox("Quadril", ["Alinhado", "Anteversão", "Retroversão", "Elevado D", "Elevado E"])
                col1, col2 = st.columns(2)
                joelhos = col1.selectbox("Joelhos", ["Alinhados", "Valgo D", "Valgo E", "Varo D", "Varo E", "Recurvatum"])
                pes = col2.selectbox("Pés", ["Normais", "Plano D", "Plano E", "Cavo D", "Cavo E", "Pronado", "Supinado"])
                observacoes_postural = st.text_area("Observações")
                if st.form_submit_button("💾 SALVAR"):
                    dados_postural = (id_cliente, str(data_postural), vista_anterior, vista_posterior,
                                      vista_lat_dir, vista_lat_esq, cabeca, ombros, coluna, quadril,
                                      joelhos, pes, observacoes_postural)
                    salvar_avaliacao_postural(dados_postural)
                    st.success("✅ Avaliação postural salva!")
                    st.markdown("---")
                    st.subheader("📋 Resumo")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Anterior: {vista_anterior}")
                        st.write(f"Posterior: {vista_posterior}")
                        st.write(f"Lateral Dir: {vista_lat_dir}")
                        st.write(f"Lateral Esq: {vista_lat_esq}")
                    with col2:
                        st.write(f"Cabeça: {cabeca}")
                        st.write(f"Ombros: {ombros}")
                        st.write(f"Coluna: {coluna}")
                        st.write(f"Quadril: {quadril}")
                        st.write(f"Joelhos: {joelhos}")
                        st.write(f"Pés: {pes}")
        else:
            df_postural = carregar_avaliacoes_posturais(id_cliente)
            if df_postural.empty:
                st.info("Nenhuma avaliação postural encontrada.")
            else:
                for _, av in df_postural.iterrows():
                    with st.expander(f"📅 {av['data']}"):
                        st.write(f"Anterior: {av['vista_anterior']} | Posterior: {av['vista_posterior']}")
                        st.write(f"Lateral Dir: {av['vista_lateral_direita']} | Esq: {av['vista_lateral_esquerda']}")
                        st.write(f"Cabeça: {av['cabeca']} | Ombros: {av['ombros']} | Coluna: {av['coluna']}")
                        st.write(f"Quadril: {av['quadril']} | Joelhos: {av['joelhos']} | Pés: {av['pes']}")

elif menu == "Fotos Avaliativas":
    st.header("📸 FOTOS AVALIATIVAS")
    st.markdown("---")
    df_clientes = listar_alunos()
    if df_clientes.empty:
        st.warning("⚠️ Nenhum aluno cadastrado.")
    else:
        cliente_nome = st.selectbox("👤 Selecione o aluno", df_clientes['nome'])
        id_cliente = df_clientes[df_clientes['nome'] == cliente_nome]['id'].values[0]
        tab_fotos = st.radio("📋 Ação", ["Nova Foto", "Galeria"], horizontal=True)
        if tab_fotos == "Nova Foto":
            data_foto = st.date_input("📅 Data da foto", datetime.now())
            col1, col2, col3 = st.columns(3)
            with col1:
                frente = st.file_uploader("Frente", type=['jpg','jpeg','png'], key="frente")
                if frente: st.image(frente, width=200)
            with col2:
                costas = st.file_uploader("Costas", type=['jpg','jpeg','png'], key="costas")
                if costas: st.image(costas, width=200)
            with col3:
                perfil = st.file_uploader("Perfil", type=['jpg','jpeg','png'], key="perfil")
                if perfil: st.image(perfil, width=200)
            if st.button("💾 SALVAR FOTOS"):
                for img, tipo in [(frente, "Frente"), (costas, "Costas"), (perfil, "Perfil")]:
                    if img:
                        salvar_foto_db(id_cliente, str(data_foto), tipo, img.read())
                st.success("✅ Fotos salvas!")
        else:
            df_fotos = carregar_fotos(id_cliente)
            if df_fotos.empty:
                st.info("Nenhuma foto encontrada.")
            else:
                datas = df_fotos['data'].unique()
                for data in datas:
                    with st.expander(f"📅 {data}"):
                        fotos_data = df_fotos[df_fotos['data'] == data]
                        cols = st.columns(3)
                        for i, (_, foto) in enumerate(fotos_data.iterrows()):
                            with cols[i % 3]:
                                st.image(foto['foto'], caption=foto['tipo'], width=250)

elif menu == "Geração de Treino":
    st.header("📋 GERAR PLANILHA DE PERIODIZAÇÃO ONDULATÓRIA")
    st.markdown("---")
    df_clientes = listar_alunos()
    if df_clientes.empty:
        st.warning("⚠️ Nenhum aluno cadastrado.")
    else:
        cliente_nome = st.selectbox("👤 Escolha o aluno", df_clientes['nome'])
        id_cliente = df_clientes[df_clientes['nome'] == cliente_nome]['id'].values[0]
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
                semanas = st.select_slider("📅 Semanas", options=[4,8,12,16], value=4)
            with col2:
                freq = st.radio("📆 Dias/semana", [3,4,5], horizontal=True)
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                gerar = st.button("🚀 GERAR PLANILHA", type="primary")
            if gerar:
                planilhas = gerar_planilha_ondulatoria(cliente, semanas=semanas, frequencia=freq)
                st.success(f"✅ Planilha gerada com {len(planilhas)} semanas!")
                st.markdown(get_table_download_link(planilhas, cliente_nome), unsafe_allow_html=True)
                st.markdown("---")
                st.subheader("📊 VISUALIZAÇÃO PRÉVIA")
                tabs = st.tabs(list(planilhas.keys()))
                for i, (nome_semana, df_semana) in enumerate(planilhas.items()):
                    with tabs[i]:
                        st.markdown(f"### 🟢 {nome_semana.upper()}")
                        df_display = df_semana[df_semana['EXERCÍCIO'].str.contains('─') == False]
                        dias_unicos = df_display[df_display['DIA'].str.startswith('▶', na=False)]['DIA'].tolist()
                        for dia_header in dias_unicos:
                            dia_nome = df_display[df_display['DIA'] == dia_header]['EXERCÍCIO'].values[0]
                            with st.expander(f"📍 {dia_header} - {dia_nome}", expanded=True):
                                idx_inicio = df_display[df_display['DIA'] == dia_header].index[0]
                                idx_dias_seguintes = df_display[df_display['DIA'].str.startswith('▶', na=False)].index
                                idx_fim = idx_dias_seguintes[idx_dias_seguintes > idx_inicio].min() if any(idx_dias_seguintes > idx_inicio) else len(df_display)
                                df_dia = df_display.iloc[idx_inicio+1:idx_fim]
                                df_dia = df_dia[df_dia['EXERCÍCIO'] != '']
                                if not df_dia.empty:
                                    st.dataframe(df_dia[['TIPO', 'EXERCÍCIO', 'SÉRIES', 'REPETIÇÕES', '% 1RM', 'CARGA (kg)', 'DESCANSO']],
                                                 use_container_width=True, hide_index=True)

elif menu == "Histórico & Evolução":
    st.header("📈 HISTÓRICO DO CLIENTE")
    df_clientes = listar_alunos()
    if df_clientes.empty:
        st.warning("⚠️ Nenhum aluno cadastrado.")
    else:
        nome = st.selectbox("👤 Selecione o aluno", df_clientes['nome'])
        cliente = carregar_cliente(int(df_clientes[df_clientes['nome']==nome]['id'].values[0]))
        st.markdown("### 🏋️ Força Máxima (1RM)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Agachamento", f"{cliente['agachamento_1rm']} kg")
        col2.metric("Supino", f"{cliente['supino_1rm']} kg")
        col3.metric("Terra", f"{cliente['terra_1rm']} kg")
        st.info("📊 Gráficos de evolução serão disponibilizados em breve.")

elif menu == "Gerenciar Alunos":
    st.title("📋 Gerenciar Alunos")
    df = listar_alunos()
    if df.empty:
        st.info("Nenhum aluno cadastrado.")
    else:
        st.dataframe(df[['id', 'nome', 'telefone', 'mensalidade', 'vencimento', 'nivel', 'objetivo']],
                     use_container_width=True, hide_index=True)
        st.subheader("Excluir Aluno")
        aluno_id = st.number_input("ID do aluno a ser excluído", min_value=1, step=1)
        if st.button("🗑️ EXCLUIR ALUNO"):
            excluir_aluno(aluno_id)
            st.success("Aluno removido (avaliações, fotos e treinos também excluídos).")
            st.rerun()

# =========================
# RODAPÉ
# =========================
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
    <p style="color: {VERDE_CLARO}; font-size: 1.5rem;">🟢</p>
    <p style="color: {VERDE_HULK}; font-weight: bold;">HULK PERSONAL TRAINER</p>
    <p style="color: {BRANCO}; font-size: 0.8rem;">© 2026 - Todos os direitos reservados</p>
    <p style="color: {AMARELO_ALERTA}; font-style: italic;">"QUANTO MAIS RAIVA, MAIS FORTE FICA!"</p>
</div>
""", unsafe_allow_html=True)