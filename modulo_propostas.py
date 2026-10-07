import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# ESTADO DA PROPOSTA
# ==============================================================================
def obter_proximo_numero_proposta():
    agora = datetime.now()
    mes = agora.strftime("%m")
    ano = agora.strftime("%Y")
    
    if "sequencial_proposta" not in st.session_state:
        st.session_state["sequencial_proposta"] = 1
        
    seq = st.session_state["sequencial_proposta"]
    return f"{mes}/{seq:05d}/{ano}"

def inicializar_estado_proposta():
    if "rascunho_itens" not in st.session_state:
        st.session_state["rascunho_itens"] = []

def remover_item_proposta(codigo_para_remover):
    st.session_state["rascunho_itens"] = [
        item for item in st.session_state["rascunho_itens"] 
        if item["Código"] != codigo_para_remover
    ]

# ==============================================================================
# RENDERIZADOR DE BLOCO
# ==============================================================================
def renderizar_bloco_categoria(titulo, categoria_filtro, df_categoria, icone_bloco):
    st.markdown(f"#### {icone_bloco} {titulo}")
    
    # Card com Fundo Claro para garantir legibilidade
    with st.container():
        st.markdown("""
            <div style="background-color: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        """, unsafe_allow_html=True)
        
        if df_categoria.empty:
            st.info(f"Nenhum serviço cadastrado na categoria '{titulo}'.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # Premissa 01: Apenas itens da respectiva categoria
        codigos_categoria = df_categoria["Código"].tolist()
        opcoes = [""] + codigos_categoria
        
        col_sel, col_qtd, col_btn = st.columns([4, 2, 2])
        
        with col_sel:
            item_selecionado = st.selectbox(
                f"Selecionar {titulo}:",
                options=opcoes,
                format_func=lambda x: "" if x == "" else f"{x} - {df_categoria[df_categoria['Código'] == x]['Descrição'].values[0]}",
                key=f"select_cat_{categoria_filtro}"
            )
            
        with col_qtd:
            quantidade = st.number_input(
                "Quantidade:",
                min_value=1.0,
                value=1.0,
                step=1.0,
                key=f"qtd_cat_{categoria_filtro}"
            )
            
        with col_btn:
            st.write("")
            st.write("")
            if st.button("➕ Adicionar", key=f"btn_add_{categoria_filtro}"):
                if item_selecionado != "":
                    row = df_categoria[df_categoria["Código"] == item_selecionado].iloc[0]
                    tarifa_raw = str(row["Tarifa (R$)"]).replace(".", "").replace(",", ".")
                    try:
                        tarifa_float = float(tarifa_raw)
                    except ValueError:
                        tarifa_float = float(row["Tarifa (R$)"])
                    
                    # Evita duplicidade no rascunho
                    ja_existe = any(i["Código"] == item_selecionado for i in st.session_state["rascunho_itens"])
                    if not ja_existe:
                        st.session_state["rascunho_itens"].append({
                            "Código": str(row["Código"]),
                            "Descrição": str(row["Descrição"]),
                            "Unidade": str(row["Unidade"]),
                            "Tarifa (R$)": tarifa_float,
                            "Quantidade": quantidade,
                            "Total (R$)": tarifa_float * quantidade,
                            "Categoria": titulo
                        })
                        st.rerun()
                    else:
                        st.warning("Este item já foi adicionado ao rascunho.")
                else:
                    st.warning("Selecione um item antes de adicionar.")

        # Premissas 02, 03 e 04: Exibição dos itens abaixo com a lixeira
        itens_do_bloco = [i for i in st.session_state["rascunho_itens"] if i["Categoria"] == titulo]
        
        if itens_do_bloco:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: #0A2540;'>📋 Itens Inseridos:</h5>", unsafe_allow_html=True)
            
            for item in itens_do_bloco:
                c_del, c_cod, c_desc, c_un, c_tar, c_qtd, c_tot = st.columns([0.8, 1.5, 3.5, 1.5, 1.5, 1.5, 1.5])
                
                with c_del:
                    if st.button("🗑️", key=f"del_{item['Código']}", help="Remover item"):
                        remover_item_proposta(item['Código'])
                        st.rerun()
                        
                with c_cod:
                    st.markdown(f"<span style='color: #0A2540; font-weight: bold;'>{item['Código']}</span>", unsafe_allow_html=True)
                with c_desc:
                    st.markdown(f"<span style='color: #0A2540;'>{item['Descrição']}</span>", unsafe_allow_html=True)
                with c_un:
                    st.markdown(f"<span style='color: #0A2540;'>{item['Unidade']}</span>", unsafe_allow_html=True)
                with c_tar:
                    st.markdown(f"<span style='color: #0A2540;'>R$ {item['Tarifa (R$)']:.5f}".rstrip('0').rstrip('.') + "</span>", unsafe_allow_html=True)
                with c_qtd:
                    st.markdown(f"<span style='color: #0A2540;'>{item['Quantidade']}</span>", unsafe_allow_html=True)
                with c_tot:
                    st.markdown(f"<span style='color: #0052B4; font-weight: bold;'>R$ {item['Total (R$)']:,.2f}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# RENDERIZADOR PRINCIPAL ABA 2
# ==============================================================================
def renderizar_aba_propostas(carregar_dados_fn, salvar_dados_fn=None):
    inicializar_estado_proposta()
    numero_proposta = obter_proximo_numero_proposta()
    
    col_tit, col_num = st.columns([3, 1])
    with col_tit:
        st.markdown("## 📝 Proposta Rascunho")
        st.caption("Monte a estrutura comercial selecionando os serviços por categoria.")
    with col_num:
        st.markdown(f"### Nº: `{numero_proposta}`")

    st.markdown("<br>", unsafe_allow_html=True)

    df_servicos = carregar_dados_fn(apenas_ativos=True)

    if df_servicos.empty:
        st.warning("Nenhum serviço ativo encontrado no cadastro.")
        return

    # Trata variações de digitação na Categoria
    df_servicos["Cat_Upper"] = df_servicos["Categoria"].astype(str).str.strip().str.upper()

    df_armazenagem = df_servicos[df_servicos["Cat_Upper"] == "ARMAZENAGEM"]
    df_seguro = df_servicos[df_servicos["Cat_Upper"] == "SEGURO"]
    df_servicos_handling = df_servicos[df_servicos["Cat_Upper"].isin(["SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]
    df_outros = df_servicos[~df_servicos["Cat_Upper"].isin(["ARMAZENAGEM", "SEGURO", "SERVIÇO", "MOVIMENTAÇÃO (HANDLING)"])]

    # 4 Blocos
    renderizar_bloco_categoria("Armazenagem", "ARM", df_armazenagem, "🏬")
    renderizar_bloco_categoria("Seguro", "SEG", df_seguro, "🛡️")
    renderizar_bloco_categoria("Serviços e Movimentações", "SER", df_servicos_handling, "⚙️")
    renderizar_bloco_categoria("Outros", "OUT", df_outros, "📦")

    # Resumo Geral e Total da Proposta
    todos_itens = st.session_state["rascunho_itens"]
    valor_total_proposta = sum(item["Total (R$)"] for item in todos_itens)

    col_res1, col_res2 = st.columns([2, 1])
    with col_res1:
        st.markdown(f"### Valor Total Estimado: **R$ {valor_total_proposta:,.2f}**")
        
    with col_res2:
        if st.button("🔒 Fechar Rascunho e Salvar Proposta", use_container_width=True):
            if not todos_itens:
                st.error("Adicione pelo menos um item antes de fechar a proposta.")
            else:
                st.session_state["sequencial_proposta"] += 1
                st.session_state["rascunho_itens"] = []
                st.success(f"Proposta {numero_proposta} gravada em rascunho com sucesso!")
                st.balloons()
                st.rerun()
