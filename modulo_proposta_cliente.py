import streamlit as st
import pandas as pd
from datetime import datetime
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def gerar_pdf_proposta(numero_proposta, cliente_nome, cnpj_val, itens_proposta):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

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

    cnpj_texto = ""
    if cnpj_val:
        cnpj_texto = " | <b>CNPJ:</b> " + str(cnpj_val)
    
    cliente_str = str(cliente_nome) if cliente_nome else "Não Informado"
    data_str = datetime.now().strftime("%d/%m/%Y")
    
    tit_text = "PROPOSTA COMERCIAL — Nº " + str(numero_proposta)
    sub_text = "<b>Cliente:</b> " + cliente_str + cnpj_texto + " | <b>Data:</b> " + data_str
    
    story.append(Paragraph(tit_text, titulo_style))
    story.append(Paragraph(sub_text, subtitulo_style))
    story.append(Spacer(1, 12))

    dados_tabela = [["Código", "Descrição", "Categoria", "Unidade", "Tarifa (R$)"]]
    
    for item in itens_proposta:
        tarifa_val = item.get("Tarifa (R$)", 0.0)
        try:
            tarifa_float = float(tarifa_val)
            tarifa_str = "R$ " + f"{tarifa_float:,.5f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            tarifa_str = str(tarifa_val)
        
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

def renderizar_aba_proposta_cliente(salvar_proposta_sheets_fn=None, carregar_propostas_salvas_fn=None):
    st.markdown("## 📄 Visão Final da Proposta (Cliente)")
    st.caption("Visualização não editável pronta para conferência, geração de PDF e salvamento.")
    st.markdown("<br>", unsafe_allow_html=True)

    itens_rascunho = st.session_state.get("rascunho_itens", [])
    
    # =========================================================================
    # MEMÓRIA SEGURA CONTRA O "WIDGET CLEANUP" DO STREAMLIT
    # =========================================================================
    if "proposta_cliente_nome" in st.session_state:
        st.session_state["_safe_cliente_nome"] = st.session_state["proposta_cliente_nome"]
    if "proposta_cliente_cnpj" in st.session_state:
        st.session_state["_safe_cnpj_val"] = st.session_state["proposta_cliente_cnpj"]

    cliente_nome = str(st.session_state.get("_safe_cliente_nome", "")).strip()
    cnpj_val = str(st.session_state.get("_safe_cnpj_val", "")).strip()
    
    agora = datetime.now()
    mes_str = agora.strftime("%m")
    ano_str = agora.strftime("%Y")
    
    if st.session_state.get("proposta_id_em_edicao"):
        numero_proposta_atual = str(st.session_state["proposta_id_em_edicao"])
    else:
        seq = st.session_state.get("sequencial_proposta", 1)
        numero_proposta_atual = mes_str + "/" + f"{seq:05d}" + "/" + ano_str

    st.markdown("### 📋 Documento da Proposta")

    if not itens_rascunho:
        st.warning("⚠️ Nenhum item pendente no rascunho. Monte os itens na **Tela 2 (Propostas e Precificação)** ou escolha uma proposta na consulta abaixo.")
    else:
        col_info1, col_info2, col_info3 = st.columns([2.5, 1.5, 1.5])
        with col_info1:
            lbl_cli = cliente_nome if cliente_nome else "Não Informado"
            st.markdown("**Cliente / Razão Social:**\n#### " + lbl_cli)
        with col_info2:
            lbl_cnpj = cnpj_val if cnpj_val else "Não Informado"
            st.markdown("**CNPJ:**\n#### " + lbl_cnpj)
        with col_info3:
            st.markdown("**Número da Proposta:**\n### `" + numero_proposta_atual + "`")

        st.markdown("<br>", unsafe_allow_html=True)

        dados_estaticos = []
        for item in itens_rascunho:
            tarifa_val = item.get("Tarifa (R$)", 0.0)
            try:
                tarifa_float = float(tarifa_val)
                tarifa_fmt = "R$ " + f"{tarifa_float:,.5f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                tarifa_fmt = str(tarifa_val)
            
            dados_estaticos.append({
                "Proposta": numero_proposta_atual,
                "Cliente": cliente_nome,
                "CNPJ": cnpj_val,
                "Código": item.get("Código", ""),
                "Descrição": item.get("Descrição", ""),
                "Categoria": item.get("Categoria", ""),
                "Unidade": item.get("Unidade", ""),
                "Tarifa": tarifa_fmt,
                "Observações": item.get("Observações", "")
            })

        df_estatico = pd.DataFrame(dados_estaticos)
        
        st.dataframe(
            df_estatico,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_pdf, col_fechar = st.columns(2)

        with col_pdf:
            if REPORTLAB_DISPONIVEL:
                pdf_bytes = gerar_pdf_proposta(numero_proposta_atual, cliente_nome, cnpj_val, itens_rascunho)
                nome_arquivo_pdf = "Proposta_" + numero_proposta_atual.replace("/", "_") + ".pdf"
                st.download_button(
                    label="📥 Exportar Proposta em PDF",
                    data=pdf_bytes,
                    file_name=nome_arquivo_pdf,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("Para habilitar o PDF, instale `reportlab` no ambiente.")

        with col_fechar:
            if st.button("🔒 Salvar Proposta no Google Sheets", type="primary", use_container_width=True):
                if salvar_proposta_sheets_fn:
                    linhas_para_salvar = []
                    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%
