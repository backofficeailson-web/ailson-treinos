# treino/exercicios.py

ESTRUTURA_BASE = {
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

EXTRAS = {
    4: {
        'nome': 'DIA 4 - VARIAÇÃO INFERIOR (TERRA/AGACHAMENTO)',
        'exercicios': [
            {'nome': 'Terra Déficit', 'tipo': 'PRINCIPAL', 'base': 'terra', 'fator': 0.90},
            {'nome': 'Box Squat', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.85},
            {'nome': 'Agachamento Pausado', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.75},
            {'nome': 'Remada Nórdica', 'tipo': 'ACESSÓRIO', 'base': 'terra', 'fator': 0.40},
            {'nome': 'Afundo', 'tipo': 'ACESSÓRIO', 'base': 'agach', 'fator': 0.45},
            {'nome': 'Dips (Paralela)', 'tipo': 'FINALIZADOR', 'base': 'agach', 'fator': 0.25},
        ]
    },
    5: {
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
}