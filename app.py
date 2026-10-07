import streamlit as st
import pandas as pd
import gspread
import base64
import os
from google.oauth2.service_account import Credentials

# ==============================================================================
# 1. FUNÇÕES AUXILIARES DE IMAGEM & CSS PERSONALIZADO
# ==============================================================================
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def aplicar_estilo_personalizado():
    bg_b64 = get_base64_of_bin_file('background.jpg')
    logo_b64 = get_base64_of_bin_file('logo.png')
    
    bg_css = f"""
        background: linear-gradient(rgba(10, 25, 40, 0.75), rgba(10, 25, 40, 0.75)), 
                    url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
    """ if bg_b64 else "background-color: #0A2540;"

    st.markdown(f"""
    <style>
        /* Fundo da Aplicação */
        .stApp {{
            {bg_css}
        }}

        /* Estilização do Topo e Cabeçalho */
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
        .header-title {{
            color: #0A2540;
            font-size: 24px;
            font-weight: 800;
            margin: 0;
        }}
        .header-subtitle {{
            color: #555;
            font-size: 14px;
            margin: 0;
        }}

        /* Estilização dos Formulários e Cartões */
        div[data-testid="stForm"], div.stExpander, div[data-testid="stDataFrame"] {{
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }}

        /* Estilo dos Rótulos (Labels) de Entrada */
        label, .stMarkdown label, .stMarkdown p {{
            color: #0A2540 !important;
            font-weight: 700 !important;
        }}

        /* Títulos de Seções */
        h1, h2, h3, h4 {{
            color: #FFFFFF !important;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
        }}

        /* Estilo das Abas (Tabs) */
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

        /* Botões Principais */
        .stButton>button, div[data-testid="stForm"] button {{
            background: linear-gradient(135deg, #0052B4 0%, #003B82 100%) !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease !important;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 82, 180, 0.4);
        }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Globex Multimodal - Módulo Comercial",
    page_icon="📦",
    layout="wide"
)

aplicar_estilo_personalizado()

# ==============================================================================
# 3. CONEXÃO COM O GOOGLE SHEETS
# ==============================================================================
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"

@st.cache_resource(ttl=0)
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
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    return client.open_by_url(url).sheet1

def formatar_tarifa(val):
    try:
        f = float(val)
        s = f"{f:.5f}".rstrip('0')
        if s.endswith('.'):
            s += '00'
        elif len(s.split('.')[1]) < 2:
            s += '0'
        return s
    except (ValueError, TypeError):
        return str(val)

def carregar_dados(apenas_
