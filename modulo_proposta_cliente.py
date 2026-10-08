import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Importação da biblioteca para geração de PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False


# ==============================================================================
# FUNÇÃO PARA GERAR O ARQUIVO PDF EM MEMÓRIA
# ==============================================================================
def gerar_pdf_proposta(numero_proposta, cliente_nome, itens_proposta):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Estilos
    titulo_style = ParagraphStyle(
        'TituloProposta',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0052B4'),
        spaceAfter=12
    )
    subtitulo_style = ParagraphStyle(
        'SubTituloProposta',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=18
    )

    story.append(Paragraph(f"PROPOSTA COMERCIAL — Nº {numero_proposta}", titulo_style))
    story.append(Paragraph(f"<b>Cliente:</b> {cliente_nome if cliente_nome else 'Não Informado'} | <b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}", subtitulo_style))
    story.append(Spacer(1, 12))

    # Tabela de Itens
    dados_tabela = [["Código", "Descrição", "Categoria", "Unidade", "Tarifa (R$)"]]
    
    for item in itens_proposta:
        tarifa_val = item.get("Tarifa (R$)", 0.0)
        tarifa_str = f"R$ {float(tarifa_val):,.5f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        dados_tabela.append([
            str(item.get("Código", "")),
            str(item.get("Descrição", "")),
            str(item.get("Categoria", "")),
            str(item.get("Unidade", "")),
            tarifa_str
        ])

    tabela = Table(dados_tabela, colWidths=[70, 220, 100, 70, 80])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052B4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(tabela)
    doc.build(story)
    buffer.seek(0)
    return buffer


# ==============================================================================
# RENDERIZADOR PRINCIPAL TELA 3 - PROPOSTA DO CLIENTE
# ==============================================================================
def renderizar_aba_proposta_cliente(salvar_proposta_sheets_fn=None, carregar_propostas_salvas_fn=None):
    st.markdown("## 📄 Visão Final da Proposta (Cliente)")
    st.caption("Visualização não editável pronta para conferência, geração de PDF e salvamento.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Recupera o número da proposta e itens do rascunho
    itens_rascunho = st.session_state.get("rascunho_itens", [])
    
    agora = datetime.now()
    mes_str = agora.strftime("%m")
    ano_str = agora.strftime("%Y")
    seq = st.session_state.get("sequencial_proposta", 1)
    numero_proposta_atual = f"{mes_str}/{seq:05d}/{ano_str}"

    # --------------------------------------------------------------------------
    # 1. PAINEL DE VISUALIZAÇÃO DA PROPOSTA (NÃO EDITÁVEL)
    # --------------------------------------------------------------------------
    st.markdown("### 📋 Documento da Proposta")

    if not itens_rascunho:
        st.warning("⚠️ Nenhum item no rascunho da proposta. Adicione itens na **Tela 2 (Propostas e Precificação)** primeiro.")
    else:
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            nome_cliente = st.text_input("Nome do Cliente / Razão Social:", placeholder="Ex: Empresa ABC Ltda", key="input_nome_cliente_p3")
        with col_c2:
            st.markdown(f"**Número da Proposta:**\n### `{numero_proposta_atual}`")

        st.markdown("<br>", unsafe_allow_html=True)

        # Monta DataFrame estático (Não Editável)
        dados_estaticos = []
        for item in itens_rascunho:
            tarifa_val = item.get("Tarifa (R$)", 0.0)
            tarifa_fmt = f"R$ {float(tarifa_val):,.5f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            dados_estaticos.append({
                "Proposta": numero_proposta_atual,
                "Código": item.get("Código", ""),
                "Descrição": item.get("Descrição", ""),
                "Categoria": item.get("Categoria", ""),
                "Unidade": item.get("Unidade", ""),
                "Tarifa": tarifa_fmt,
                "Observações": item.get("Observações", "")
            })

        df_estatico = pd.DataFrame(dados_estaticos)
        
        # Exibe a tabela não editável
        st.dataframe(
            df_estatico,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 2. AÇÕES: GERAR PDF E FECHAR PROPOSTA (GRAVAR NO GOOGLE SHEETS)
        # ----------------------------------------------------------------------
        col_pdf, col_fechar = st.columns(2)

        with col_pdf:
            if REPORTLAB_DISPONIVEL:
                pdf_bytes = gerar_pdf_proposta(numero_proposta_atual, nome_cliente, itens_rascunho)
                st.download_button(
                    label="📥 Exportar Proposta em PDF",
                    data=pdf_bytes,
                    file_name=f"Proposta_{numero_proposta_atual.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("Para habilitar o download de PDF, instale a biblioteca `reportlab` (`pip install reportlab`).")

        with col_fechar:
            if st.button("🔒 Fechar Proposta e Salvar no Google Sheets", use_container_width=True):
                if salvar_proposta_sheets_fn:
                    # Prepara as linhas para inserção na planilha Google Sheets
                    linhas_para_salvar = []
                    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    for item in itens_rascunho:
                        linhas_para_salvar.append({
                            "Proposta": numero_proposta_atual,
                            "Data": data_hoje,
                            "Cliente": nome_cliente if nome_cliente else "Não Informado",
                            "Código": str(item.get("Código", "")),
                            "Descrição": str(item.get("Descrição", "")),
                            "Categoria": str(item.get("Categoria", "")),
                            "Unidade": str(item.get("Unidade", "")),
                            "Tarifa (R$)": float(item.get("Tarifa (R$)", 0.0)),
                            "Observações": str(item.get("Observações", ""))
                        })

                    sucesso = salvar_proposta_sheets_fn(linhas_para_salvar)

                    if sucesso:
                        st.session_state["sequencial_proposta"] = seq + 1
                        st.session_state["rascunho_itens"] = []
                        st.success(f"Proposta `{numero_proposta_atual}` fechada e gravada com sucesso na planilha!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Erro ao salvar os dados no Google Sheets.")
                else:
                    st.success(f"Proposta `{numero_proposta_atual}` finalizada!")
                    st.session_state["sequencial_proposta"] = seq + 1
                    st.session_state["rascunho_itens"] = []
                    st.rerun()

    st.markdown("---")

    # --------------------------------------------------------------------------
    # 3. PAINEL DE CONSULTA DE PROPOSTAS GRAVADAS
    # --------------------------------------------------------------------------
    st.markdown("### 🔍 Consulta de Propostas Gravadas")

    with st.expander("🔎 Filtrar e Consultar Histórico de Propostas", expanded=True):
        col_filtro_m, col_filtro_a = st.columns(2)

        with col_filtro_m:
            mes_consulta = st.selectbox(
                "Filtrar por Mês:",
                options=["Todos", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                index=0
            )
            
        with col_filtro_a:
            ano_consulta = st.text_input("Filtrar por Ano (Ex: 2026):", value="")

        if carregar_propostas_salvas_fn:
            df_historico = carregar_propostas_salvas_fn()

            if isinstance(df_historico, pd.DataFrame) and not df_historico.empty:
                df_filtrado = df_historico.copy()

                # Aplicação do filtro de Mês e Ano pela máscara MM/SEQUENCIAL/AAAA
                if "Proposta" in df_filtrado.columns:
                    if mes_consulta != "Todos":
                        df_filtrado = df_filtrado[df_filtrado["Proposta"].astype(str).str.startswith(mes_consulta + "/")]

                    if ano_consulta.strip():
                        df_filtrado = df_filtrado[df_filtrado["Proposta"].astype(str).str.endswith("/" + ano_consulta.strip())]

                st.markdown(f"**Registros Encontrados: `{len(df_filtrado)}`**")
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma proposta salva foi encontrada na base do Google Sheets.")
        else:
            st.info("A função de leitura de propostas do Google Sheets não foi vinculada.")
