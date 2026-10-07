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

def carregar_dados(apenas_ativos=True):
    try:
        worksheet = obter_aba_google_sheets()
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        colunas_esperadas = ["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações", "Status"]
        
        if df.empty:
            df_vazio = pd.DataFrame(columns=colunas_esperadas)
            return df_vazio[colunas_esperadas[:-1]] if apenas_ativos else df_vazio

        # Garante a existência da coluna Status
        if "Status" not in df.columns:
            df["Status"] = "Ativo"
        
        # Preenche status vazios como Ativo
        df["Status"] = df["Status"].astype(str).str.strip()
        df["Status"] = df["Status"].replace("", "Ativo")

        # Converte a coluna Código inteira para string/texto sem decimais indesejados
        df["Código"] = df["Código"].astype(str).str.strip()

        if apenas_ativos:
            df_ativos = df[df["Status"].str.upper() != "INATIVO"].copy()
            return df_ativos[["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"]]
        
        return df
    except Exception as e:
        import traceback
        st.error(f"Erro ao carregar dados do Google Sheets: {type(e).__name__} - {str(e)}")
        st.caption(f"Detalhes técnicos: {traceback.format_exc()}")
        return pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações"])

def salvar_dados_completos(df_completo):
    try:
        worksheet = obter_aba_google_sheets()
        worksheet.clear()
        
        # Converte explicitamente a coluna Código em texto para gravação no Sheets
        df_salvar = df_completo.copy()
        df_salvar["Código"] = df_salvar["Código"].astype(str).str.strip()
        
        dados_lista = [df_salvar.columns.values.tolist()] + df_salvar.astype(str).values.tolist()
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

# ==============================================================================
# 4. INTERFACE DO APLICATIVO
# ==============================================================================
st.title("GLOBEX MULTIMODAL")
st.caption("Módulo de Gestão Comercial & Precificação")

tabs = st.tabs(["📋 Cadastro de Serviços", "🛠️ Propostas e Precificação"])

with tabs[0]:
    st.subheader("Cadastro e Gestão de Serviços")
    
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
            tarifa = st.number_input(
                "Tarifa (R$) *", 
                min_value=0.00, 
                step=0.01, 
                format="%.2f", 
                key=f"tarifa_{fid}"
            )
        
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

    # Processamento de Cadastro e Validação Rígida
    if btn_salvar:
        codigo_limpo = str(codigo).strip()
        df_base_completa = carregar_dados(apenas_ativos=False)
        
        # Normalização rigorosa para comparar strings idênticas
        if not df_base_completa.empty and "Código" in df_base_completa.columns:
            codigos_existentes = [str(c).strip().upper() for c in df_base_completa["Código"].tolist() if str(c).strip() != ""]
        else:
            codigos_existentes = []

        codigo_duplicado = codigo_limpo.upper() in codigos_existentes

        erros = []
        if not codigo_limpo:
            erros.append("Código do Serviço é obrigatório")
        elif codigo_duplicado:
            erros.append(f"O Código '{codigo_limpo}' JÁ ESTÁ CADASTRADO! Escolha um código diferente")
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
                "Código": codigo_limpo,
                "Descrição": descricao.strip(),
                "Tarifa (R$)": f"{tarifa:.2f}",
                "Unidade": unidade,
                "Categoria": categoria,
                "Observações": observacoes.strip(),
                "Status": "Ativo"
            }])
            
            df_atualizado = pd.concat([df_base_completa, nova_linha], ignore_index=True)
            
            if salvar_dados_completos(df_atualizado):
                st.success(f"Serviço '{codigo_limpo}' salvo com sucesso!")
                st.session_state["form_id"] += 1
                st.rerun()
        else:
            campos_faltantes = " | ".join(erros)
            st.error(f"⚠️ Atenção: {campos_faltantes}")

    # Tabela de Serviços
    st.markdown("---")
    st.subheader("🔍 Base de Serviços Cadastrados")
    
    df_servicos_ativos = carregar_dados(apenas_ativos=True)
    
    # Exclusão via seleção direta
    if not df_servicos_ativos.empty:
        servicos_lista = df_servicos_ativos["Código"].tolist()
        
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            servico_para_excluir = st.selectbox("Selecione um serviço para EXCLUIR:", [""] + servicos_lista)
        with col_del2:
            st.write("")
            st.write("")
            if st.button("🗑️ Excluir Serviço Selecionado"):
                if servico_para_excluir:
                    df_base_completa = carregar_dados(apenas_ativos=False)
                    mask = df_base_completa["Código"].astype(str).str.strip() == str(servico_para_excluir).strip()
                    df_base_completa.loc[mask, "Status"] = "Inativo"
                    if salvar_dados_completos(df_base_completa):
                        st.success(f"Serviço '{servico_para_excluir}' excluído com sucesso!")
                        st.rerun()
                else:
                    st.warning("Selecione um serviço para excluir.")

    st.markdown("---")
    st.dataframe(df_servicos_ativos, use_container_width=True)

with tabs[1]:
    st.info("Módulo reservado para simulações e formação de propostas comerciais.")
