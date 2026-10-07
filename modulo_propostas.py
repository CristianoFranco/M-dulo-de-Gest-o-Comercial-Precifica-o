import streamlit as st
import pandas as pd

def renderizar_aba_propostas(carregar_dados_fn):
    st.markdown("### 🛠️ Propostas Comercial & Precificação")
    
    # Exemplo: Carregar os serviços cadastrados ativos para usar nas simulações
    df_servicos = carregar_dados_fn(apenas_ativos=True)
    
    if df_servicos.empty:
        st.warning("Nenhum serviço ativo encontrado. Cadastre serviços na Aba 1 antes de criar propostas.")
        return

    # Exemplo de Interface da Aba 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Dados do Cliente / Proposta")
        cliente = st.text_input("Nome do Cliente / Empresa", placeholder="Ex: Cliente XYZ")
        validade = st.date_input("Validade da Proposta")
        
    with col2:
        st.markdown("#### 📦 Seleção de Serviços")
        servico_selecionado = st.selectbox(
            "Selecione o Serviço:", 
            options=df_servicos["Código"].tolist(),
            format_func=lambda x: f"{x} - {df_servicos[df_servicos['Código']==x]['Descrição'].values[0]}"
        )
        
        quantidade = st.number_input("Quantidade Estimada", min_value=1, value=100)

    st.markdown("---")
    st.info("Aqui pode adicionar a lógica de cálculo, margem de lucro e geração de PDFs de propostas comercial.")
