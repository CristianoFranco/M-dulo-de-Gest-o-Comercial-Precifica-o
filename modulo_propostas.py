import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# FUNÇÕES AUXILIARES DA PROPOSTA
# ==============================================================================
def obter_proximo_numero_proposta():
    """Gera o número sequencial no formato MM/NNNNN/AAAA"""
    agora = datetime.now()
    mes = agora.strftime("%m")
    ano = agora.strftime("%Y")
    
    # Inicializa o sequencial na sessão caso não exista
    if "sequencial_proposta" not in st.session_state:
        st.session_state["sequencial_proposta"] = 1
        
    seq = st.session_state["sequencial_proposta"]
    return f"{mes}/{seq:05d}/{ano}"

def inicializar_estado_proposta():
    """Inicializa as listas de itens do rascunho para cada bloco"""
    if "itens_armazenagem" not in st.session_state:
        st.session_state["itens_armazenagem"] = []
    if "itens_seguro" not in st.session_state:
        st.session_state["itens_seguro"] = []
    if "itens_servicos" not in st.session_state:
        st.session_state["itens_servicos"] = []
    if "itens_outros" not in st.session_state:
        st.session_state["itens_outros"] = []

# ==============================================================================
# COMPONENTE DE BLOCO DA CATEGORIA
# ==============================================================================
def renderizar_bloco_categoria(titulo, chave_sessao, df_categoria, icone_bloco):
    st.markdown(f"#### {icone_bloco} {titulo}")
    
    if df_categoria.empty:
        st.info(f"Nenhum serviço cadastrado na categoria '{titulo}'.")
        return

    # Opções formatadas para o Selectbox
    opcoes = [""] + df_categoria["Código"].tolist()
    
    col_sel, col_qtd, col_btn = st.columns([4, 2, 2])
    
    with col_sel:
        item_selecionado = st.selectbox(
            f"Selecionar {titulo}:",
            options=opcoes,
            format_func=lambda x: "" if x == "" else f"{x} - {df_categoria[df_categoria['Código'] == x]['Descrição'].values[0]}",
            key=f"select_{chave_sessao}"
        )
        
    with col_qtd:
        quantidade = st.number_input(
            "Quantidade:",
            min_value=1.0,
            value=1.0,
            step=1.0,
            key=f"qtd_{chave_sessao}"
        )
        
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar", key=f"btn_add_{chave_sessao}"):
            if item_selecionado != "":
                row = df_categoria[df_categoria["Código"] == item_selecionado].iloc[0]
                tarifa_float = float(str(row["Tarifa (R$)"]).replace(",", "."))
                
                # Verifica se o item já está no rascunho
                ja_existe = any(i["Código"] == item_selecionado for i in st.session_state[chave_sessao])
                if not ja_existe:
                    st.session_state[chave_sessao].append({
                        "Código": row["Código"],
                        "Descrição": row["Descrição"],
                        "Unidade": row["Unidade"],
                        "Tarifa (R$)": tarifa_float,
                        "Quantidade": quantidade,
                        "Total (R$)": tarifa_float * quantidade
                    })
                    st.rerun()
                else:
                    st.warning("Este item já foi adicionado a este bloco.")
            else:
                st.warning("Selecione um item antes de adicionar.")

    # Exibição dos Itens Adicionados no Bloco
    if st.session_state[chave_sessao]:
        st.markdown("**Itens Adicionados:**")
        
        for idx, item in enumerate(st.session_state[chave_sessao]):
            c_del, c_cod, c_desc, c_un, c_tar, c_qtd, c_tot = st.columns([0.6, 1.5, 3.5, 1.5, 1.5, 1.5, 1.5])
            
            with c_del:
                if st.button("🗑️", key=f"del_{chave_sessao}_{idx}", help="Remover item"):
                    st.session_state[chave_sessao].pop(idx)
                    st.rerun()
                    
            with c_cod:
                st.write(f"**{item['Código']}**")
            with c_desc:
                st.write(item["Descrição"])
            with c_un:
                st.write(f"_{item['Unidade']}_")
            with c_tar:
                st.write(f"R$ {item['Tarifa (R$)']:.5f}".rstrip('0').rstrip('.'))
            with c_qtd:
                st.write(f"Qtd: {item['Quantidade']}")
            with c_tot:
                st.write(f"**R$ {(item['Tarifa (R$)'] * item['Quantidade']):.2f}**")
    st.markdown("---")

# ==============================================================================
# RENDERIZADOR PRINCIPAL DA ABA 2
# ==============================================================================
def renderizar_aba_propostas(carregar_dados_fn, salvar_dados_fn=None):
    inicializar_estado_proposta()
    numero_proposta = obter_proximo_numero_proposta()
    
    # Cabeçalho Principal
    col_tit, col_num = st.columns([3, 1])
    with col_tit:
        st.markdown("## 📝 Proposta Rascunho")
        st.caption("Monte a estrutura comercial selecionando os serviços por categoria.")
    with col_num:
        st.markdown(f"### Nº: `{numero_proposta}`")

    st.markdown("<br>", unsafe_allow_html=True)

    # Carrega a base de dados dos serviços ativos
    df_servicos = carregar_dados_fn(apenas_ativos=True)

    if df_servicos.empty:
        st.warning("Nenhum serviço ativo encontrado no cadastro. Por favor, adicione serviços na Aba 1 antes de criar propostas.")
        return

    # Normalização das Categorias da Planilha
    df_servicos["Categoria_Clean"] = df_servicos["Categoria"].astype(str).str.strip().str.upper()

    # Separação por Categoria
    df_armazenagem = df_servicos[df_servicos["Categoria_Clean"] == "ARMAZENAGEM"]
    df_seguro = df_servicos[df_servicos["Categoria_Clean"] == "SEGURO"]
    df_servicos_handling = df_servicos[df_servicos["Categoria_Clean"].isin(["SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]
    df_outros = df_servicos[~df_servicos["Categoria_Clean"].isin(["ARMAZENAGEM", "SEGURO", "SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]

    # --------------------------------------------------------------------------
    # BLOCO 1 - ARMAZENAGEM
    # --------------------------------------------------------------------------
    renderizar_bloco_categoria("Armazenagem", "itens_armazenagem", df_armazenagem, "🏬")

    # --------------------------------------------------------------------------
    # BLOCO 2 - SEGURO
    # --------------------------------------------------------------------------
    renderizar_bloco_categoria("Seguro", "itens_seguro", df_seguro, "🛡️")

    # --------------------------------------------------------------------------
    # BLOCO 3 - SERVIÇOS E MOVIMENTAÇÕES (HANDLING)
    # --------------------------------------------------------------------------
    renderizar_bloco_categoria("Serviços e Movimentações", "itens_servicos", df_servicos_handling, "⚙️")

    # --------------------------------------------------------------------------
    # BLOCO 4 - OUTROS
    # --------------------------------------------------------------------------
    renderizar_bloco_categoria("Outros", "itens_outros", df_outros, "📦")

    # --------------------------------------------------------------------------
    # RESUMO TOTAL & FECHAR RASCUNHO
    # --------------------------------------------------------------------------
    todos_itens = (
        st.session_state["itens_armazenagem"] + 
        st.session_state["itens_seguro"] + 
        st.session_state["itens_servicos"] + 
        st.session_state["itens_outros"]
    )
    
    valor_total_proposta = sum(item["Tarifa (R$)"] * item["Quantidade"] for item in todos_itens)

    col_res1, col_res2 = st.columns([2, 1])
    
    with col_res1:
        st.markdown(f"### Valor Total Estimado: **R$ {valor_total_proposta:,.2f}**")
        
    with col_res2:
        if st.button("🔒 Fechar Rascunho e Salvar Proposta", use_container_width=True):
            if not todos_itens:
                st.error("Não é possível fechar uma proposta vazia. Adicione pelo menos um item.")
            else:
                # Incrementa o número da proposta para a próxima
                st.session_state["sequencial_proposta"] += 1
                
                # Limpa os itens do rascunho
                st.session_state["itens_armazenagem"] = []
                st.session_state["itens_seguro"] = []
                st.session_state["itens_servicos"] = []
                st.session_state["itens_outros"] = []
                
                st.success(f"Proposta {numero_proposta} salva com sucesso como Rascunho!")
                st.balloons()
                st.rerun()
