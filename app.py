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

        /* ESTILIZAÇÃO DOS BOTÕES DE NAVEGAÇÃO */
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
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

def obter_aba_servicos():
    sh = obter_planilha_google_sheets()
    return sh.sheet1

def obter_aba_propostas():
    sh = obter_planilha_google_sheets()
    try:
        return sh.worksheet("Propostas_Salvas")
    except Exception:
        ws = sh.add_worksheet(title="Propostas_Salvas", rows=1000, cols=10)
        ws.append_row(["Proposta", "Data", "Cliente", "Código", "Descrição", "Categoria", "Unidade", "Tarifa (R$)", "Observações"])
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

# ------------------------------------------------------------------------------
# FUNÇÕES DE INTEGRACÃO COM A TELA 3 (PROPOSTAS SALVAS)
# ------------------------------------------------------------------------------
def salvar_propostas_na_planilha(linhas_proposta):
    try:
        ws = obter_aba_propostas()
        novas_linhas = []
        for reg in linhas_proposta:
            novas_linhas.append([
                str(reg.get("Proposta", "")),
                str(reg.get("Data", "")),
                str(reg.get("Cliente", "")),
                str(reg.get("Código", "")),
                str(reg.get("Descrição", "")),
                str(reg.get("Categoria", "")),
                str(reg.get("Unidade", "")),
                str(reg.get("Tarifa (R$)", "")),
                str(reg.get("Observações", ""))
            ])
        ws.append_rows(novas_linhas)
        return True
    except Exception as e:
        st.error(f"Erro ao gravar proposta no Google Sheets: {e}")
        return False

def carregar_propostas_da_planilha():
    try:
        ws = obter_aba_propostas()
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

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
# 3. CABEÇALHO & NAVEGAÇÃO
# ==============================================================================
logo_b64 = get_base64_of_bin_file('logo.png')

if logo_b64:
    st.markdown(f"""
        <div class="header-container">
            <div>
                <h1 class="header-title">Módulo Comercial & Precificação</h1>
                <p class="header-subtitle">Gestão Integrada de Serviços e Tabelas Tarifárias</p>
            </div>
            <div>
                <img src="data:image/png;base64,{logo_b64}" style="height: 60px;">
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="header-title">Módulo Comercial & Precificação</h1>
                <p class="header-subtitle">Gestão Integrada de Serviços e Tabelas Tarifárias</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# BARRA DE NAVEGAÇÃO COM DESTAQUE VISUAL (3 TELAS)
col_nav1, col_nav2, col_nav3, _ = st.columns([2.2, 2.5, 2.5, 2.8])

aba_atual = st.session_state["aba_ativa"]

with col_nav1:
    if st.button(
        "📋 Cadastro",
        key="btn_nav_cadastro",
        type="primary" if aba_atual == "cadastro" else "secondary",
        use_container_width=True
    ):
        st.session_state["aba_ativa"] = "cadastro"
        st.rerun()

with col_nav2:
    if st.button(
        "🛠️ Propostas / Precificação",
        key="btn_nav_propostas",
        type="primary" if aba_atual == "propostas" else "secondary",
        use_container_width=True
    ):
        st.session_state["aba_ativa"] = "propostas"
        st.rerun()

with col_nav3:
    if st.button(
        "📄 Proposta Cliente",
        key="btn_nav_cliente",
        type="primary" if aba_atual == "cliente" else "secondary",
        use_container_width=True
    ):
        st.session_state["aba_ativa"] = "cliente"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# RENDERIZAÇÃO DA TELA SELECIONADA
if st.session_state["aba_ativa"] == "cadastro":
    renderizar_aba_cadastro(carregar_dados, salvar_dados_completos, normalizar_codigo)
elif st.session_state["aba_ativa"] == "propostas":
    renderizar_aba_propostas(carregar_dados, salvar_dados_completos)
else:
    renderizar_aba_proposta_cliente(
        salvar_proposta_sheets_fn=salvar_propostas_na_planilha,
        carregar_propostas_salvas_fn=carregar_propostas_da_planilha
    )
