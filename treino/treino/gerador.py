# treino/gerador.py
import pandas as pd
from .exercicios import ESTRUTURA_BASE, EXTRAS

def _definir_fases(objetivo):
    if objetivo == "Hipertrofia":
        return [
            {'foco': 'Resistência Muscular', 'series_base': 3, 'rep_range': '12-15', 'intensidade': 0.60, 'descanso': '45-60s'},
            {'foco': 'Hipertrofia Tensional', 'series_base': 4, 'rep_range': '8-10', 'intensidade': 0.70, 'descanso': '60-90s'},
            {'foco': 'Hipertrofia Metabólica', 'series_base': 4, 'rep_range': '10-12', 'intensidade': 0.65, 'descanso': '45-60s'},
            {'foco': 'Choque/Densidade', 'series_base': 5, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '90s'}
        ]
    elif objetivo == "Força Máxima":
        return [
            {'foco': 'Preparação/Volume', 'series_base': 4, 'rep_range': '6-8', 'intensidade': 0.75, 'descanso': '2-3min'},
            {'foco': 'Força Pura', 'series_base': 5, 'rep_range': '4-5', 'intensidade': 0.85, 'descanso': '3-4min'},
            {'foco': 'Força Máxima', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.92, 'descanso': '4-5min'},
            {'foco': 'Descarga Técnica', 'series_base': 3, 'rep_range': '3-4', 'intensidade': 0.80, 'descanso': '2-3min'}
        ]
    else:
        return [
            {'foco': 'Força-Velocidade', 'series_base': 5, 'rep_range': '3-5', 'intensidade': 0.50, 'descanso': '2min'},
            {'foco': 'Velocidade-Força', 'series_base': 6, 'rep_range': '2-3', 'intensidade': 0.60, 'descanso': '2-3min'},
            {'foco': 'Pico de Potência', 'series_base': 4, 'rep_range': '3-4', 'intensidade': 0.55, 'descanso': '2min'},
            {'foco': 'Transferência', 'series_base': 5, 'rep_range': '5-6', 'intensidade': 0.45, 'descanso': '90s'}
        ]

def _expandir_dias(frequencia):
    dias = {**ESTRUTURA_BASE}
    if frequencia >= 4:
        dias[4] = EXTRAS[4]
    if frequencia == 5:
        dias[5] = EXTRAS[5]
    return dias

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
    fator_volume = {1:0.7, 2:0.85, 3:1.0, 4:1.15, 5:1.3, 6:1.5}.get(nivel_num, 1.0)

    fases = _definir_fases(objetivo)
    dias_treino = _expandir_dias(frequencia)
    if objetivo == "Força Máxima":
        for dia in dias_treino:
            dias_treino[dia]['exercicios'] = [ex for ex in dias_treino[dia]['exercicios'] if ex['tipo'] in ['PRINCIPAL', 'ACESSÓRIO']][:4]

    planilhas_por_semana = {}
    for semana in range(1, semanas+1):
        idx_fase = (semana-1) % 4
        fase = fases[idx_fase]
        ciclo = (semana-1)//4
        fator_progressao = 1.0 + (ciclo * 0.025)
        registros = []
        for dia in range(1, frequencia+1):
            dia_info = dias_treino[dia]
            registros.append({
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
                    rep_range = fase['rep_range'].split('-')
                    repeticoes = f"{int(rep_range[0])+2}-{int(rep_range[1])+2}" if len(rep_range)==2 else str(int(fase['rep_range'])+2)
                    descanso = '60-90s'
                else:
                    intensidade_final = fase['intensidade'] * 0.6
                    series = 3
                    repeticoes = '12-15'
                    descanso = '45-60s'

                carga_str = f"{max(round(carga_base * fator * intensidade_final * fator_progressao, 1), 1.0):.1f}" if carga_base > 0 else 'PESO CORPORAL'
                registros.append({
                    'DIA': f'  {dia}', 'TIPO': tipo, 'EXERCÍCIO': nome_ex,
                    'SÉRIES': series, 'REPETIÇÕES': repeticoes,
                    '% 1RM': f"{int(intensidade_final*100)}%",
                    'CARGA (kg)': carga_str, 'DESCANSO': descanso, 'OBSERVAÇÃO': ''
                })
            registros.append({
                'DIA': '', 'TIPO': '', 'EXERCÍCIO': '─'*60,
                'SÉRIES': '', 'REPETIÇÕES': '', '% 1RM': '',
                'CARGA (kg)': '', 'DESCANSO': '', 'OBSERVAÇÃO': ''
            })
        planilhas_por_semana[f'Semana {semana:02d}'] = pd.DataFrame(registros)
    return planilhas_por_semana