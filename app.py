import streamlit as st
import pandas as pd
import gspread
import base64
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from modulo_cadastro import renderizar_aba_cadastro
from modulo_propostas import renderizar_aba_propostas
from modulo_proposta_cliente import renderizar_aba_proposta_cliente

# ==============================================================================
# 1. ESTILO E CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Globex Multimodal - Módulo Comercial",
    page_icon="📦",
    layout="wide"
)

UNIDADES_PADRAO = [
    "",
    "Por caixa",
    "por unidade",
    "por pallet",
    "por hora/homem",
    "por etiqueta",
    "por volume",
    "por mês"
]

if "lista_unidades" not in st.session_state:
    st.session_state["lista_unidades"] = UNIDADES_PADRAO.copy()
if "form_id" not in st.session_state:
    st.session_state["form_id"] = 0
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastro"

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def aplicar_estilo_personalizado():
    bg_b64 = get_base64_of_bin_file('background.jpg')
    
    if bg_b64:
        bg_style = ".stApp {{ background: linear-gradient(rgba(10, 25, 40, 0.75), rgba(10, 25, 40, 0.75)), url('data:image/jpg;base64,{}') no-repeat center center fixed; background-size: cover; }}".format(bg_b64)
    else:
        bg_style = ".stApp { background-color: #0A2540; }"
        
    css_template = """
        <style>
            {}
            
            .header-container {{
                background: rgba(255, 255, 255, 0.95);
                padding: 20px 30px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 25px;
            }}
            .header-title {{ color: #0A2540; font-size: 24px; font-weight: 800; margin: 0; }}
            .header-subtitle {{ color: #555; font-size: 14px; margin: 0; }}
            
            div[data-testid="stForm"], div.stExpander, div[data-testid="stDataFrame"] {{
                background: rgba(255, 255, 255, 0.95) !important;
                border-radius: 12px !important;
                padding: 20px !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            }}
            
            label, .stMarkdown label, .stMarkdown p {{ color: #0A2540 !important; font-weight: 700 !important; }}
            h1, h2, h3, h4 {{ color: #FFFFFF !important; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8); }}
            
            div.stButton > button {{
                border-radius: 8px !important;
                font-weight: 700 !important;
                transition: all 0.2s ease-in-out;
            }}
            
            div.stButton > button:hover, div.stButton > button:hover p, div.stButton > button:hover span {{
                color: #FFFFFF !important;
            }}
        </style>
    """.format(bg_style)
    
    st.markdown(css_template, unsafe_allow_html=True)

aplicar_estilo_personalizado()

# ==============================================================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==============================================================================
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"
HEADER_PROPOSTAS_ESPERADO = [
    "Proposta", "Data", "Cliente", "CNPJ", "Código", 
    "Descrição", "Categoria", "Unidade", "Tarifa (R$)", "Observações"
]

@st.cache_resource(ttl=3600)
def obter_planilha_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/{}".format(SPREADSHEET_ID))

def obter_aba_servicos():
    sh = obter_planilha_google_sheets()
    return sh.sheet1

def obter_aba_propostas():
    sh = obter_planilha_google_sheets()
    try:
        ws = sh.worksheet("Propostas_Salvas")
    except Exception:
        ws = sh.add_worksheet(title="Propostas_Salvas", rows=1000, cols=10)
        ws.append_row(HEADER_PROPOSTAS_ESPERADO)
        return ws
        
    valores = ws.get_all_values()
    if not valores or valores[0] != HEADER_PROPOSTAS_ESPERADO:
        if not valores:
            ws.append_row(HEADER_PROPOSTAS_ESPERADO)
        else:
            ws.update(range_name='A1:J1', values=[HEADER_PROPOSTAS_ESPERADO])
            
    return ws

@st.cache_data(ttl=60)
def carregar_dados_cached():
    try:
        worksheet = obter_aba_servicos()
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

def carregar_dados(apenas_ativos=True):
    df = carregar_dados_cached()
    colunas_esperadas = ["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações", "Status"]
    
    if df.empty:
        df_vazio = pd.DataFrame(columns=colunas_esperadas)
        return df_vazio[colunas_esperadas[:-1]] if apenas_ativos else df_vazio
    if "Status" not in df.columns:
        df["Status"] = "Ativo"
    
    df["Status"] = df["Status"].astype(str).str.strip().replace("", "Ativo")
    df["Código"] = df["Código"].astype(str).str.strip()
    if apenas_ativos:
        df_ativos = df[df["Status"].str.upper() != "INATIVO"].copy()
        return df_ativos[["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"]]
    
    return df

def salvar_dados_completos(df_completo):
    try:
        worksheet = obter_aba_servicos()
        header = ["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações", "Status"]
        
        matriz_atual = worksheet.get_all_values()
        if not matriz_atual or len(matriz_atual) == 0:
            worksheet.append_row(header)
            matriz_atual = [header]
            
        mapa_linhas = {}
        for idx, linha in enumerate(matriz_atual[1:], start=2):
            if len(linha) > 0:
                codigo_planilha = str(linha[0]).strip()
                mapa_linhas[codigo_planilha] = idx

        for _, row in df_completo.iterrows():
            codigo = str(row.get("Código", "")).strip()
            descricao = str(row.get("Descrição", ""))
            tarifa = str(row.get("Tarifa (R$)", ""))
            unidade = str
