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

        /* ============================================================================== */
        /* ABAS FORMATADAS COMO BOTÕES / BLOCOS DISCRETOS                                */
        /* ============================================================================== */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: 12px !important;
            border-bottom: none !important;
        }}

        /* Estilo Base para os Botões/Blocos das Abas */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease-in-out !important;
        }}

        /* Texto da Aba Inativa: Branco limpo, discreto e perfeitamente legível */
        div[data-testid="stTabs"] button[data-baseweb="tab"] *, 
        div[data-testid="stTabs"] button[data-baseweb="tab"] p, 
        div[data-testid="stTabs"] button[data-baseweb="tab"] span {{
            color: #E2E8F0 !important;
            -webkit-text-fill-color: #E2E8F0 !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            opacity: 1 !important;
        }}

        /* Hover no Botão Inativo */
        div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
            background-color: rgba(255, 255, 255, 0.22) !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
        }}

        /* Aba Ativa (Selecionada): Destaque Azul com Borda e Fundo Sólido */
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            background-color: #0052B4 !important;
            border-color: #3B82F6 !important;
            box-shadow: 0 4px 12px rgba(0, 82, 180, 0.4) !important;
        }}

        div[data-testid="stTabs"] button[aria-selected="true"] *, 
        div[data-testid="stTabs"] button[aria-selected="true"] p, 
        div[data-testid="stTabs"] button[aria-selected="true"] span {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 800 !important;
        }}

        /* Botões Globais */
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
# 2. CONEXÃO COM GOOGLE SHEETS
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

@st.cache_data(ttl=60)
def carregar_dados_cached():
    try:
        worksheet = obter_aba_google_sheets()
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
        return df_ativos[["Código", "Descrição", "Tarifa (R$)",
