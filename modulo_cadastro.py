import streamlit as st
import pandas as pd

# ==============================================================================
# ESTILIZAÇÃO CSS EXCLUSIVA PARA OS BOTÕES (DENTRO E FORA DO EXPANDER)
# ==============================================================================
def aplicar_estilos_botoes_cadastro():
    st.markdown("""
        <style>
            /* Botão de Inclusão / Ações do Expander (Azul com Texto Branco) */
            div[data-testid="stExpander"] div.stButton > button {
                background-color: #0052B4 !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #60A5FA !important;
                opacity: 1 !important;
            }
            div[data-testid="stExpander"] div.stButton > button p {
                color: #FFFFFF !important;
                font-weight: bold !important;
            }
            div[data-testid="stExpander"] div.stButton > button:hover {
                background-color: #003B82 !important;
                border-color: #93C5FD !important;
            }

            /* Botão de Exclusão Especificamente (Vermelho com Texto Branco) */
            div[data-testid="stExpander"] .btn-excluir-container div.stButton > button {
                background-color: #D32F2F !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #EF4444 !important;
                opacity: 1 !important;
            }
            div[data-testid="stExpander"] .btn-excluir-container div.stButton > button p {
                color: #FFFFFF !important;
                font-weight: bold !important;
            }
            div[data-testid="stExpander"] .btn-excluir-container div.stButton > button:hover {
                background-color: #991B1B !important;
                border-color: #F87171 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# RENDERIZADOR PRINCIPAL ABA 1 - CADASTRO
# ==============================================================================
def renderizar_aba_cadastro(carregar_dados_fn, salvar_dados_fn, normalizar_codigo_fn=None, formatar_tarifa_fn=None):
    aplicar_estilos_botoes_cadastro()
    
    st.markdown("## 📋 Cadastro de Serviços e Tarifas")
    st.caption("Gerencie o catálogo principal de serviços, unidades e valores base.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "lista_unidades" not in st.session_state:
        st.session_state["lista_unidades"] = ["por mês", "Por caixa", "por volume", "Por conteiner", "Por pallet", "Por hora"]
        
    if "lista_categorias" not in st.session_state:
        st.session_state["lista_categorias"] = ["Armazenagem", "Seguro", "Serviço", "Movimentação (Handling)", "Outros"]

    # --------------------------------------------------------------------------
    # EXPANDER: GERENCIAR UNIDADES (INCLUIR / EXCLUIR)
    # --------------------------------------------------------------------------
    with st.expander("⚙️ Gerenciar Opções da Lista de Unidades (+ / -)", expanded=False):
        col_add, col_rem = st.columns(2)
        
        with col_add:
            st.markdown("##### ➕ Adicionar Nova Unidade")
            nova_unidade = st.text_input("Nome da Unidade", placeholder="Ex: por container", key="input_nova_unidade")
            if st.button("Confirmar Inclusão", key="btn_confirmar_inc_unidade"):
                if nova_unidade.strip():
                    if nova_unidade.strip() not in st.session_state["lista_unidades"]:
                        st.session_state["lista_unidades"].append(nova_unidade.strip())
                        st.success(f"Unidade '{nova_unidade}' adicionada!")
                        st.rerun()
                    else:
                        st.warning("Esta unidade já existe na lista.")
                else:
                    st.warning("Digite um nome válido.")

        with col_rem:
            st.markdown("##### ➖ Remover Unidade Existente")
            unidade_excluir = st.selectbox("Selecione para excluir", options=[""] + st.session_state["lista_unidades"], key="select_excluir_unidade")
            
            # Encapsulado para aplicação do CSS de exclusão em vermelho
            st.markdown('<div class="btn-excluir-container">', unsafe_allow_html=True)
            if st.button("Confirmar Exclusão", key="btn_confirmar_exc_unidade"):
                if unidade_excluir and unidade_excluir in st.session_state["lista_unidades"]:
                    st.session_state["lista_unidades"].remove(unidade_excluir)
                    st.success(f"Unidade '{unidade_excluir}' removida!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # FORMULÁRIO DE CADASTRO
    # --------------------------------------------------------------------------
    st.markdown("### ➕ Novo Cadastro de Serviço")
    
    with st.form("form_cadastro_servico", clear_on_submit=True):
        col1, col2, col3 = st.columns([1.5, 3.5, 2])
        
        with col1:
            codigo = st.text_input("Código do Serviço*", placeholder="Ex: 101")
        with col2:
            descricao = st.text_input("Descrição*", placeholder="Ex: Armazenagem Geral")
        with col3:
            tarifa = st.number_input("Tarifa (R$)*", min_value=0.0, step=0.01, format="%.5f")

        col4, col5, col6 = st.columns([2, 2, 3])
        
        with col4:
            unidade = st.selectbox("Unidade*", options=st.session_state["lista_unidades"])
        with col5:
            categoria = st.selectbox("Categoria*", options=st.session_state["lista_categorias"])
        with col6:
            observacoes = st.text_input("Observações", placeholder="Ex: Informações adicionais")

        st.markdown("<br>", unsafe_allow_html=True)
        btn_salvar = st.form_submit_button("💾 Cadastrar Serviço", use_container_width=True)

        if btn_salvar:
            if not codigo.strip() or not descricao.strip():
                st.error("Preencha os campos obrigatórios (*): Código e Descrição.")
            else:
                cod_final = normalizar_codigo_fn(codigo) if normalizar_codigo_fn else str(codigo.strip())
                df_atual = carregar_dados_fn()
                
                if not df_atual.empty and cod_final in df_atual["Código"].astype(str).values:
                    st.error(f"O código '{cod_final}' já está cadastrado no sistema.")
                else:
                    novo_registro = {
                        "Código": cod_final,
                        "Descrição": str(descricao.strip()),
                        "Tarifa (R$)": tarifa,
                        "Unidade": unidade,
                        "Categoria": categoria,
                        "Observações": observacoes.strip(),
                        "Ativo": True
                    }
                    salvar_dados_fn(novo_registro)
                    st.success(f"Serviço '{descricao}' cadastrado com sucesso!")
                    st.rerun()

    st.markdown("---")

    # --------------------------------------------------------------------------
    # TABELA DE EXIBIÇÃO
    # --------------------------------------------------------------------------
    st.markdown("### 📑 Serviços Cadastrados")
    df_exibicao = carregar_dados_fn()
    
    if not df_exibicao.empty:
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum serviço cadastrado até o momento.")
