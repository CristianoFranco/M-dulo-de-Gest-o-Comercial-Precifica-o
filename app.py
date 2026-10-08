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
        
        div[data-testid="stForm"], div.stExp
