import streamlit as st
import pandas as pd

def renderizar_aba_cadastro(*args, **kwargs):
    # Extração flexível de argumentos para evitar TypeError e duplicação de elementos no Streamlit
    carregar_dados_fn = kwargs.get("carregar_dados_fn") or (args[0] if len(args) > 0 else None)
    salvar_dados_completos_fn = kwargs.get("salvar_dados_completos_fn") or (args[1] if len(args) > 1 else None)
    normalizar_codigo_fn = kwargs.get("normalizar_codigo_fn") or (args[2] if len(args) > 2 else None)
    formatar_tarifa_fn = kwargs.get("formatar_tarifa_fn") or (args[3] if len(args) > 3 else None)

    st.markdown("## 📋 Cadastro e Gestão de Serviços")
    st.caption("Cadastre novos serviços e visualize a tabela tarifária ativa.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Carrega dados completos no backend para verificar códigos inativos para reativação
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

    col_form, col_tabela = st.columns([1.2, 1.8], gap="large")

    with col_form:
        st.markdown("### ➕ Novo Serviço")
        with st.form("form_cadastro_servico", clear_on_submit=True):
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
        st.markdown("### 📊 Tabela de Serviços")
        # Filtra apenas os ativos para exibição na tabela e remove a coluna de status
        df_exibir = df_completo[df_completo["Status"].str.upper() != "INATIVO"].copy()
        if "Status" in df_exibir.columns:
            df_exibir = df_exibir.drop(columns=["Status"])

        if df_exibir.empty:
            st.info("Nenhum serviço cadastrado.")
        else:
            st.dataframe(df_exibir, use_container_width=True, height=380, hide_index=True)
