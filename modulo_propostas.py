import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# FUNÇÕES AUXILIARES DA PROPOSTA
# ==============================================================================
def obter_proximo_numero_proposta():
    if st.session_state.get("proposta_id_em_edicao"):
        return st.session_state["proposta_id_em_edicao"]
    agora = datetime.now()
    mes = agora.strftime("%m")
    ano = agora.strftime("%Y")
    
    if "sequencial_proposta" not in st.session_state:
        st.session_state["sequencial_proposta"] = 1
        
    seq = st.session_state["sequencial_proposta"]
    return f"{mes}/{seq:05d}/{ano}"

def inicializar_estado_proposta():
    if "rascunho_itens" not in st.session_state:
        st.session_state["rascunho_itens"] = []
    if "proposta_cliente_nome" not in st.session_state:
        st.session_state["proposta_cliente_nome"] = ""
    if "proposta_cliente_cnpj" not in st.session_state:
        st.session_state["proposta_cliente_cnpj"] = ""

def remover_item_proposta_por_indice(index_para_remover):
    if 0 <= index_para_remover < len(st.session_state["rascunho_itens"]):
        item_removido = st.session_state["rascunho_itens"].pop(index_para_remover)
        for k in list(st.session_state.keys()):
            if k.endswith(f"_{item_removido.get('Código', '')}_{index_para_remover}"):
                del st.session_state[k]

def aplicar_reajuste_percentual_global(percentual):
    fator = 1.0 + (float(percentual) / 100.0)
    
    for idx, item in enumerate(st.session_state["rascunho_itens"]):
        val_atual = float(item["Tarifa (R$)"])
        nova_tarifa = round(val_atual * fator, 5)
        item["Tarifa (R$)"] = nova_tarifa
        
        cat_code = item.get("Cat_Code", "GEN")
        input_key = f"input_tarifa_{cat_code}_{item['Código']}_{idx}"
        st.session_state[input_key] = nova_tarifa

# ==============================================================================
# RENDERIZADOR DE BLOCO POR CATEGORIA
# ==============================================================================
def renderizar_bloco_categoria(titulo, categoria_filtro, df_categoria, icone_bloco):
    st.markdown(f"#### {icone_bloco} {titulo}")
    
    if df_categoria.empty:
        st.info(f"Nenhum serviço cadastrado na categoria '{titulo}'.")
        st.markdown("---")
        return
        
    codigos_categoria = df_categoria["Código"].tolist()
    opcoes = [""] + codigos_categoria
    
    col_sel, col_btn = st.columns([6, 2])
    
    with col_sel:
        item_selecionado = st.selectbox(
            f"Selecionar {titulo}:",
            options=opcoes,
            format_func=lambda x: "" if x == "" else f"{x} - {df_categoria[df_categoria['Código'] == x]['Descrição'].values[0]}",
            key=f"select_cat_{categoria_filtro}"
        )
        
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar", key=f"btn_add_{categoria_filtro}"):
            if item_selecionado != "":
                row = df_categoria[df_categoria["Código"] == item_selecionado].iloc[0]
                tarifa_raw = str(row["Tarifa (R$)"]).replace(".", "").replace(",", ".")
                try:
                    tarifa_float = float(tarifa_raw)
                except ValueError:
                    tarifa_float = float(row["Tarifa (R$)"])
                
                obs_val = str(row["Observações"]) if "Observações" in row and pd.notna(row["Observações"]) else ""
                
                ja_existe = any(str(i.get("Código", "")) == str(item_selecionado) for i in st.session_state["rascunho_itens"])
                if not ja_existe:
                    st.session_state["rascunho_itens"].append({
                        "Código": str(row["Código"]),
                        "Descrição": str(row["Descrição"]),
                        "Tarifa (R$)": tarifa_float,
                        "Unidade": str(row["Unidade"]),
                        "Observações": obs_val,
                        "Categoria": titulo,
                        "Cat_Code": categoria_filtro
                    })
                    st.rerun()
                else:
                    st.warning("Este item já foi adicionado ao rascunho.")
            else:
                st.warning("Selecione um item antes de adicionar.")
                
    itens_do_bloco_com_idx = [
        (idx, item) for idx, item in enumerate(st.session_state["rascunho_itens"])
        if item.get("Cat_Code") == categoria_filtro or item.get("Categoria") == titulo
    ]
    
    if itens_do_bloco_com_idx:
        st.markdown("<h5 style='color: #FFFFFF; font-weight: bold; margin-top: 15px;'>📋 Itens Inseridos:</h5>", unsafe_allow_html=True)
        
        h_del, h_cod, h_desc, h_tar, h_un, h_obs = st.columns([0.5, 1.2, 3.2, 2.2, 1.8, 2.2])
        with h_del: st.markdown("<b style='color: #FFFFFF;'>❌</b>", unsafe_allow_html=True)
        with h_cod: st.markdown("<b style='color: #FFFFFF;'>Código</b>", unsafe_allow_html=True)
        with h_desc: st.markdown("<b style='color: #FFFFFF;'>Descrição</b>", unsafe_allow_html=True)
        with h_tar: st.markdown("<b style='color: #FFFFFF;'>Tarifa Editável (R$)</b>", unsafe_allow_html=True)
        with h_un: st.markdown("<b style='color: #FFFFFF;'>Unidade</b>", unsafe_allow_html=True)
        with h_obs: st.markdown("<b style='color: #FFFFFF;'>Observações</b>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 4px 0 10px 0; border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
        
        for idx, item in itens_do_bloco_com_idx:
            c_del, c_cod, c_desc, c_tar, c_un, c_obs = st.columns([0.5, 1.2, 3.2, 2.2, 1.8, 2.2])
            
            with c_del:
                if st.button("❌", key=f"btn_x_{categoria_filtro}_{item['Código']}_{idx}", help="Remover item"):
                    remover_item_proposta_por_indice(idx)
                    st.rerun()
                    
            with c_cod:
                st.markdown(f"<span style='color: #FFFFFF; font-weight: bold;'>{item['Código']}</span>", unsafe_allow_html=True)
            with c_desc:
                st.markdown(f"<span style='color: #FFFFFF;'>{item['Descrição']}</span>", unsafe_allow_html=True)
            with c_tar:
                input_key = f"input_tarifa_{categoria_filtro}_{item['Código']}_{idx}"
                
                if input_key not in st.session_state:
                    st.session_state[input_key] = float(item["Tarifa (R$)"])
                    
                nova_tarifa = st.number_input(
                    label=f"Tarifa_{item['Código']}_{idx}",
                    label_visibility="collapsed",
                    min_value=0.0,
                    step=0.01,
                    format="%.5f",
                    key=input_key
                )
                item["Tarifa (R$)"] = nova_tarifa
                    
            with c_un:
                st.markdown(f"<span style='color: #FFFFFF;'>{item['Unidade']}</span>", unsafe_allow_html=True)
            with c_obs:
                st.markdown(f"<span style='color: #FFFFFF;'>{item.get('Observações', '')}</span>", unsafe_allow_html=True)
                
    st.markdown("---")

# ==============================================================================
# RENDERIZADOR PRINCIPAL ABA 2
# ==============================================================================
def renderizar_aba_propostas(carregar_dados_fn, salvar_dados_fn=None, *args, **kwargs):
    inicializar_estado_proposta()
    
    # Se não estiver a editar uma proposta existente, garante que os campos de cliente iniciam limpos
    if not st.session_state.get("proposta_id_em_edicao"):
        if "proposta_cliente_nome" in st.session_state and st.session_state.get("rascunho_itens") == []:
            # Opcional: limpa se o rascunho estiver vazio para evitar reter lixo antigo
            pass

    numero_proposta = obter_proximo_numero_proposta()
    
    st.markdown("""
        <style>
            div[data-testid="stTextInput"] label,
            div[data-testid="stTextInput"] label p {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 16px !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
            }
            div[data-testid="stExpander"] .stButton > button {
                background-color: #0052B4 !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #60A5FA !important;
                opacity: 1 !important;
                border-radius: 6px !important;
            }
            div[data-testid="stExpander"] .stButton > button:hover {
                background-color: #003B82 !important;
                color: #FFFFFF !important;
            }
            div[data-testid="stExpander"] .stButton > button p {
                color: #FFFFFF !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col_tit, col_num = st.columns([3, 1])
    with col_tit:
        st.markdown("## 📝 Proposta Rascunho")
        st.caption("Monte a estrutura comercial selecionando os serviços e ajustando as tarifas.")
    with col_num:
        st.markdown(f"### Nº: `{numero_proposta}`")
        if st.session_state.get("proposta_id_em_edicao"):
            if st.button("➕ Nova Proposta (Limpar Edição)", use_container_width=True):
                st.session_state["proposta_id_em_edicao"] = None
                st.session_state["rascunho_itens"] = []
                st.session_state["proposta_cliente_nome"] = ""
                st.session_state["proposta_cliente_cnpj"] = ""
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --------------------------------------------------------------------------
    # CAMPOS DE INPUT VINCULADOS DIRETAMENTE À SESSÃO COM LIMPEZA SEGURA
    # --------------------------------------------------------------------------
    col_cli, col_cnpj = st.columns([2.5, 1.5])
    
    with col_cli:
        cliente_nome = st.text_input(
            "Cliente *",
            placeholder="Ex: Empresa ABC Ltda",
            key="proposta_cliente_nome"
        )
        
    with col_cnpj:
        cnpj_val = st.text_input(
            "CNPJ",
            placeholder="Ex: 00.000.000/0001-00",
            key="proposta_cliente_cnpj"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        df_servicos = carregar_dados_fn(apenas_ativos=True)
    except Exception:
        try:
            df_servicos = carregar_dados_fn()
        except Exception:
            df_servicos = pd.DataFrame()
            
    if df_servicos is None or not isinstance(df_servicos, pd.DataFrame):
        df_servicos = pd.DataFrame()
        
    # Painel de Ajuste Percentual Global
    if st.session_state["rascunho_itens"]:
        with st.expander("📈 **Ajuste Percentual Geral nas Tarifas do Rascunho**", expanded=True):
            col_perc, col_apply, _ = st.columns([2, 2.5, 3.5])
            
            with col_perc:
                percentual_ajuste = st.number_input(
                    "Reajuste (%):",
                    value=0.0,
                    step=0.5,
                    format="%.2f",
                    key="input_reajuste_perc_global",
                    help="Exemplo: 5.0 para +5% ou -5.0 para 5% de desconto"
                )
            with col_apply:
                st.write("")
                st.write("")
                if st.button("⚡ Aplicar Reajuste", key="btn_aplicar_reajuste_global", use_container_width=True):
                    if percentual_ajuste != 0.0:
                        aplicar_reajuste_percentual_global(percentual_ajuste)
                        st.success(f"Reajuste de {percentual_ajuste:.2f}% aplicado!")
                        st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        
    if df_servicos.empty or "Categoria" not in df_servicos.columns:
        st.warning("Nenhum serviço ativo foi encontrado na base de dados do Google Sheets.")
        return
        
    df_servicos["Cat_Upper"] = df_servicos["Categoria"].astype(str).str.strip().str.upper()
    df_armazenagem = df_servicos[df_servicos["Cat_Upper"] == "ARMAZENAGEM"]
    df_seguro = df_servicos[df_servicos["Cat_Upper"] == "SEGURO"]
    df_servicos_handling = df_servicos[df_servicos["Cat_Upper"].isin(["SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]
    df_outros = df_servicos[~df_servicos["Cat_Upper"].isin(["ARMAZENAGEM", "SEGURO", "SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]
    
    for item in st.session_state["rascunho_itens"]:
        if not item.get("Cat_Code") or item.get("Cat_Code") == "GEN":
            cat_up = str(item.get("Categoria", "")).strip().upper()
            if cat_up == "ARMAZENAGEM":
                item["Cat_Code"] = "ARM"
            elif cat_up == "SEGURO":
                item["Cat_Code"] = "SEG"
            elif cat_up in ["SERVIÇO", "MOVIMENTAÇÃO (HANDLING)", "SERVIÇOS E MOVIMENTAÇÕES"]:
                item["Cat_Code"] = "SER"
            else:
                item["Cat_Code"] = "OUT"
                
    # 4 Blocos
    renderizar_bloco_categoria("Armazenagem", "ARM", df_armazenagem, "🏬")
    renderizar_bloco_categoria("Seguro", "SEG", df_seguro, "🛡️")
    renderizar_bloco_categoria("Serviços e Movimentações", "SER", df_servicos_handling, "⚙️")
    renderizar_bloco_categoria("Outros", "OUT", df_outros, "📦")
    
    todos_itens = st.session_state["rascunho_itens"]
    col_res1, col_res2 = st.columns([2, 1])
    
    with col_res1:
        st.markdown(f"### Total de Itens no Rascunho: **{len(todos_itens)}**")
        
    with col_res2:
        if st.button("➡️ Finalizar Lançamento e Ir para Proposta Cliente", use_container_width=True):
            if not cliente_nome.strip():
                st.error("⚠️ O campo 'Cliente *' é obrigatório!")
            elif not todos_itens:
                st.error("Adicione pelo menos um item antes de avançar.")
            else:
                st.session_state["aba_ativa"] = "cliente"
                st.rerun()
