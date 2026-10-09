import streamlit as st
import pandas as pd

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

def aplicar_estilos_botoes():
    st.markdown("""
        <style>
            div[data-testid="stExpander"] div.stButton > button,
            .btn-editar-container div.stButton > button,
            .btn-acao-form div.stButton > button {
                background-color: #0052B4 !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #60A5FA !important;
                opacity: 1 !important;
            }
            div[data-testid="stExpander"] div.stButton > button p,
            .btn-editar-container div.stButton > button p,
            .btn-acao-form div.stButton > button p {
                color: #FFFFFF !important;
                font-weight: bold !important;
            }
            div[data-testid="stExpander"] div.stButton > button:hover,
            .btn-editar-container div.stButton > button:hover,
            .btn-acao-form div.stButton > button:hover {
                background-color: #003B82 !important;
                border-color: #93C5FD !important;
            }
            
            div[data-testid="stExpander"] .btn-excluir-unidade-container div.stButton > button,
            .btn-excluir-servico-container div.stButton > button {
                background-color: #D32F2F !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #EF4444 !important;
                opacity: 1 !important;
            }
            div[data-testid="stExpander"] .btn-excluir-unidade-container div.stButton > button p,
            .btn-excluir-servico-container div.stButton > button p {
                color: #FFFFFF !important;
                font-weight: bold !important;
            }
            div[data-testid="stExpander"] .btn-excluir-unidade-container div.stButton > button:hover,
            .btn-excluir-servico-container div.stButton > button:hover {
                background-color: #991B1B !important;
                border-color: #F87171 !important;
            }
        </style>
    """, unsafe_allow_html=True)


def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_fn, normalizar_codigo_fn, formatar_tarifa_fn):
    aplicar_estilos_botoes()

    if "lista_unidades" not in st.session_state:
        st.session_state["lista_unidades"] = UNIDADES_PADRAO.copy()
        
    if "form_id" not in st.session_state:
        st.session_state["form_id"] = 0

    if "modo_edicao_codigo" not in st.session_state:
        st.session_state["modo_edicao_codigo"] = None

    st.markdown("### 📝 Cadastro e Gestão de Serviços")
    
    fid = st.session_state.get("form_id", 0)
    modo_edicao = st.session_state["modo_edicao_codigo"] is not None

    df_base_completa = carregar_dados_fn(apenas_ativos=False)
    if df_base_completa is None or not isinstance(df_base_completa, pd.DataFrame):
        df_base_completa = pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações", "Status"])
    
    if "Status" not in df_base_completa.columns:
        df_base_completa["Status"] = "Ativo"

    dados_edicao = {}
    if modo_edicao:
        reg_atual = df_base_completa[df_base_completa["Código"].astype(str).str.strip() == str(st.session_state["modo_edicao_codigo"])]
        if not reg_atual.empty:
            dados_edicao = reg_atual.iloc[0].to_dict()
            st.info(f"✏️ Editando o serviço código: **{st.session_state['modo_edicao_codigo']}**")

    k_cod = f"codigo_{fid}"
    k_cat = f"categoria_{fid}"
    k_tar = f"tarifa_{fid}"
    k_desc = f"descricao_{fid}"
    k_uni = f"unidade_{fid}"
    k_obs = f"obs_{fid}"

    if modo_edicao:
        if k_cod not in st.session_state or st.session_state.get("_ultimo_editado") != st.session_state["modo_edicao_codigo"]:
            st.session_state[k_cod] = str(dados_edicao.get("Código", ""))
            st.session_state[k_cat] = str(dados_edicao.get("Categoria", ""))
            try:
                st.session_state[k_tar] = float(dados_edicao.get("Tarifa (R$)", 0.0))
            except ValueError:
                st.session_state[k_tar] = 0.0
            st.session_state[k_desc] = str(dados_edicao.get("Descrição", ""))
            st.session_state[k_uni] = str(dados_edicao.get("Unidade", ""))
            st.session_state[k_obs] = str(dados_edicao.get("Observações", ""))
            st.session_state["_ultimo_editado"] = st.session_state["modo_edicao_codigo"]
    else:
        if k_cod not in st.session_state or st.session_state.get("_ultimo_editado") is not None:
            st.session_state[k_cod] = ""
            st.session_state[k_cat] = ""
            st.session_state[k_tar] = 0.00000
            st.session_state[k_desc] = ""
            st.session_state[k_uni] = ""
            st.session_state[k_obs] = ""
            st.session_state["_ultimo_editado"] = None

    # Formulário de Cadastro / Edição
    with st.form("form_servico", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código do Serviço *", key=k_cod, placeholder="Ex: SERV-001")
            
            categorias_opcoes = ["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]
            categoria = st.selectbox("Categoria *", options=categorias_opcoes, key=k_cat)
            
            tarifa = st.number_input("Tarifa (R$) *", min_value=0.00000, step=0.00001, format="%.5f", key=k_tar)
        
        with col2:
            descricao = st.text_input("Descrição do Serviço *", key=k_desc, placeholder="Ex: Armazenagem de carga paletizada")
            
            unidades_disponiveis_form = st.session_state["lista_unidades"]
            unidade = st.selectbox("Unidade *", options=unidades_disponiveis_form, key=k_uni)
            
            observacoes = st.text_area("Observações e Premissas (Opcional)", key=k_obs, placeholder="Ex: Faturamento mínimo mensal de 50 paletes.")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            btn_salvar = st.form_submit_button("💾 Cadastrar / Salvar Serviço" if not modo_edicao else "💾 Atualizar Alterações")
        if modo_edicao:
            with col_f2:
                btn_cancelar = st.form_submit_button("❌ Cancelar Edição")
        else:
            btn_cancelar = False

    st.markdown("<br>", unsafe_allow_html=True)

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
            unidades_remover_list = [u for u in st.session_state["lista_unidades"] if u != ""]
            if unidades_remover_list:
                unidade_para_remover = st.selectbox("Selecione para excluir", unidades_remover_list, key="select_rem_u")
                st.markdown('<div class="btn-excluir-unidade-container">', unsafe_allow_html=True)
                if st.button("Confirmar Exclusão"):
                    st.session_state["lista_unidades"].remove(unidade_para_remover)
                    st.success(f"Unidade '{unidade_para_remover}' removida!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Não existem unidades personalizadas para remover.")

    # Ação de Cancelar Edição
    if btn_cancelar:
        st.session_state["modo_edicao_codigo"] = None
        st.session_state["_ultimo_editado"] = None
        st.session_state["form_id"] += 1
        st.rerun()

    # Processamento de Cadastro ou Edição (Salvar / Atualizar)
    if btn_salvar:
        codigo_limpo = str(codigo).strip()
        codigo_norm = normalizar_codigo_fn(codigo_limpo)
        
        if not df_base_completa.empty and "Código" in df_base_completa.columns and "Status" in df_base_completa.columns:
            df_ativos_val = df_base_completa[df_base_completa["Status"].astype(str).str.upper() != "INATIVO"]
            codigos_ativos_norm = [normalizar_codigo_fn(c) for c in df_ativos_val["Código"].tolist() if str(c).strip() != ""]
        else:
            codigos_ativos_norm = []

        if modo_edicao and normalizar_codigo_fn(st.session_state["modo_edicao_codigo"]) == codigo_norm:
            codigo_duplicado = False
        else:
            codigo_duplicado = codigo_norm in codigos_ativos_norm

        erros = []
        if not codigo_limpo:
            erros.append("Código do Serviço é obrigatório")
        elif codigo_duplicado:
            erros.append(f"O Código '{codigo_limpo}' já está em uso por um serviço ATIVO! Escolha outro código.")
        if not descricao.strip():
            erros.append("Descrição do Serviço")
        if not categoria:
            erros.append("Categoria")
        if not unidade:
            erros.append("Unidade")
        if tarifa <= 0:
            erros.append("Tarifa (R$) deve ser maior que 0.00000")

        if not erros:
            tarifa_formatada = formatar_tarifa_fn(tarifa)
            
            if modo_edicao:
                mask_ed = df_base_completa["Código"].astype(str).str.strip() == str(st.session_state["modo_edicao_codigo"]).strip()
                df_base_completa.loc[mask_ed, "Código"] = codigo_limpo
                df_base_completa.loc[mask_ed, "Descrição"] = descricao.strip()
                df_base_completa.loc[mask_ed, "Tarifa (R$)"] = tarifa_formatada
                df_base_completa.loc[mask_ed, "Unidade"] = unidade
                df_base_completa.loc[mask_ed, "Categoria"] = categoria
                df_base_completa.loc[mask_ed, "Observações"] = observacoes.strip()
                df_base_completa.loc[mask_ed, "Status"] = "Ativo"
                
                st.session_state["modo_edicao_codigo"] = None
                st.session_state["_ultimo_editado"] = None
                msg_sucesso = f"Serviço '{codigo_limpo}' atualizado com sucesso!"
            else:
                mask_inativo = df_base_completa["Código"].astype(str).str.strip() == codigo_limpo
                if not df_base_completa[mask_inativo].empty:
                    df_base_completa.loc[mask_inativo, "Descrição"] = descricao.strip()
                    df_base_completa.loc[mask_inativo, "Tarifa (R$)"] = tarifa_formatada
                    df_base_completa.loc[mask_inativo, "Unidade"] = unidade
                    df_base_completa.loc[mask_inativo, "Categoria"] = categoria
                    df_base_completa.loc[mask_inativo, "Observações"] = observacoes.strip()
                    df_base_completa.loc[mask_inativo, "Status"] = "Ativo"
                else:
                    nova_linha = pd.DataFrame([{
                        "Código": codigo_limpo,
                        "Descrição": descricao.strip(),
                        "Tarifa (R$)": tarifa_formatada,
                        "Unidade": unidade,
                        "Categoria": categoria,
                        "Observações": observacoes.strip(),
                        "Status": "Ativo"
                    }])
                    df_base_completa = pd.concat([df_base_completa, nova_linha], ignore_index=True)
                msg_sucesso = f"Serviço '{codigo_limpo}' cadastrado com sucesso!"
            
            if salvar_dados_fn(df_base_completa):
                st.success(msg_sucesso)
                st.session_state["form_id"] += 1
                st.rerun()
        else:
            campos_faltantes = " | ".join(erros)
            st.error(f"⚠️ Atenção: {campos_faltantes}")

    # Tabela e Gestão de Serviços Ativos
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Base de Serviços Cadastrados")
    
    df_servicos_ativos = carregar_dados_fn(apenas_ativos=True)
    
    if not df_servicos_ativos.empty:
        df_servicos_ativos_copia = df_servicos_ativos.copy()
        df_servicos_ativos_copia["Opcao_Select"] = df_servicos_ativos_copia["Código"].astype(str) + " - " + df_servicos_ativos_copia["Descrição"].astype(str)
        lista_opcoes_servicos = [""] + df_servicos_ativos_copia["Opcao_Select"].tolist()
        
        col_sel_s, col_btn_edit, col_btn_del = st.columns([3, 1.2, 1.2])
        
        with col_sel_s:
            servico_escolhido = st.selectbox("Selecione um serviço (Código e Descrição):", options=lista_opcoes_servicos)
            
        codigo_selecionado = servico_escolhido.split(" - ")[0].strip() if servico_escolhido else ""

        with col_btn_edit:
            st.write("")
            st.write("")
            st.markdown('<div class="btn-editar-container">', unsafe_allow_html=True)
            if st.button("✏️ Editar"):
                if codigo_selecionado:
                    st.session_state["modo_edicao_codigo"] = codigo_selecionado
                    st.session_state["form_id"] += 1
                    st.rerun()
                else:
                    st.warning("Selecione um serviço para editar.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_btn_del:
            st.write("")
            st.write("")
            st.markdown('<div class="btn-excluir-servico-container">', unsafe_allow_html=True)
            if st.button("🗑️ Excluir"):
                if codigo_selecionado:
                    df_completa_del = carregar_dados_fn(apenas_ativos=False)
                    mask = df_completa_del["Código"].astype(str).str.strip() == codigo_selecionado
                    df_completa_del.loc[mask, "Status"] = "Inativo"
                    if salvar_dados_fn(df_completa_del):
                        st.success(f"Serviço '{codigo_selecionado}' excluído com sucesso!")
                        if st.session_state.get("modo_edicao_codigo") == codigo_selecionado:
                            st.session_state["modo_edicao_codigo"] = None
                            st.session_state["_ultimo_editado"] = None
                        st.rerun()
                else:
                    st.warning("Selecione um serviço para excluir.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Exibe explicitamente a tabela de dados ativos abaixo dos botões de gestão
    df_exibicao = df_servicos_ativos.copy()
    if "Opcao_Select" in df_exibicao.columns:
        df_exibicao = df_exibicao.drop(columns=["Opcao_Select"])
        
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
