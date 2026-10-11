import streamlit as st
import pandas as pd

def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_completos_fn=None, normalizar_codigo_fn=None, formatar_tarifa_fn=None):
    # Estilo CSS para garantir que todos os rótulos de campos fiquem visíveis (brancos)
    st.markdown("""
        <style>
            div[data-testid="stTextInput"] label,
            div[data-testid="stSelectbox"] label,
            div[data-testid="stNumberInput"] label,
            div[data-testid="stTextArea"] label,
            div[data-testid="stTextInput"] label p,
            div[data-testid="stSelectbox"] label p,
            div[data-testid="stNumberInput"] label p,
            div[data-testid="stTextArea"] label p {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 15px !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📋 Cadastro e Gestão de Serviços")
    st.caption("Cadastre novos serviços, visualize a tabela tarifária ativa e gerencie os itens cadastrados.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Carrega todos os dados (incluindo inativos para validação de backend)
    try:
        df_completo = carregar_dados_fn(apenas_ativos=False) if carregar_dados_fn else pd.DataFrame()
    except Exception:
        df_completo = carregar_dados_fn() if carregar_dados_fn else pd.DataFrame()

    if df_completo is None or not isinstance(df_completo, pd.DataFrame):
        df_completo = pd.DataFrame(columns=["Código", "Descrição", "Tarifa (R$)", "Unidade", "Categoria", "Observações", "Status"])

    if "Status" not in df_completo.columns:
        df_completo["Status"] = "Ativo"
    
    df_completo["Status"] = df_completo["Status"].astype(str).str.strip().replace("", "Ativo")
    df_completo["Código"] = df_completo["Código"].astype(str).str.strip()

    col_form, col_tabela = st.columns([1.1, 1.9], gap="large")

    with col_form:
        st.markdown("### ➕ Novo Serviço")
        with st.form("form_cad_servico_final_v4", clear_on_submit=True):
            codigo_input = st.text_input("Código *", placeholder="Ex: 1, 2, A1...", key="in_cad_cod_v4")
            descricao_input = st.text_input("Descrição *", placeholder="Ex: Armazenagem, Reembalagem...", key="in_cad_desc_v4")
            
            categoria_input = st.selectbox(
                "Categoria *",
                options=["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"],
                key="sel_cad_cat_v4"
            )
            
            unidade_opcoes = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês"])
            unidade_input = st.selectbox("Unidade *", options=unidade_opcoes, key="sel_cad_un_v4")
            
            tarifa_input = st.number_input("Tarifa (R$) *", min_value=0.0, step=0.01, format="%.5f", key="num_cad_tar_v4")
            obs_input = st.text_area("Observações e Premissas (Opcional)", placeholder="Ex: Faturamento mínimo...", key="area_cad_obs_v4")

            submitted = st.form_submit_button("💾 Salvar Serviço", use_container_width=True)

            if submitted:
                codigo_limp = normalizar_codigo_fn(codigo_input) if normalizar_codigo_fn else str(codigo_input).strip()
                
                if not codigo_limp or not descricao_input or not categoria_input or not unidade_input:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")
                else:
                    df_ativos_existentes = df_completo[df_completo["Status"].str.upper() != "INATIVO"]
                    codigo_ja_ativo = not df_ativos_existentes[df_ativos_existentes["Código"] == codigo_limp].empty
                    
                    if codigo_ja_ativo:
                        st.error(f"⚠️ Atenção: O Código '{codigo_limp}' equivale a um código JÁ CADASTRADO e Ativo! Escolha um código diferente.")
                    else:
                        idx_existente = df_completo[df_completo["Código"] == codigo_limp].index
                        tarifa_val = formatar_tarifa_fn(tarifa_input) if formatar_tarifa_fn else tarifa_input

                        novo_registro = {
                            "Código": codigo_limp,
                            "Descrição": descricao_input.strip(),
                            "Tarifa (R$)": tarifa_val,
                            "Unidade": unidade_input,
                            "Categoria": categoria_input,
                            "Observações": obs_input.strip() if obs_input else "",
                            "Status": "Ativo"
                        }

                        if not idx_existente.empty:
                            for k, v in novo_registro.items():
                                df_completo.loc[idx_existente[0], k] = v
                            st.success(f"Servício com o código '{codigo_limp}' (anteriormente inativo) foi reativado e atualizado com sucesso!")
                        else:
                            df_novo = pd.DataFrame([novo_registro])
                            df_completo = pd.concat([df_completo, df_novo], ignore_index=True)
                            st.success(f"Servício '{descricao_input}' cadastrado com sucesso!")

                        if salvar_dados_completos_fn:
                            salvar_dados_completos_fn(df_completo)
                        st.rerun()

    with col_tabela:
        st.markdown("### 📊 Tabela de Serviços Ativos")
        
        df_exibir = df_completo[df_completo["Status"].str.upper() != "INATIVO"].copy()
        if "Status" in df_exibir.columns:
            df_exibir = df_exibir.drop(columns=["Status"])

        if df_exibir.empty:
            st.info("Nenhum serviço ativo cadastrado.")
        else:
            st.dataframe(df_exibir, use_container_width=True, height=260, hide_index=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚙️ Gerenciar Serviço (Editar / Excluir)")
            
            ativos_lista = df_completo[df_completo["Status"].str.upper() != "INATIVO"]["Código"].tolist()
            cod_selecionado = st.selectbox("Selecione o Código do Serviço Ativo:", options=[""] + ativos_lista, key="select_servico_gerenciar_ativo_v4")
            
            if cod_selecionado:
                row_sel = df_completo[df_completo["Código"] == cod_selecionado].iloc[0]
                
                col_btn_edit, col_btn_exc = st.columns(2)
                with col_btn_edit:
                    btn_acao_editar = st.button("✏️ Editar", use_container_width=True, key="btn_edit_action_v4")
                with col_btn_exc:
                    btn_acao_excluir = st.button("🗑️ Excluir", use_container_width=True, key="btn_exc_action_v4")
                
                if btn_acao_editar:
                    st.session_state["modo_acao_servico"] = "editar"
                    st.session_state["codigo_em_edicao"] = cod_selecionado
                    st.rerun()
                
                if btn_acao_excluir:
                    idx_alvo = df_completo[df_completo["Código"] == cod_selecionado].index[0]
                    df_completo.loc[idx_alvo, "Status"] = "Inativo"
                    if salvar_dados_completos_fn:
                        salvar_dados_completos_fn(df_completo)
                    st.success("Item excluído com sucesso!")
                    st.session_state.pop("modo_acao_servico", None)
                    st.session_state.pop("codigo_em_edicao", None)
                    st.rerun()

                modo_atual = st.session_state.get("modo_acao_servico")
                codigo_editando = st.session_state.get("codigo_em_edicao")

                if modo_atual == "editar" and codigo_editando == cod_selecionado:
                    st.markdown("---")
                    st.markdown(f"##### Editando Serviço (Código Fixo: `{cod_selecionado}`)")
                    
                    edit_desc = st.text_input("Descrição *", value=str(row_sel["Descrição"]), key="edit_desc_txt_v4")
                    
                    cats = ["Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]
                    cat_atual = str(row_sel["Categoria"])
                    cat_idx = cats.index(cat_atual) if cat_atual in cats else 0
                    edit_cat = st.selectbox("Categoria *", options=cats, index=cat_idx, key="edit_cat_sel_v4")
                    
                    unidades = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês"])
                    un_atual = str(row_sel["Unidade"])
                    un_idx = unidades.index(un_atual) if un_atual in unidades else 0
                    edit_un = st.selectbox("Unidade *", options=unidades, index=un_idx, key="edit_un_sel_v4")
                    
                    try:
                        t_val_inicial = float(str(row_sel["Tarifa (R$)"]).replace(".", "").replace(",", "."))
                    except Exception:
                        try:
                            t_val_inicial = float(row_sel["Tarifa (R$)"])
                        except Exception:
                            t_val_inicial = 0.0
                            
                    edit_tarifa = st.number_input("Tarifa (R$) *", value=t_val_inicial, min_value=0.0, step=0.01, format="%.5f", key="edit_tar_num_v4")
                    edit_obs = st.text_area("Observações e Premissas (Opcional)", value=str(row_sel.get("Observações", "")), key="edit_obs_area_v4")
                    
                    col_salvar, col_cancelar = st.columns(2)
                    with col_salvar:
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_salvar_edicao_v4"):
                            # Inativa o registro antigo com o mesmo código e adiciona o novo registro atualizado
                            idx_antigo = df_completo[df_completo["Código"] == cod_selecionado].index
                            for i in idx_antigo:
                                if str(df_completo.loc[i, "Status"]).strip().upper() != "INATIVO":
                                    df_completo.loc[i, "Status"] = "Inativo"
                            
                            tarifa_val = formatar_tarifa_fn(edit_tarifa) if formatar_tarifa_fn else edit_tarifa
                            novo_registro = {
                                "Código": str(cod_selecionado),
                                "Descrição": edit_desc.strip(),
                                "Tarifa (R$)": tarifa_val,
                                "Unidade": edit_un,
                                "Categoria": edit_cat,
                                "Observações": edit_obs.strip() if edit_obs else "",
                                "Status": "Ativo"
                            }
                            
                            df_novo = pd.DataFrame([novo_registro])
                            df_completo = pd.concat([df_completo, df_novo], ignore_index=True)
                            
                            if salvar_dados_completos_fn:
                                salvar_dados_completos_fn(df_completo)
                            st.success(f"Servício '{cod_selecionado}' atualizado com sucesso!")
                            st.session_state.pop("modo_acao_servico", None)
                            st.session_state.pop("codigo_em_edicao", None)
                            st.rerun()
                    with col_cancelar:
                        if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_edicao_v4"):
                            st.session_state.pop("modo_acao_servico", None)
                            st.session_state.pop("codigo_em_edicao", None)
                            st.rerun()
