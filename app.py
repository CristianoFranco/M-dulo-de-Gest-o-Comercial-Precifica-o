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
SPREADSHEET_ID = "1wbhgMnqQuyOxwCef4pJh3vDnafBBU2AZk-uSt1NnPWc"

@st.cache_resource
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

def carregar_dados():
    try:
        worksheet = obter_aba_google_sheets()
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])
        return df
    except Exception as e:
        import traceback
        st.error(f"Erro ao carregar dados do Google Sheets: {type(e).__name__} - {str(e)}")
        st.caption(f"Detalhes técnicos: {traceback.format_exc()}")
        return pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])

def salvar_dados(df):
    try:
        worksheet = obter_aba_google_sheets()
        worksheet.clear()
        dados_lista = [df.columns.values.tolist()] + df.astype(str).values.tolist()
        worksheet.update(range_name='A1', values=dados_lista)
        st.cache_resource.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")
        return False

# ==============================================================================
# 3. GERENCIAMENTO DE ESTADO E MODAIS (POP-UPS)
# ==============================================================================
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

def limpar_formulario():
    st.session_state["form_codigo"] = ""
    st.session_state["form_descricao"] = ""
    st.session_state["form_categoria"] = ""
    st.session_state["form_unidade"] = ""
    st.session_state["form_tarifa"] = 0.0
    st.session_state["form_observacoes"] = ""

if "form_codigo" not in st.session_state:
    limpar_formulario()

# --- Pop-up 1: Adicionar Unidade ---
@st.dialog("➕ Adicionar Nova Unidade")
def popup_adicionar_unidade():
    st.write("Digite o nome da nova unidade para incluir na lista de seleção:")
    nova_unidade = st.text_input("Nome da Unidade", placeholder="Ex: por container, por kg...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar Unidade", use_container_width=True):
            nome_limpo = nova_unidade.strip()
            if nome_limpo:
                if nome_limpo not in st.session_state["lista_unidades"]:
                    st.session_state["lista_unidades"].append(nome_limpo)
                    st.session_state["form_unidade"] = nome_limpo
                    st.success(f"Unidade '{nome_limpo}' adicionada!")
                    st.rerun()
                else:
                    st.warning("Esta unidade já existe na lista!")
            else:
                st.warning("Informe um nome para a unidade.")
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

# --- Pop-up 2: Remover Unidade ---
@st.dialog("➖ Remover Unidade da Lista")
def popup_remover_unidade():
    unidades_existentes = [u for u in st.session_state["lista_unidades"] if u != ""]
    if not unidades_existentes:
        st.info("Não há unidades para remover.")
        return

    unidade_selecionada = st.selectbox("Selecione a unidade que deseja excluir:", unidades_existentes)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Confirmar Exclusão", use_container_width=True):
            if unidade_selecionada in st.session_state["lista_unidades"]:
                st.session_state["lista_unidades"].remove(unidade_selecionada)
                if st.session_state.get("form_unidade") == unidade_selecionada:
                    st.session_state["form_unidade"] = ""
                st.success(f"Unidade '{unidade_selecionada}' removida!")
                st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

# ==============================================================================
# 4. INTERFACE DO APLICATIVO
# ==============================================================================
st.title("GLOBEX MULTIMODAL")
st.caption("Módulo de Gestão Comercial & Precificação")

tabs = st.tabs(["📋 Cadastro de Serviços", "🛠️ Propostas e Precificação"])

with tabs[0]:
    st.subheader("Cadastro e Gestão de Serviços")
    
    df_servicos = carregar_dados()

    with st.form("form_servico", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código do Serviço *", key="form_codigo", placeholder="Ex: SERV-001")
            categoria = st.selectbox(
                "Categoria *", 
                ["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"],
                key="form_categoria"
            )
            tarifa = st.number_input("Tarifa (R$) *", min_value=0.0, format="%.2f", key="form_tarifa")
        
        with col2:
            descricao = st.text_input("Descrição do Serviço *", key="form_descricao", placeholder="Ex: Armazenagem de carga paletizada")
            unidade = st.selectbox(
                "Unidade *", 
                st.session_state["lista_unidades"],
                key="form_unidade"
            )
            observacoes = st.text_area("Observações e Premissas (Opcional)", key="form_observacoes", placeholder="Ex: Faturamento mínimo mensal de 50 paletes.")
        
        btn_salvar = st.form_submit_button("💾 Cadastrar / Salvar Serviço")

    # Botões para abrir as janelas pop-up
    col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
    with col_b1:
        if st.button("➕ Nova Unidade"):
            popup_adicionar_unidade()
    with col_b2:
        if st.button("➖ Excluir Unidade"):
            popup_remover_unidade()

    # Ação de Salvamento do Serviço
    if btn_salvar:
        erros = []
        if not codigo.strip():
            erros.append("Código do Serviço")
        if not descricao.strip():
            erros.append("Descrição do Serviço")
        if not categoria:
            erros.append("Categoria")
        if not unidade:
            erros.append("Unidade")
        if tarifa <= 0:
            erros.append("Tarifa (R$) deve ser maior que 0.00")

        if not erros:
            nova_linha = pd.DataFrame([{
                "Código": codigo.strip(),
                "Descrição": descricao.strip(),
                "Tarifa (R$)": f"{tarifa:.2f}",
                "Unidade": unidade,
                "Categoria": categoria,
