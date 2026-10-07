import streamlit as st
import pandas as pd
import gspread
import re
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

def carregar_dados():
    try:
        worksheet = obter_aba_google_sheets()
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        colunas_esperadas = ["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"]
        if df.empty or not all(col in df.columns for col in colunas_esperadas):
            return pd.DataFrame(columns=colunas_esperadas)
        return df[colunas_esperadas]
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
# 3. GERENCIAMENTO DE ESTADO E UNIDADES
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

if "form_id" not in st.session_state:
    st.session_state["form_id"] = 0

def converter_para_float(valor_texto):
    """Converte entrada do usuário em float de moeda válido."""
    if not valor_texto:
        return 0.0
    texto_limpo = re.sub(r'[^\d,. ]', '', str(valor_texto)).strip()
    if not texto_limpo:
        return 0.0
    # Substitui vírgula por ponto para conversão Python
    texto_limpo = texto_limpo.replace('.', '').replace(',', '.') if ',' in texto_limpo else texto_limpo
    try:
        return float(texto_limpo)
    except ValueError:
        return -1.0

# ==============================================================================
# 4. INTERFACE DO APLICATIVO
# ==============================================================================
st.title("GLOBEX MULTIMODAL")
st.caption("Módulo de Gestão Comercial & Precificação")

tabs = st.tabs(["📋 Cadastro de Serviços", "🛠️ Propostas e Precificação"])

with tabs[0]:
    st.subheader("Cadastro e Gestão de Serviços")
    
    df_servicos = carregar_dados()

    fid = st.session_state["form_id"]

    with st.form("form_servico", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código do Serviço *", key=f"codigo_{fid}", placeholder="Ex: SERV-001")
            categoria = st.selectbox(
                "Categoria *", 
                ["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"],
                key=f"categoria_{fid}"
            )
            tarifa_input = st.text_input("Tarifa (R$) *", key=f"tarifa_{fid}", placeholder="Ex: 15,50")
        
        with col2:
            descricao = st.text_input("Descrição do Serviço *", key=f"descricao_{fid}", placeholder="Ex: Armazenagem de carga paletizada")
            unidade = st.selectbox(
                "Unidade *", 
                st.session_state["lista_unidades"],
                key=f"unidade_{fid}"
            )
            observacoes = st.text_area("Observações e Premissas (Opcional)", key=f"obs_{fid}", placeholder="Ex: Faturamento mínimo mensal de 50 paletes.")
        
        btn_salvar = st.form_submit_button("💾 Cadastrar / Salvar Serviço")

    # Gestão de Unidades (+ / -)
    with st.expander("⚙️ Gerenciar Opções da Lista de Unidades (+ / -)"):
        col_u1, col_u2 = st.columns(2)
        
        with col_u1:
            st.markdown("**➕ Adicionar Nova Unidade**")
            nova_unidade_input = st.text_input("Nome da Unidade", placeholder="Ex: por container", key="input_add_u")
            if st.button("Confirmar Inclusão"):
                nome_limpo = nova_unidade_input.strip()
                if nome_limpo:
                    if nome_limpo not in st.session_state["lista_unidades"]:
                        st.session_state["lista_unidades"].append(nome_limpo)
                        st.success(f"Unidade '{nome_limpo}' adicionada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Esta unidade já consta na lista.")
                else:
                    st.warning("Digite um nome válido para a unidade.")
                    
        with col_u2:
            st.markdown("**➖ Remover Unidade Existente**")
            unidades_disponiveis = [u for u in st.session_state["lista_unidades"] if u != ""]
            if unidades_disponiveis:
                unidade_para_remover = st.selectbox("Selecione para excluir", unidades_disponiveis, key="select_rem_u")
                if st.button("Confirmar Exclusão"):
                    st.session_state["lista_unidades"].remove(unidade_para_remover)
                    st.success(f"Unidade '{unidade_para_remover}' removida!")
                    st.rerun()
            else:
                st.info("Não existem unidades personalizadas para remover.")

    # Processamento e validação ao salvar
    if btn_salvar:
        erros = []
        val_tarifa = converter_para_float(tarifa_input)

        if not codigo.strip():
            erros.append("Código do Serviço")
        if not descricao.strip():
            erros.append("Descrição do Serviço")
        if not categoria:
            erros.append("Categoria")
        if not unidade:
            erros.append("Unidade")
        if val_tarifa <= 0:
            erros.append("Tarifa (R$) válida e maior que 0.00 (digite apenas números e vírgula/ponto)")

        if not erros:
            nova_linha = pd.DataFrame([{
                "Código": codigo.strip(),
                "Descrição": descricao.strip(),
                "Tarifa (R$)": f"{val_tarifa:.2f}",
                "Unidade": unidade,
                "Categoria": categoria,
                "Observações": observacoes.strip()
            }])
            
            # Recarrega antes de concatenar para evitar resgatar itens excluídos
            df_base_fresca = carregar_dados()
            df_atualizado = pd.concat([df_base_fresca, nova_linha], ignore_index=True)
            
            if salvar_dados(df_atualizado):
                st.success(f"Serviço '{codigo}' salvo com sucesso!")
                st.session_state["form_id"] += 1
                st.rerun()
        else:
            campos_faltantes = " | ".join(erros)
            st.warning(f"Por favor, verifique os seguintes campos obrigatórios: **{campos_faltantes}**")

    st.markdown("---")
    st.subheader("🔍 Base de Serviços Cadastrados")
    
    df_editavel = st.data_editor(
        df_servicos, 
        num_rows="dynamic", 
        use_container_width=True,
        key="tabela_servicos_editor"
    )
    
    if st.button("💾 Sincronizar Alterações / Exclusões da Tabela"):
        if salvar_dados(df_editavel):
            st.success("Alterações e exclusões salvas no Google Sheets com sucesso!")
            st.rerun()

with tabs[1]:
    st.info("Módulo reservado para simulações e formação de propostas comerciais.")
