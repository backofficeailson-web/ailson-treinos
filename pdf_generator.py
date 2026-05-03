from fpdf import FPDF
from datetime import datetime
import os
from utils import calcular_imc, calcular_rcq, classificar_imc, classificar_rcq, classificar_gordura
from database import execute_query

def gerar_pdf_avaliacao(id_cliente):
    cliente_data = execute_query("SELECT * FROM clientes WHERE id = ?", (id_cliente,), fetchone=True)
    if not cliente_data:
        return None
    colunas = ['id','nome','telefone','mensalidade','vencimento','idade','nivel','objetivo','agachamento_1rm','supino_1rm','terra_1rm','pegada_direita','pegada_esquerda','historico','ativo']
    cliente = dict(zip(colunas, cliente_data))
    
    ultima_av = execute_query("SELECT * FROM avaliacao_fisica WHERE cliente_id = ? ORDER BY data DESC LIMIT 1", (id_cliente,), fetchone=True)
    if not ultima_av:
        return None
    
    # Cria PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_title(f"Avaliação Física - {cliente['nome']}")
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"AILSON PERSONAL TRAINNER", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Avaliação Física - {cliente['nome']}", ln=True, align="C")
    pdf.ln(10)
    # Dados básicos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Dados do Aluno", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Nome: {cliente['nome']}", ln=True)
    pdf.cell(0, 6, f"Idade: {cliente['idade']} anos", ln=True)
    pdf.ln(5)
    # Medidas
    av_cols = ['id','cliente_id','data','peso','altura','torax','cintura','abdomen','quadril','braco_direito','braco_esquerdo','coxa_direita','coxa_esquerda','panturrilha_direita','panturrilha_esquerda','triceps','subescapular','peitoral','axilar_media','suprailiaca','abdominal','coxa','biceps','perna','observacoes']
    av = dict(zip(av_cols, ultima_av))
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Medidas", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Data: {av['data']}", ln=True)
    pdf.cell(0, 6, f"Peso: {av['peso']} kg   Altura: {av['altura']} m", ln=True)
    imc = calcular_imc(av['peso'], av['altura'])
    pdf.cell(0, 6, f"IMC: {imc:.1f} - {classificar_imc(imc)}", ln=True)
    rcq = calcular_rcq(av['cintura'], av['quadril'])
    pdf.cell(0, 6, f"RCQ: {rcq:.2f} - {classificar_rcq(rcq)}", ln=True)
    pdf.ln(3)
    pdf.cell(0, 6, "Circunferências (cm):", ln=True)
    pdf.cell(0, 6, f"Tórax: {av['torax']}  Cintura: {av['cintura']}  Abdômen: {av['abdomen']}  Quadril: {av['quadril']}", ln=True)
    pdf.cell(0, 6, f"Braço Dir: {av['braco_direito']}  Braço Esq: {av['braco_esquerdo']}", ln=True)
    pdf.cell(0, 6, f"Coxa Dir: {av['coxa_direita']}  Coxa Esq: {av['coxa_esquerda']}", ln=True)
    pdf.ln(3)
    pdf.cell(0, 6, "Dobras Cutâneas (mm):", ln=True)
    pdf.cell(0, 6, f"Tríceps: {av['triceps']}  Subescapular: {av['subescapular']}  Peitoral: {av['peitoral']}", ln=True)
    pdf.cell(0, 6, f"Axilar Média: {av['axilar_media']}  Supra-ilíaca: {av['suprailiaca']}  Abdominal: {av['abdominal']}", ln=True)
    pdf.cell(0, 6, f"Coxa: {av['coxa']}  Bíceps: {av['biceps']}  Perna: {av['perna']}", ln=True)
    if av['observacoes']:
        pdf.ln(3)
        pdf.cell(0, 6, f"Observações: {av['observacoes']}", ln=True)
    
    # Salvar
    nome_arquivo = f"avaliacao_{cliente['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo
