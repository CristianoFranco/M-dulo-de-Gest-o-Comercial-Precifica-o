import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client, Client

SUPABASE_URL = "https://qyfknmvxtizxoluqhhwu.supabase.co"
SUPABASE_KEY = "sb_publishable_ZA84cQ2dd_qwvjOhfcGMVA_v2tooKh8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

def migrar():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
    client = gspread.authorize(creds)
    sh = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    
    # 1. Migrar Serviços
    ws = sh.sheet1
    dados = ws.get_all_records()
    
    for row in dados:
        cod = str(row.get("Código", "")).strip()
        if not cod:
            continue
            
        tarifa_val = row.get("Tarifa (R$)", 0.0)
        try:
            tarifa_clean = str(tarifa_val).replace("R$", "").replace(" ", "").replace(",", ".")
            tarifa_float = float(tarifa_clean) if tarifa_clean else 0.0
        except ValueError:
            tarifa_float = 0.0

        payload = {
            "codigo": cod,
            "descricao": str(row.get("Descrição", "")).strip(),
            "tarifa": tarifa_float,
            "unidade": str(row.get("Unidade", "")).strip(),
            "categoria": str(row.get("Categoria", "")).strip(),
            "observacoes": str(row.get("Observações", "")).strip(),
            "status": str(row.get("Status", "Ativo")).strip()
        }
        
        supabase.table("servicos").upsert(payload, on_conflict="codigo").execute()
    print("✅ Serviços migrados com sucesso para o Supabase!")

if __name__ == "__main__":
    migrar()
