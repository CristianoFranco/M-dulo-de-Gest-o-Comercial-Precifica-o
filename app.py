import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO
# ==============================================================================
st.set_page_config(
    page_title="Globex Multimodal - Módulo Comercial",
    page_icon="📦",
    layout="wide"
)

# CSS Customizado nas cores da Globex Multimodal
st.markdown("""
<style>
    .main { background-color: #EBF1F5; }
    h1 { color: #0A2540; font-weight: 800; }
    .stButton>button {
        background: linear-gradient(135deg, #0052B4 0%, #003B82 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONEXÃO COM O GOOGLE SHEETS
# ==============================================================================
# ID da sua planilha no Google Drive
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"

@st.cache_resource
def conectar_google_sheets():
    # Tenta conectar usando os Secrets do Streamlit ou credenciais locais
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    else:
        # Se estiver testando localmente sem secrets configurados
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

try:
    worksheet = conectar_google_sheets()
except Exception as e:
    worksheet = None

def carregar_dados():
    if worksheet is None:
        return pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])

def salvar_dados(df):
    if worksheet is not None:
        worksheet.clear()
        dados = [df.columns.values.tolist()] + df.astype(str).values.tolist()
        worksheet.update(dados)

# ==============================================================================
# 3. INTERFACE DO APLICATIVO
# ==============================================================================
st.title("GLOBEX MULTIMODAL")
st.caption("Módulo de Gestão Comercial & Precificação")

tabs = st.tabs(["📋 Cadastro de Serviços", "🛠️ Propostas e Precificação"])

with tabs[0]:
    st.subheader("Cadastro e Gestão de Serviços")
    
    df_servicos = carregar_dados()

    with st.form("form_servico", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código do Serviço", placeholder="Ex: SERV-001")
            categoria = st.selectbox("Categoria", ["Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"])
            tarifa = st.number_input("Tarifa (R$)", min_value=0.0, format="%.2f")
        
        with col2:
            descricao = st.text_input("Descrição do Serviço", placeholder="Ex: Armazenagem de carga paletizada")
            unidade = st.selectbox("Unidade", ["Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês"])
            observacoes = st.text_area("Observações e Premissas", placeholder="Ex: Faturamento mínimo mensal de 50 paletes.")
        
        btn_salvar = st.form_submit_button("💾 Cadastrar / Salvar Serviço")

    if btn_salvar:
        if codigo and descricao:
            nova_linha = pd.DataFrame([{
                "Código": codigo,
                "Descrição": descricao,
                "Tarifa (R$)": f"{tarifa:.2f}",
                "Unidade": unidade,
                "Categoria": categoria,
                "Observações": observacoes
            }])
            
            df_atualizado = pd.concat([df_servicos, nova_linha], ignore_index=True)
            salvar_dados(df_atualizado)
            st.success(f"Serviço '{codigo}' salvo com sucesso no Google Drive!")
            st.rerun()
        else:
            st.warning("O Código e a Descrição são obrigatórios!")

    st.markdown("---")
    st.subheader("🔍 Base de Serviços Cadastrados")
    
    # Exibição e edição direta dos dados
    df_editavel = st.data_editor(df_servicos, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 Sincronizar Alterações da Tabela"):
        salvar_dados(df_editavel)
        st.success("Tabela sincronizada com sucesso no Google Sheets!")

with tabs[1]:
    st.info("Módulo reservado para simulações e formação de propostas comerciais.")
