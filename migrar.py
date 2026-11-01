import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client, Client

# Suas credenciais do Supabase fornecidas
SUPABASE_URL = "https://qyfknmvxtizxoluqhhwu.supabase.co"
SUPABASE_KEY = "sb_publishable_ZA84cQ2dd_qwvjOhfcGMVA_v2tooKh8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações do Google Sheets baseadas no projeto atual
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

def conectar_google_sheets():
    if os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
    else:
        raise FileNotFoundError("O arquivo 'credentials.json' da conta de serviço não foi encontrado na pasta do projeto!")
    client = gspread.authorize(creds)
    return client.open_by_url(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

def migrar_servicos(sh):
    print("🔄 Migrando tabela de Serviços...")
    try:
        ws = sh.sheet1
        dados = ws.get_all_records()
        if not dados:
            print("⚠️ Nenhum serviço encontrado no Google Sheets.")
            return
        
        df = pd.DataFrame(dados)
        registros = []
        for _, row in df.iterrows():
            tarifa_val = row.get("Tarifa (R$)", 0.0)
            try:
                tarifa_float = float(str(tarifa_val).replace(",", ".")) if str(tarifa_val).strip() else 0.0
            except ValueError:
                tarifa_float = 0.0

            registros.append({
                "codigo": str(row.get("Código", "")).strip(),
                "descricao": str(row.get("Descrição", "")).strip(),
                "tarifa": tarifa_float,
                "unidade": str(row.get("Unidade", "")).strip(),
                "categoria": str(row.get("Categoria", "")).strip(),
                "observacoes": str(row.get("Observações", "")).strip(),
                "status": str(row.get("Status", "Ativo")).strip()
            })

        for reg in registros:
            if reg["codigo"]:
                supabase.table("servicos").upsert(reg, on_conflict="codigo").execute()
        print(f"✅ {len(registros)} serviços migrados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao migrar serviços: {e}")

def migrar_propostas(sh):
    print("🔄 Migrando tabela de Propostas Salvas...")
    try:
        ws = sh.worksheet("Propostas_Salvas")
        valores = ws.get_all_values()
        if not valores or len(valores) < 2:
            print("⚠️ Nenhuma proposta salva encontrada no Google Sheets.")
            return
        
        header = valores[0]
        linhas = valores[1:]
        df = pd.DataFrame(linhas, columns=header)
        
        registros = []
        for _, row in df.iterrows():
            tarifa_val = row.get("Tarifa (R$)", 0.0)
            try:
                tarifa_float = float(str(tarifa_val).replace(",", ".")) if str(tarifa_val).strip() else 0.0
            except ValueError:
                tarifa_float = 0.0

            data_val = row.get("Data", "")
            if not data_val or data_val.strip() == "":
                data_val = None

            registros.append({
                "proposta": str(row.get("Proposta", "")).strip(),
                "data": data_val,
                "cliente": str(row.get("Cliente", "")).strip(),
                "cnpj": str(row.get("CNPJ", "")).strip(),
                "codigo": str(row.get("Código", "")).strip(),
                "descricao": str(row.get("Descrição", "")).strip(),
                "categoria": str(row.get("Categoria", "")).strip(),
                "unidade": str(row.get("Unidade", "")).strip(),
                "tarifa": tarifa_float,
                "observacoes": str(row.get("Observacoes", "") or row.get("Observações", "")).strip()
            })

        if registros:
            chunk_size = 100
            for i in range(0, len(registros), chunk_size):
                chunk = registros[i:i + chunk_size]
                supabase.table("propostas").insert(chunk).execute()
        print(f"✅ {len(registros)} itens de propostas migrados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao migrar propostas: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando migração do Google Sheets para o Supabase...")
    planilha = conectar_google_sheets()
    migrar_servicos(planilha)
    migrar_propostas(planilha)
    print("🎉 Processo de migração concluído!")
