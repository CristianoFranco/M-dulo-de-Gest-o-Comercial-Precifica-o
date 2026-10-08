import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================================================================
# FUNÇÕES AUXILIARES DA PROPOSTA
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
        if str(item.get("Código", "")) != str(codigo_para_remover)
    ]

def aplicar_reajuste_percentual_global(percentual):
    fator = 1.0 + (float(percentual) / 100.0)
    for idx in range(len(st.session_state["rascunho_itens"])):
        val_atual = float(st.session_state["rascunho_itens"][idx]["Tarifa (R$)"])
        st.session_state["rascunho_itens"][idx]["Tarifa (R$)"] = round(val_atual * fator, 5)

# ==============================================================================
# RENDERIZADOR DE BLOCO POR CATEGORIA
# ==============================================================================
def renderizar_bloco_categoria(titulo, categoria_filtro, df_categoria, icone_bloco):
    st.markdown(f"#### {icone_bloco} {titulo}")
    
    if df_categoria.empty:
        st.info(f"Nenhum serviço cadastrado na categoria '{titulo}'.")
        st.markdown("---")
        return

    codigos_categoria = df_categoria["Código"].tolist()
    opcoes = [""] + codigos_categoria
    
    col_sel, col_btn = st.columns([6, 2])
    
    with col_sel:
        item_selecionado = st.selectbox(
            f"Selecionar {titulo}:",
            options=opcoes,
            format_func=lambda x: "" if x == "" else f"{x} - {df_categoria[df_categoria['Código'] == x]['Descrição'].values[0]}",
            key=f"select_cat_{categoria_filtro}"
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
                
                obs_val = str(row["Observações"]) if "Observações" in row and pd.notna(row["Observações"]) else ""
                
                ja_existe = any(str(i.get("Código", "")) == str(item_selecionado) for i in st.session_state["rascunho_itens"])
                if not ja_existe:
                    st.session_state["rascunho_itens"].append({
                        "Código": str(row["Código"]),
                        "Descrição": str(row["Descrição"]),
                        "Tarifa (R$)": tarifa_float,
                        "Unidade": str(row["Unidade"]),
                        "Observações": obs_val,
                        "Categoria": titulo
                    })
                    st.rerun()
                else:
                    st.warning("Este item já foi adicionado ao rascunho.")
            else:
                st.warning("Selecione um item antes de adicionar.")

    itens_do_bloco = [i for i in st.session_state["rascunho_itens"] if i.get("Categoria") == titulo]
    
    if itens_do_bloco:
        st.markdown("<h5 style='color: #FFFFFF; font-weight: bold; margin-top: 15px;'>📋 Itens Inseridos:</h5>", unsafe_allow_html=True)
        
        h_del, h_cod, h_desc, h_tar, h_un, h_obs = st.columns([0.5, 1.2, 3.2, 2.2, 1.8, 2.2])
        with h_del: st.markdown("<b style='color: #FFFFFF;'>❌</b>", unsafe_allow_html=True)
        with h_cod: st.markdown("<b style='color: #FFFFFF;'>Código</b>", unsafe_allow_html=True)
        with h_desc: st.markdown("<b style='color: #FFFFFF;'>Descrição</b>", unsafe_allow_html=True)
        with h_tar: st.markdown("<b style='color: #FFFFFF;'>Tarifa Editável (R$)</b>", unsafe_allow_html=True)
        with h_un: st.markdown("<b style='color: #FFFFFF;'>Unidade</b>", unsafe_allow_html=True)
        with h_obs: st.markdown("<b style='color: #FFFFFF;'>Observações</b>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 4px 0 10px 0; border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

        for item in itens_do_bloco:
            c_del, c_cod, c_desc, c_tar, c_un, c_obs = st.columns([0.5, 1.2, 3.2, 2.2, 1.8, 2.2])
            
            with c_del:
                if st.button("❌", key=f"btn_x_{categoria_filtro}_{item['Código']}", help="Remover item"):
                    remover_item_proposta(item['Código'])
                    st.rerun()
                    
            with c_cod:
                st.markdown(f"<span style='color: #FFFFFF; font-weight: bold;'>{item['Código']}</span>", unsafe_allow_html=True)
            with c_desc:
                st.markdown(f"<span style='color: #FFFFFF;'>{item['Descrição']}</span>", unsafe_allow_html=True)
            with c_tar:
                nova_tarifa = st.number_input(
                    label=f"Tarifa_{item['Código']}",
                    label_visibility="collapsed",
                    value=float(item["Tarifa (R$)"]),
                    min_value=0.0,
                    step=0.01,
                    format="%.5f",
                    key=f"input_tarifa_{categoria_filtro}_{item['Código']}"
                )
                if nova_tarifa != item["Tarifa (R$)"]:
                    item["Tarifa (R$)"] = nova_tarifa
                    
            with c_un:
                st.markdown(f"<span style='color: #FFFFFF;'>{item['Unidade']}</span>", unsafe_allow_html=True)
            with c_obs:
                st.markdown(f"<span style='color: #FFFFFF;'>{item.get('Observações', '')}</span>", unsafe_allow_html=True)

    st.markdown("---")

# ==============================================================================
# RENDERIZADOR PRINCIPAL ABA 2
# ==============================================================================
def renderizar_aba_propostas(carregar_dados_fn, salvar_dados_fn=None):
    inicializar_estado_proposta()
    numero_proposta = obter_proximo_numero_proposta()
    
    col_tit, col_num = st.columns([3, 1])
    with col_tit:
        st.markdown("## 📝 Proposta Rascunho")
        st.caption("Monte a estrutura comercial selecionando os serviços e ajustando as tarifas.")
    with col_num:
        st.markdown(f"### Nº: `{numero_proposta}`")

    st.markdown("<br>", unsafe_allow_html=True)

    # Painel de Ajuste Percentual Global
    if st.session_state["rascunho_itens"]:
        with st.expander("📈 **Ajuste Percentual Geral nas Tarifas do Rascunho**", expanded=True):
            col_perc, col_apply, _ = st.columns([1.8, 2.2, 4])
            
            with col_perc:
                percentual_ajuste = st.number_input(
                    "Reajuste (%):",
                    value=0.0,
                    step=0.5,
                    format="%.2f",
                    key="input_reajuste_perc_global",
                    help="Exemplo: 5.0 para +5% de aumento ou -5.0 para 5% de desconto em todas as tarifas"
                )
            with col_apply:
                st.write("")
                st.write("")
                if st.button("⚡ Aplicar Reajuste", key="btn_aplicar_reajuste_global", type="primary", use_container_width=True):
                    if percentual_ajuste != 0.0:
                        aplicar_reajuste_percentual_global(percentual_ajuste)
                        st.success(f"Reajuste de {percentual_ajuste:.2f}% aplicado!")
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    df_servicos = carregar_dados_fn(apenas_ativos=True)

    if df_servicos.empty:
        st.warning("Nenhum serviço ativo encontrado no cadastro.")
        return

    df_servicos["Cat_Upper"] = df_servicos["Categoria"].astype(str).str.strip().str.upper()

    df_armazenagem = df_servicos[df_servicos["Cat_Upper"] == "ARMAZENAGEM"]
    df_seguro = df_servicos
