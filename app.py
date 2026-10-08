import streamlit as st
import pandas as pd
import gspread
import base64
import os
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

        /* ESTILIZAÇÃO DIFERENCIADA PARA OS BOTÕES DE NAVEGAÇÃO */
        div[data-testid="stColumn"] button[kind="primary"] {{
            background: #0052B4 !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            border: 2px solid #60A5FA !important;
            box-shadow: 0 4px 14px rgba(0, 82, 180, 0.6) !important;
        }}

        div[data-testid="stColumn"] button[kind="secondary"] {{
            background: rgba(255, 255, 255, 0.1) !important;
            color: #E2E8F0 !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
        }}
        
        div[data-testid="stColumn"] button[kind="secondary"]:hover {{
            background: rgba(255, 255, 255, 0.2) !important;
            color: #FFFFFF !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

aplicar_estilo_personalizado()

# ==============================================================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==============================================================================
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"

@st.cache_resource(ttl=3600)
def obter_planilha_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds = Credentials.from
