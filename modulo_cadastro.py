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

def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_fn, normalizar_codigo_fn, formatar_tarifa_fn):
    # Garantia contra KeyError: Inicializa a lista de unidades se não existir
    if "lista_unidades" not in st.session_state:
        st.session_state["lista_unidades"] = UNIDADES_PADRAO.copy()
        
    if "form_id" not in st.session_state:
        st.session_state["form_id"] = 0

    st.markdown("### 📝 Cadastro e Gestão de Serviços")
    
    fid = st.session_state.get("form_id", 0)

    # Formulário de Cadastro
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
                min_value=0.00000, 
                step=0.00001, 
                format="%.5f", 
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
            unidades_disponiveis = [u for u in st.session_state["lista_unidades"] if u != ""]
            if unidades_disponiveis:
                unidade_para_remover = st.selectbox("Selecione para excluir", unidades_disponiveis, key="select_rem_u")
                if st.button("Confirmar Exclusão"):
                    st.session_state["lista_unidades"].remove(unidade_para_remover)
                    st.success(f"Unidade '{unidade_para_remover}' removida!")
                    st.rerun()
            else:
                st.info("Não existem unidades personalizadas para remover.")

    # Processamento de Cadastro
    if btn_salvar:
        codigo_limpo = str(codigo).strip()
        codigo_norm = normalizar_codigo_fn(codigo_limpo)
        
        df_base_completa = carregar_dados_fn(apenas_ativos=False)
        
        if not df_base_completa.empty and "Código" in df_base_completa.columns:
            codigos_existentes_norm = [
                normalizar_codigo_fn(c) for c in df_base_completa["Código"].tolist() if str(c).strip() != ""
            ]
        else:
            codigos_existentes_norm = []

        codigo_duplicado = codigo_norm in codigos_existentes_norm

        erros = []
        if not codigo_limpo:
            erros.append("Código do Serviço é obrigatório")
        elif codigo_duplicado:
            erros.append(f"O Código '{codigo_limpo}' equivale a um código JÁ CADASTRADO! Escolha um código diferente.")
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
            
            nova_linha = pd.DataFrame([{
                "Código": codigo_limpo,
                "Descrição": descricao.strip(),
                "Tarifa (R$)": tarifa_formatada,
                "Unidade": unidade,
                "Categoria": categoria,
                "Observações": observacoes.strip(),
                "Status": "Ativo"
            }])
            
            df_atualizado = pd.concat([df_base_completa, nova_linha], ignore_index=True)
            
            if salvar_dados_fn(df_atualizado):
                st.success(f"Serviço '{codigo_limpo}' salvo com sucesso!")
                st.session_state["form_id"] += 1
                st.rerun()
        else:
            campos_faltantes = " | ".join(erros)
            st.error(f"⚠️ Atenção: {campos_faltantes}")

    # Tabela de Serviços
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Base de Serviços Cadastrados")
    
    df_servicos_ativos = carregar_dados_fn(apenas_ativos=True)
    
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
                    df_base_completa = carregar_dados_fn(apenas_ativos=False)
                    mask = df_base_completa["Código"].astype(str).str.strip() == str(servico_para_excluir).strip()
                    df_base_completa.loc[mask, "Status"] = "Inativo"
                    if salvar_dados_fn(df_base_completa):
                        st.success(f"Serviço '{servico_para_excluir}' excluído com sucesso!")
                        st.rerun()
                else:
                    st.warning("Selecione um serviço para excluir.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_servicos_ativos, use_container_width=True)
