import streamlit as st
import pandas as pd

def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_completos_fn=None, normalizar_codigo_fn=None, formatar_tarifa_fn=None):
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
        with st.form("form_cadastro_servico_unico", clear_on_submit=True):
            codigo_input = st.text_input("Código *", placeholder="Ex: 1, 2, A1...")
            descricao_input = st.text_input("Descrição *", placeholder="Ex: Armazenagem, Reembalagem...")
            
            categoria_input = st.selectbox(
                "Categoria *",
                options=["", "Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]
            )
            
            unidade_opcoes = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês"])
            unidade_input = st.selectbox("Unidade *", options=unidade_opcoes)
            
            tarifa_input = st.number_input("Tarifa (R$) *", min_value=0.0, step=0.01, format="%.5f")
            obs_input = st.text_area("Observações e Premissas (Opcional)", placeholder="Ex: Faturamento mínimo...")

            submitted = st.form_submit_button("💾 Salvar Serviço", use_container_width=True)

            if submitted:
                codigo_limp = normalizar_codigo_fn(codigo_input) if normalizar_codigo_fn else str(codigo_input).strip()
                
                if not codigo_limp or not descricao_input or not categoria_input or not unidade_input:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")
                else:
                    # Verifica se o código já existe e está ATIVO
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
                            # Reativa e atualiza o registro inativo com este mesmo código
                            for k, v in novo_registro.items():
                                df_completo.loc[idx_existente[0], k] = v
                            st.success(f"Servício com o código '{codigo_limp}' (anteriormente inativo) foi reativado e atualizado com sucesso!")
                        else:
                            # Insere novo registro
                            df_novo = pd.DataFrame([novo_registro])
                            df_completo = pd.concat([df_completo, df_novo], ignore_index=True)
                            st.success(f"Servício '{descricao_input}' cadastrado com sucesso!")

                        if salvar_dados_completos_fn:
                            salvar_dados_completos_fn(df_completo)
                        st.rerun()

    with col_tabela:
        st.markdown("### 📊 Tabela de Serviços Ativos")
        
        # Filtra apenas ativos e remove a coluna status para exibição limpa
        df_exibir = df_completo[df_completo["Status"].str.upper() != "INATIVO"].copy()
        if "Status" in df_exibir.columns:
            df_exibir = df_exibir.drop(columns=["Status"])

        if df_exibir.empty:
            st.info("Nenhum serviço ativo cadastrado.")
        else:
            # Altura fixa contida perfeitamente no bloco visual
            st.dataframe(df_exibir, use_container_width=True, height=260, hide_index=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚙️ Gerenciar Serviço (Editar / Excluir)")
            
            ativos_lista = df_completo[df_completo["Status"].str.upper() != "INATIVO"]["Código"].tolist()
            cod_selecionado = st.selectbox("Selecione o Código do Serviço Ativo:", options=[""] + ativos_lista, key="select_servico_gerenciar")
            
            if cod_selecionado:
                row_sel = df_completo[df_completo["Código"] == cod_selecionado].iloc[0]
                
                acao = st.radio("Escolha a Ação:", options=["Editar Serviço", "Excluir Serviço"], horizontal=True, key="radio_acao_servico")
                
                if acao == "Editar Serviço":
                    with st.form("form_edicao_servico_unico"):
                        st.text_input("Código (Fixo / Não Editável)", value=str(row_sel["Código"]), disabled=True)
                        
                        edit_desc = st.text_input("Descrição", value=str(row_sel["Descrição"]))
                        
                        cats = ["Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]
                        cat_atual = str(row_sel["Categoria"])
                        cat_idx = cats.index(cat_atual) if cat_atual in cats else 0
                        edit_cat = st.selectbox("Categoria", options=cats, index=cat_idx)
                        
                        unidades = st.session_state.get("lista_unidades", ["", "Por caixa", "por unidade", "por pallet", "por hora/homem", "por etiqueta", "por volume", "por mês"])
                        un_atual = str(row_sel["Unidade"])
                        un_idx = unidades.index(un_atual) if un_atual in unidades else 0
                        edit_un = st.selectbox("Unidade", options=unidades, index=un_idx)
                        
                        try:
                            t_val_inicial = float(str(row_sel["Tarifa (R$)"]).replace(".", "").replace(",", "."))
                        except Exception:
                            try:
                                t_val_inicial = float(row_sel["Tarifa (R$)"])
                            except Exception:
                                t_val_inicial = 0.0
                                
                        edit_tarifa = st.number_input("Tarifa (R$)", value=t_val_inicial, min_value=0.0, step=0.01, format="%.5f")
                        edit_obs = st.text_area("Observações", value=str(row_sel.get("Observações", "")))
                        
                        btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                        if btn_salvar_edicao:
                            idx_alvo = df_completo[df_completo["Código"] == cod_selecionado].index[0]
                            df_completo.loc[idx_alvo, "Descrição"] = edit_desc.strip()
                            df_completo.loc[idx_alvo, "Categoria"] = edit_cat
                            df_completo.loc[idx_alvo, "Unidade"] = edit_un
                            df_completo.loc[idx_alvo, "Tarifa (R$)"] = formatar_tarifa_fn(edit_tarifa) if formatar_tarifa_fn else edit_tarifa
                            df_completo.loc[idx_alvo, "Observações"] = edit_obs.strip()
                            
                            if salvar_dados_completos_fn:
                                salvar_dados_completos_fn(df_completo)
                            st.success(f"Servício '{cod_selecionado}' atualizado com sucesso!")
                            st.rerun()
                else:
                    if st.button("🗑️ Confirmar Exclusão do Serviço", type="primary", use_container_width=True):
                        idx_alvo = df_completo[df_completo["Código"] == cod_selecionado].index[0]
                        df_completo.loc[idx_alvo, "Status"] = "Inativo"
                        if salvar_dados_completos_fn:
                            salvar_dados_completos_fn(df_completo)
                        st.success(f"Servício '{cod_selecionado}' excluído com sucesso! O código foi liberado.")
                        st.rerun()
