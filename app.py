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
            unidade = str(row.get("Unidade", ""))
            categoria = str(row.get("Categoria", ""))
            observacoes = str(row.get("Observações", ""))
            status = str(row.get("Status", "Ativo"))
            
            linha_dados = [codigo, descricao, tarifa, unidade, categoria, observacoes, status]
            
            if codigo in mapa_linhas:
                row_idx = mapa_linhas[codigo]
                worksheet.update(range_name=f"A{row_idx}:G{row_idx}", values=[linha_dados])
            else:
                worksheet.append_row(linha_dados)
                nova_linha_idx = len(worksheet.get_all_values())
                mapa_linhas[codigo] = nova_linha_idx

        carregar_dados_cached.clear()
        return True
    except Exception as e:
        st.error("Erro ao salvar no Google Sheets por linhas: {}".format(e))
        return False

# ==============================================================================
# FUNÇÕES DE INTEGRAÇÃO COM A TELA 3 (PROPOSTAS SALVAS)
# ==============================================================================
def salvar_propostas_na_planilha(linhas_proposta):
    try:
        ws = obter_aba_propostas()
        num_prop = str(linhas_proposta[0].get("Proposta", "")).strip() if linhas_proposta else ""
        todos_valores = ws.get_all_values()
        if not todos_valores:
            todos_valores = [HEADER_PROPOSTAS_ESPERADO]
        linhas_existentes = todos_valores[1:] if len(todos_valores) > 1 else []
        está_editando = st.session_state.get("proposta_id_em_edicao") is not None
        
        linhas_filtradas = []
        for lin in linhas_existentes:
            if len(lin) > 0:
                proposta_linha = str(lin[0]).strip()
                if está_editando and proposta_linha == num_prop:
                    continue
                linhas_filtradas.append(lin)
        novas_linhas_matriz = []
        for reg in linhas_proposta:
            novas_linhas_matriz.append([
                str(reg.get("Proposta", "")),
                str(reg.get("Data", "")),
                str(reg.get("Cliente", "")),
                str(reg.get("CNPJ", "")),
                str(reg.get("Código", "")),
                str(reg.get("Descrição", "")),
                str(reg.get("Categoria", "")),
                str(reg.get("Unidade", "")),
                str(reg.get("Tarifa (R$)", "")),
                str(reg.get("Observações", ""))
            ])
            
        ws.clear()
        conteudo_final = [HEADER_PROPOSTAS_ESPERADO] + linhas_filtradas + novas_linhas_matriz
        ws.update(range_name='A1', values=conteudo_final)
        return True
    except Exception as e:
        st.error(f"Erro ao gravar proposta no Google Sheets: {e}")
        return False

def carregar_propostas_da_planilha():
    try:
        ws = obter_aba_propostas()
        valores = ws.get_all_values()
        if not valores or len(valores) < 2:
            return pd.DataFrame(columns=HEADER_PROPOSTAS_ESPERADO)
        df = pd.DataFrame(valores[1:], columns=valores[0])
        return df
    except Exception:
        return pd.DataFrame(columns=HEADER_PROPOSTAS_ESPERADO)

def obter_proximo_numero_proposta_global():
    if st.session_state.get("proposta_id_em_edicao"):
        return st.session_state["proposta_id_em_edicao"]
        
    agora = datetime.now()
    mes = agora.strftime("%m")
    ano = agora.strftime("%Y")
    prefixo_busca = f"{mes}/"
    sufixo_busca = f"/{ano}"
    
    try:
        df_hist = carregar_propostas_da_planilha()
        maior_seq = 0
        if not df_hist.empty and "Proposta" in df_hist.columns:
            for prop in df_hist["Proposta"].dropna().unique():
                p_str = str(prop).strip()
                if p_str.startswith(prefixo_busca) and p_str.endswith(sufixo_busca):
                    partes = p_str.split("/")
                    if len(partes) == 3:
                        try:
                            num_seq = int(partes[1])
                            if num_seq > maior_seq:
                                maior_seq = num_seq
                        except ValueError:
                            continue
        proximo_seq = maior_seq + 1
        return f"{mes}/{proximo_seq:05d}/{ano}"
    except Exception:
        return f"{mes}/00001/{ano}"

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

def executar_renderizar_cadastro():
    params = [carregar_dados, salvar_dados_completos, normalizar_codigo, formatar_tarifa]
    for i in range(len(params), 0, -1):
        try:
            renderizar_aba_cadastro(*params[:i])
            return
        except TypeError:
            continue

# ==============================================================================
# 3. CABEÇALHO & NAVEGAÇÃO
# ==============================================================================
logo_b64 = get_base64_of_bin_file('logo.png')
if logo_b64:
    header_html = """
        <div class="header-container">
            <div>
                <h1 class="header-title">Módulo Comercial & Precificação</h1>
                <p class="header-subtitle">Gestão Integrada de Serviços e Tabelas Tarifárias</p>
            </div>
            <div>
                <img src="data:image/png;base64,{}" style="height: 60px;">
            </div>
        </div>
    """.format(logo_b64)
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="header-title">Módulo Comercial & Precificação</h1>
                <p class="header-subtitle">Gestão Integrada de Serviços e Tabelas Tarifárias</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# BARRA DE NAVEGAÇÃO COM CONTROLE EXCLUSIVO DE ESTADO ATIVO
col_nav1, col_nav2, col_nav3, _ = st.columns([2.2, 2.5, 2.5, 2.8])
aba_atual = st.session_state["aba_ativa"]

with col_nav1:
    tipo_btn1 = "primary" if aba_atual == "cadastro" else "secondary"
    if st.button("📋 Cadastro", key="btn_nav_cadastro", type=tipo_btn1, use_container_width=True):
        st.session_state["aba_ativa"] = "cadastro"
        st.rerun()

with col_nav2:
    tipo_btn2 = "primary" if aba_atual == "propostas" else "secondary"
    if st.button("🛠️ Proposta Rascunho", key="btn_nav_propostas", type=tipo_btn2, use_container_width=True):
        st.session_state["aba_ativa"] = "propostas"
        st.rerun()

with col_nav3:
    tipo_btn3 = "primary" if aba_atual == "cliente" else "secondary"
    if st.button("📄 Proposta Cliente", key="btn_nav_cliente", type=tipo_btn3, use_container_width=True):
        st.session_state["aba_ativa"] = "cliente"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    "<script>setTimeout(function() { window.scrollTo({top: 0, behavior: 'auto'}); var mainContent = window.parent.document.querySelector('.main'); if (mainContent) { mainContent.scrollTop = 0; } }, 30);</script>",
    unsafe_allow_html=True
)

if st.session_state["aba_ativa"] == "cadastro":
    executar_renderizar_cadastro()
elif st.session_state["aba_ativa"] == "propostas":
    renderizar_aba_propostas(
        carregar_dados_fn=carregar_dados, 
        salvar_dados_completos_fn=salvar_dados_completos,
        obter_proximo_numero_fn=obter_proximo_numero_proposta_global
    )
else:
    renderizar_aba_proposta_cliente(
        salvar_proposta_sheets_fn=salvar_propostas_na_planilha,
        carregar_propostas_salvas_fn=carregar_propostas_da_planilha
    )
