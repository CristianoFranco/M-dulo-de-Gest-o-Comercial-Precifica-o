import streamlit as pd_st # (mantém importações originais)
import streamlit as st
import pandas as pd
import re
from datetime import datetime

def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_completos_fn=None, normalizar_codigo_fn=None, formatar_tarifa_fn=None):
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
                color: #2E86DE !important;
                font-weight: bold !important;
                font-size: 15px !important;
            }
            div[data-testid="stDataFrame"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📋 Cadastro e Gestão de Serviços")
    st.caption("Cadastre novos serviços, visualize a tabela tarifária ativa e gerencie os itens cadastrados.")
    st.markdown("<br>", unsafe_allow_html=True)

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
        
        if "form_cad_version" not in st.session_state:
            st.session_state["form_cad_version"] = 1

        ver = st.session_state["form_cad_version"]

        codigo_input = st.text_input("Código *", placeholder="Ex: 1, 2, A1...", key=f"cad_codigo_v16_{ver}")
        descricao_input = st.text_input("Descrição *", placeholder="Ex: Armazenagem, Reembalagem...", key=f"cad_desc_v16_{ver}")
        
        categoria_input = st.selectbox(
            "Categoria *",
            options=["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"],
            key=f"cad_cat_v16_{ver}"
        )
        
        unidade_opcoes = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês", "percentual"])
        unidade_input = st.selectbox("Unidade *", options=unidade_opcoes, key=f"cad_un_v16_{ver}")
        
        if f"limpar_input_unidade_{ver}" not in st.session_state:
            st.session_state[f"limpar_input_unidade_{ver}"] = False

        chave_input_nova_unidade = f"input_nova_unidade_personalizada_{ver}"
        if st.session_state[f"limpar_input_unidade_{ver}"]:
            st.session_state[chave_input_nova_unidade] = ""
            st.session_state[f"limpar_input_unidade_{ver}"] = False

        with st.container():
            col_add_un1, col_add_un2 = st.columns([2.5, 1])
            with col_add_un1:
                nova_unidade_txt = st.text_input("Cadastrar Nova Unidade:", placeholder="Ex: por container", key=chave_input_nova_unidade, label_visibility="collapsed")
            with col_add_un2:
                if st.button("➕ Adicionar", key=f"btn_incluir_nova_unidade_{ver}", use_container_width=True):
                    if nova_unidade_txt.strip():
                        unidade_formatada = nova_unidade_txt.strip()
                        lista_atual = st.session_state.get("lista_unidades", unidade_opcoes.copy())
                        if unidade_formatada not in lista_atual:
                            lista_atual.append(unidade_formatada)
                            st.session_state["lista_unidades"] = lista_atual
                            st.session_state[f"limpar_input_unidade_{ver}"] = True
                            st.success(f"Adicionada!")
                            st.rerun()
                        else:
                            st.warning("Já existe.")
                    else:
                        st.error("Digite o nome.")

        st.markdown("<br>", unsafe_allow_html=True)

        is_seguro_form = str(categoria_input).strip().lower() == "seguro"
        if is_seguro_form:
            tarifa_input = 0.0
            st.info("ℹ️ Categoria 'Seguro' selecionada: o campo de tarifa está oculto e será preenchido dinamicamente na Proposta Rascunho.")
        else:
            tarifa_str_input = st.text_input("Tarifa (R$) *", value="", placeholder="Ex: 150.00", key=f"cad_tar_txt_v16_{ver}")
            
            tarifa_limpa = re.sub(r'[^0-9.,]', '', tarifa_str_input)
            
            try:
                tarifa_input = float(tarifa_limpa.replace(",", ".")) if tarifa_limpa.strip() else 0.0
            except ValueError:
                tarifa_input = 0.0

        obs_input = st.text_area("Observações e Premissas (Opcional)", placeholder="Ex: Faturamento mínimo...", key=f"cad_obs_v16_{ver}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salvar Serviço", use_container_width=True, type="primary", key=f"btn_salvar_novo_servico_v16_{ver}"):
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
                    
                    tarifa_val = 0.0 if is_seguro_form else (formatar_tarifa_fn(tarifa_input) if formatar_tarifa_fn else tarifa_input)

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

                    st.session_state["form_cad_version"] += 1
                    st.rerun()

    with col_tabela:
        st.markdown("### 📊 Tabela de Serviços Ativos")
        
        df_exibir = df_completo[df_completo["Status"].str.upper() != "INATIVO"].copy()
        if "Status" in df_exibir.columns:
            df_exibir = df_exibir.drop(columns=["Status"])

        # ORDENAÇÃO CRESCENTE POR CÓDIGO (Suporta números e textos corretamente)
        if not df_exibir.empty and "Código" in df_exibir.columns:
            df_exibir["_sort_key"] = pd.to_numeric(df_exibir["Código"], errors="coerce")
            df_exibir = df_exibir.sort_values(by=["_sort_key", "Código"], ascending=[True, True]).drop(columns=["_sort_key"])

        if df_exibir.empty:
            st.info("Nenhum serviço ativo cadastrado.")
        else:
            st.dataframe(df_exibir, use_container_width=True, height=280, hide_index=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚙️ Gerenciar Serviço (Editar / Excluir)")
            
            df_ativos = df_completo[df_completo["Status"].str.upper() != "INATIVO"].copy()
            if not df_ativos.empty and "Código" in df_ativos.columns:
                df_ativos["_sort_key"] = pd.to_numeric(df_ativos["Código"], errors="coerce")
                df_ativos = df_ativos.sort_values(by=["_sort_key", "Código"], ascending=[True, True]).drop(columns=["_sort_key"])
            
            opcoes_select = [""]
            mapa_codigos = {}
            for _, r in df_ativos.iterrows():
                c_val = str(r["Código"])
                d_val = str(r["Descrição"])
                label_opcao = f"{c_val} - {d_val}"
                opcoes_select.append(label_opcao)
                mapa_codigos[label_opcao] = c_val

            selecao_completa = st.selectbox("Selecione o Serviço Ativo:", options=opcoes_select, key="select_servico_gerenciar_ativo_v16")
            
            cod_selecionado = mapa_codigos.get(selecao_completa, "") if selecao_completa else ""
            
            if cod_selecionado:
                row_sel = df_completo[(df_completo["Código"] == cod_selecionado) & (df_completo["Status"].str.upper() != "INATIVO")].iloc[0]
                
                col_btn_edit, col_btn_exc = st.columns(2)
                with col_btn_edit:
                    btn_acao_editar = st.button("✏️ Editar", use_container_width=True, key="btn_edit_action_v16")
                with col_btn_exc:
                    btn_acao_excluir = st.button("🗑️ Excluir", use_container_width=True, key="btn_exc_action_v16")
                
                if btn_acao_editar:
                    st.session_state["modo_acao_servico"] = "editar"
                    st.session_state["codigo_em_edicao"] = cod_selecionado
                    st.rerun()
                
                if btn_acao_excluir:
                    idx_alvo = df_completo[(df_completo["Código"] == cod_selecionado) & (df_completo["Status"].str.upper() != "INATIVO")].index[0]
                    
                    df_completo.loc[idx_alvo, "Código"] = f"DEL_{cod_selecionado}_{int(datetime.now().timestamp())}"
                    df_completo.loc[idx_alvo, "Status"] = "Inativo"
                    
                    if salvar_dados_completos_fn:
                        salvar_dados_completos_fn(df_completo)
                    st.success("Item excluído com sucesso e código liberado para uso!")
                    st.session_state.pop("modo_acao_servico", None)
                    st.session_state.pop("codigo_em_edicao", None)
                    st.rerun()

                modo_atual = st.session_state.get("modo_acao_servico")
                codigo_editando = st.session_state.get("codigo_em_edicao")

                if modo_atual == "editar" and codigo_editando == cod_selecionado:
                    st.markdown("---")
                    st.markdown(f"##### Editando Serviço (Código Fixo: `{cod_selecionado}`)")
                    
                    edit_desc = st.text_input("Descrição *", value=str(row_sel["Descrição"]), key="edit_desc_txt_v16")
                    
                    cats = ["Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]
                    cat_atual = str(row_sel["Categoria"])
                    cat_idx = cats.index(cat_atual) if cat_atual in cats else 0
                    edit_cat = st.selectbox("Categoria *", options=cats, index=cat_idx, key="edit_cat_sel_v16")
                    
                    unidades = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês", "percentual"])
                    un_atual = str(row_sel["Unidade"])
                    un_idx = unidades.index(un_atual) if un_atual in unidades else 0
                    edit_un = st.selectbox("Unidade *", options=unidades, index=un_idx, key="edit_un_sel_v16")
                    
                    is_seguro_edit = str(edit_cat).strip().lower() == "seguro"
                    if is_seguro_edit:
                        edit_tarifa = 0.0
                        st.info("ℹ️ Para serviços de Seguro, a tarifa é controlada diretamente na Proposta Rascunho.")
                    else:
                        try:
                            t_val_inicial = str(row_sel["Tarifa (R$)"]).strip()
                            if t_val_inicial in ["0.0", "0", "0.00", "nan"]:
                                t_val_inicial = ""
                        except Exception:
                            t_val_inicial = ""
                        
                        edit_tarifa_str = st.text_input("Tarifa (R$) *", value=t_val_inicial, placeholder="Ex: 150.00", key="edit_tar_txt_v16")
                        
                        edit_tarifa_limpa = re.sub(r'[^0-9.,]', '', edit_tarifa_str)
                        try:
                            edit_tarifa = float(edit_tarifa_limpa.replace(",", ".")) if edit_tarifa_limpa.strip() else 0.0
                        except ValueError:
                            edit_tarifa = 0.0
                        
                    edit_obs = st.text_area("Observações e Premissas (Opcional)", value=str(row_sel.get("Observações", "")), key="edit_obs_area_v16")
                    
                    col_salvar, col_cancelar = st.columns(2)
                    with col_salvar:
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_salvar_edicao_v16"):
                            idx_antigo = df_completo[(df_completo["Código"] == cod_selecionado) & (df_completo["Status"].str.upper() != "INATIVO")].index
                            for i in idx_antigo:
                                df_completo.loc[i, "Status"] = "Inativo"
                            
                            tarifa_val = 0.0 if is_seguro_edit else (formatar_tarifa_fn(edit_tarifa) if formatar_tarifa_fn else edit_tarifa)

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
                        if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_edicao_v16"):
                            st.session_state.pop("modo_acao_servico", None)
                            st.session_state.pop("codigo_em_edicao", None)
                            st.rerun()
