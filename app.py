import streamlit as st
import pandas as pd
import gspread
import base64
import os
from google.oauth2.service_account import Credentials
from modulo_cadastro import renderizar_aba_cadastro
from modulo_propostas import renderizar_aba_propostas

# ==============================================================================
# 1. ESTILO E CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Globex Multimodal - Módulo Comercial",
    page_icon="📦",
    layout="wide"
)

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ""

def aplicar_estilo_personalizado():
    bg_b64 = get_base64_of_bin_file('background.jpg')
    bg_css = f"""
        background: linear-gradient(rgba(10, 25, 40, 0.75), rgba(10, 25, 40, 0.75)), 
                    url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
    """ if bg_b64 else "background-color: #0A2540;"

    st.markdown(f"""
    <style>
        .stApp {{ {bg_css} }}
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
        button[data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #0A2540 !important;
            border-radius: 8px 8px 0 0 !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
        }}
        button[aria-selected="true"] {{
            background-color: #0052B4 !important;
            color: #FFFFFF !important;
        }}
        .stButton>button {{
            background: linear-gradient(135deg, #0052B4 0%, #003B82 100%) !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)

aplicar_estilo_personalizado()

# ==============================================================================
# 2. CONEXÃO COM GOOGLE SHEETS COM CACHE DE PROTEÇÃO DA API
# ==============================================================================
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"

@st.cache_resource(ttl=3600)
def obter_aba_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}").sheet1

# Cache de leitura por 60 segundos para EVITAR ERRO 429 DE QUOTA
@st.cache_data(ttl=60)
def carregar_dados_cached():
    try:
        worksheet = obter_aba_google_sheets()
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
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
        worksheet = obter_aba_google_sheets()
        worksheet.clear()
        df_salvar = df_completo.copy()
        df_salvar["Código"] = df_salvar["Código"].astype(str).str.strip()
        dados_lista = [df_salvar.columns.values.tolist()] + df_salvar.astype(str).values.tolist()
        worksheet.update(range_name='A1', values=dados_lista)
        carregar_dados_cached.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")
        return False

def normalizar_codigo(codigo_str):
    limpo = str(codigo_str).strip().upper()
    return str(int(limpo)) if limpo.isdigit() else limpo

def formatar_tarifa(val):
    try:
        f = float(val)
        s = f"{f:.5f}".rstrip('0')
        if s.endswith('.'): s += '00'
        elif len(s.split('.')[1]) < 2: s += '0'
        return s
    except (ValueError, TypeError):
        return str(val)

# ==============================================================================
# 3. CABEÇALHO & ABAS
# ==============================================================================
logo_b64 = get_base64_of_bin_file('logo.png')
st.markdown(f"""
    <div class="header-container">
        <div>
            <h1 class="header-title">Módulo Comercial & Precificação</h1>
            <p class="header-subtitle">Gestão Integrada de Serviços e Tabelas Tarifárias</p>
        </div>
        <div>
            {'<img src="data:image/png;base64,' + logo_b64 + '" style="height: 60px;">' if logo_b64 else ''}
        </div>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["📋 Cadastro de Serviços", "🛠️ Propostas e Precificação"])

with tabs[0]:
    renderizar_aba_cadastro(carregar_dados, salvar_dados_completos, normalizar_codigo, formatar_tarifa)

with tabs[1]:
    renderizar_aba_propostas(carregar_dados, salvar_dados_completos)
