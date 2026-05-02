# utils.py
import shutil
from datetime import date
import re

def backup_db():
    shutil.copy("ailson_personal.db", f"backup/backup_{date.today()}.db")

def extrair_dia_vencimento(vencimento_str):
    if not vencimento_str:
        return None
    numbers = re.findall(r'\d+', str(vencimento_str))
    if numbers:
        dia = int(numbers[0])
        if 1 <= dia <= 31:
            return dia
    return None