import streamlit as st
import pandas as pd
import re

def inicializar_estado_proposta():
    if "rascunho_itens" not in st.session_state:
        st.session_state["rascunho_itens"] = []
    if "_safe_cliente_nome" not in st.session_state:
        st.session_state["_safe_cliente_nome"] = ""
    if "_safe_cnpj_val" not in st.session_state:
        st.session_state["_safe_cnpj_val"] = ""

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
        st.session_state[input_key] = str(nova_tarifa)

def formatar_cnpj(val):
    digitos = "".join([c for c in str(val) if c.isdigit()])[:14]
    t = len(digitos)
    if t == 0:
        return ""
    elif t <= 2:
        return digitos
    elif t <= 5:
        return f"{digitos[:2]}.{digitos[2:]}"
    elif t <= 8:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:]}"
    elif t <= 12:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:]}"
    else:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"

def callback_cnpj():
    cnpj_formatado = formatar_cnpj(st.session_state.get("proposta_cliente_cnpj", ""))
    st.session_state["proposta_cliente_cnpj"] = cnpj_formatado
    st.session_state["_safe_cnpj_val"] = cnpj_formatado

def renderizar_bloco_categoria(titulo, categoria_filtro, df_categoria, icone_bloco):
    st.markdown(f"#### {icone_bloco} {titulo}")
    
    codigos_ja_inseridos = {str(i.get("Código", "")) for i in st.session_state["rascunho_itens"]}
    df_disponivel = df_categoria[~df_categoria["Código"].astype(str).isin(codigos_ja_inseridos)]

    if df_disponivel.empty:
        st.info(f"Todos os serviços disponíveis em '{titulo}' já foram adicionados ou não há itens.")
        renderizar_tabela_itens_bloco(titulo, categoria_filtro)
        st.markdown("---")
        return

    codigos_categoria = df_disponivel["Código"].tolist()
    opcoes = [""] + codigos_categoria
    
    col_sel, col_btn = st.columns([6, 2])
    with col_sel:
        item_selecionado = st.selectbox(
            f"Selecionar {titulo}:",
            options=opcoes,
            format_func=lambda x: "" if x == "" else f"{x} - {df_disponivel[df_disponivel['Código'] == x]['Descrição'].values[0]}",
            key=f"select_cat_{categoria_filtro}"
        )
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar", key=f"btn_add_{categoria_filtro}"):
            if item_selecionado != "":
                row = df_disponivel[df_disponivel["Código"] == item_selecionado].iloc[0]
                
                cat_original_item = str(row.get("Categoria", "")).strip().lower()
                if categoria_filtro == "OUT":
                    if "armazenagem" in cat_original_item or "seguro" in cat_original_item:
                        st.error("⚠️ Este bloco é exclusivo para Serviços Conexos (Serviços, Movimentação ou Outros). Itens de Armazenagem e Seguro devem ser inseridos nos seus blocos específicos.")
                        return

                tarifa_raw = str(row["Tarifa (R$)"]).strip()
                try:
                    tarifa_float = float(tarifa_raw.replace(",", "."))
                except ValueError:
                    tarifa_float = 0.0

                st.session_state["rascunho_itens"].append({
                    "Código": str(row["Código"]),
                    "Descrição": str(row["Descrição"]),
                    "Tarifa (R$)": tarifa_float,
                    "Unidade": str(row["Unidade"]),
                    "Observações": "",
                    "Categoria": titulo,
                    "Cat_Code": categoria_filtro
                })
                st.rerun()
            else:
                st.warning("Selecione um item antes de adicionar.")

    renderizar_tabela_itens_bloco(titulo, categoria_filtro)
    st.markdown("---")

def renderizar_tabela_itens_bloco(titulo, categoria_filtro):
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
        with h_obs: st.markdown("<b style='color: #FFFFFF;'>Observações (Editável)</b>", unsafe_allow_html=True)
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
                    st.session_state[input_key] = str(item["Tarifa (R$)"])
                tarifa_str_input = st.text_input(
                    label=f"Tarifa_{item['Código']}_{idx}",
                    label_visibility="collapsed",
                    key=input_key,
                    placeholder="0.00"
                )
                tarifa_limpa = re.sub(r'[^0-9.,]', '', tarifa_str_input)
                try:
                    nova_tarifa = float(tarifa_limpa.replace(",", ".")) if tarifa_limpa.strip() else 0.0
                except ValueError:
                    nova_tarifa = 0.0
                item["Tarifa (R$)"] = nova_tarifa
            with c_un:
                st.markdown(f"<span style='color: #FFFFFF;'>{item['Unidade']}</span>", unsafe_allow_html=True)
            with c_obs:
                obs_key = f"input_obs_{categoria_filtro}_{item['Código']}_{idx}"
                if obs_key not in st.session_state:
                    st.session_state[obs_key] = str(item.get("Observações", ""))
                obs_str_input = st.text_input(
                    label=f"Obs_{item['Código']}_{idx}",
                    label_visibility="collapsed",
                    key=obs_key,
                    placeholder="Digite observações..."
                )
                item["Observações"] = obs_str_input

def renderizar_aba_propostas(carregar_dados_fn, salvar_dados_completos_fn=None, obter_proximo_numero_fn=None, *args, **kwargs):
    inicializar_estado_proposta()
    
    if st.session_state.get("proposta_id_em_edicao"):
        numero_proposta = str(st.session_state["proposta_id_em_edicao"])
    elif st.session_state.get("proposta_id_ativo"):
        numero_proposta = str(st.session_state["proposta_id_ativo"])
    else:
        numero_proposta = obter_proximo_numero_fn() if obter_proximo_numero_fn else "10/00001/2026"
        st.session_state["proposta_id_ativo"] = numero_proposta
    
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
        
        with st.expander("➕ Nova Proposta", expanded=False):
            opcao_limpeza = st.radio(
                "O que deseja limpar?",
                ["Apenas Nome e CNPJ (Manter Itens)", "Limpar Tudo (Nome, CNPJ e Itens)"],
                key="radio_opcao_limpeza_nova_prop"
            )
            if st.button("Confirmar Nova Proposta", use_container_width=True, key="btn_confirma_nova_prop"):
                st.session_state.pop("ultimo_pdf_bytes", None)
                st.session_state.pop("ultimo_pdf_nome", None)
                st.session_state["proposta_id_em_edicao"] = None
                
                if obter_proximo_numero_fn:
                    novo_num_seq = obter_proximo_numero_fn()
                else:
                    novo_num_seq = "10/00001/2026"
                
                st.session_state["proposta_id_ativo"] = novo_num_seq
                
                if "Limpar Tudo" in opcao_limpeza:
                    st.session_state["rascunho_itens"] = []
                    for k in list(st.session_state.keys()):
                        if k.startswith("input_tarifa_") or k.startswith("input_obs_"):
                            del st.session_state[k]
                
                st.session_state["_safe_cliente_nome"] = ""
                st.session_state["_safe_cnpj_val"] = ""
                st.session_state["input_cli_nome_tela2"] = ""
                st.session_state["proposta_cliente_cnpj"] = ""
                
                st.success(f"Nova proposta iniciada com sucesso! Nº: {novo_num_seq}")
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    col_cli, col_cnpj = st.columns([2.5, 1.5])
    
    with col_cli:
        cliente_nome = st.text_input(
            "Cliente *",
            placeholder="Ex: Empresa ABC Ltda",
            value=st.session_state.get("_safe_cliente_nome", ""),
            key="input_cli_nome_tela2"
        )
        if cliente_nome:
            st.session_state["_safe_cliente_nome"] = cliente_nome
        
    with col_cnpj:
        cnpj_val = st.text_input(
            "CNPJ",
            placeholder="Ex: 00.000.000/0001-00",
            value=st.session_state.get("_safe_cnpj_val", ""),
            key="proposta_cliente_cnpj",
            on_change=callback_cnpj
        )
        if cnpj_val:
            st.session_state["_safe_cnpj_val"] = formatar_cnpj(cnpj_val)

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
        
    if not df_servicos.empty and "Código" in df_servicos.columns:
        df_servicos["_sort_key"] = pd.to_numeric(df_servicos["Código"], errors="coerce")
        df_servicos = df_servicos.sort_values(by=["_sort_key", "Código"], ascending=[True, True]).drop(columns=["_sort_key"])
        
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
    df_servicos_conexos = df_servicos[~df_servicos["Cat_Upper"].isin(["ARMAZENAGEM", "SEGURO"])]
    
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
                
    renderizar_bloco_categoria("Armazenagem", "ARM", df_armazenagem, "🏬")
    renderizar_bloco_categoria("Seguro", "SEG", df_seguro, "🛡️")
    renderizar_bloco_categoria("Serviços e Movimentações", "SER", df_servicos_handling, "⚙️")
    renderizar_bloco_categoria("Serviços Conexos", "OUT", df_servicos_conexos, "📦")
    
    todos_itens = st.session_state["rascunho_itens"]
    col_res1, col_res2 = st.columns([2, 1])
    with col_res1:
        st.markdown(f"### Total de Itens no Rascunho: **{len(todos_itens)}**")
        
    with col_res2:
        if st.button("➡️ Finalizar Lançamento e Ir para Proposta Cliente", use_container_width=True):
            cli_val = str(st.session_state.get("input_cli_nome_tela2") or st.session_state.get("_safe_cliente_nome", "")).strip()
            cnp_val = str(st.session_state.get("proposta_cliente_cnpj") or st.session_state.get("_safe_cnpj_val", "")).strip()
            
            seguro_zerado = False
            for item in todos_itens:
                cat_item = str(item.get("Categoria", "")).strip().lower()
                if cat_item == "seguro" or item.get("Cat_Code") == "SEG":
                    try:
                        t_val = float(item.get("Tarifa (R$)", 0))
                    except Exception:
                        t_val = 0.0
                    if t_val == 0.0:
                        seguro_zerado = True
                        break

            if not cli_val:
                st.error("⚠️ O campo 'Cliente *' é obrigatório!")
            elif not todos_itens:
                st.error("Adicione pelo menos um item antes de avançar.")
            elif seguro_zerado:
                st.error("⚠️ Atenção: Há itens de **Seguro** com tarifa igual a 0,0000. O percentual do seguro deve ser preenchido obrigatoriamente e ser diferente de zero.")
            else:
                st.session_state.pop("ultimo_pdf_bytes", None)
                st.session_state.pop("ultimo_pdf_nome", None)
                st.session_state["_safe_cliente_nome"] = cli_val
                st.session_state["_safe_cnpj_val"] = cnp_val
                st.session_state["proposta_id_ativo"] = numero_proposta
                st.session_state["aba_ativa"] = "cliente"
                st.rerun()
