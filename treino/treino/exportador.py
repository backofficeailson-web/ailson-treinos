# treino/exportador.py
import base64
from io import BytesIO
import pandas as pd
from datetime import datetime

def get_table_download_link(planilhas_dict, nome_cliente="cliente"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in planilhas_dict.items():
            df.to_excel(writer, sheet_name=nome_aba.replace(' ', '_')[:31], index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    nome_arquivo = f"TREINO_AILSON_{nome_cliente}_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
    return f'''
    <div style="text-align:center; padding:20px;">
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
           download="{nome_arquivo}"
           style="background:linear-gradient(135deg,#6A1B9A 0%,#2ECC40 100%);color:white;padding:15px 30px;
                  text-decoration:none;border-radius:10px;font-size:18px;font-weight:bold;display:inline-block;
                  margin:10px;border:2px solid #7CFC00;">
            🟢 BAIXAR PLANILHA COMPLETA 🟢
        </a>
    </div>
    '''