import streamlit as st
import pandas as pd
import io
import os

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def desenhar_cabecalho_rodape_simulador(canvas, doc):
    canvas.saveState()
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(diretorio_atual, 'Logo.png')
    
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, x=236, y=730, width=140, height=45, preserveAspectRatio=True, mask='auto')

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(612 / 2.0, 35, "Avenida Vitoria Rossi Martini, 31")
    canvas.drawCentredString(612 / 2.0, 25, "Distrito Industrial Indaiatuba - SP - CEP: 13.347-613")
    canvas.drawCentredString(612 / 2.0, 15, "+55 19 3936-8520 / www.globexmultimodal.com.br")
    canvas.restoreState()

def gerar_pdf_simulador(numero_prop, cliente_nome, df_simulacao_completo, valor_total_geral):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=90,
        bottomMargin=55
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0052B4'), spaceAfter=15)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#222222'), spaceAfter=10)
    
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_LEFT)
    th_style_right = ParagraphStyle('THRight', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_RIGHT)
    td_style_left = ParagraphStyle('TDLeft', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_LEFT)
    td_style_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_CENTER)
    td_style_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_RIGHT)
    total_style = ParagraphStyle('TotalStyle', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#0052B4'), alignment=TA_RIGHT)

    story.append(Paragraph(f"SIMULAÇÃO COMERCIAL - PROPOSTA Nº {numero_prop}", title_style))
    story.append(Paragraph(f"<b>Cliente / Contratante:</b> {cliente_nome}", sub_style))
    story.append(Spacer(1, 10))

    cabecalho = [
        Paragraph("Código", th_style),
        Paragraph("Descrição", th_style),
        Paragraph("Categoria", th_style),
        Paragraph("Unidade", th_style),
        Paragraph("Tarifa (R$)", th_style_right),
        Paragraph("Qtd.", th_style_right),
        Paragraph("Total (R$)", th_style_right)
    ]

    linhas_tabela = [cabecalho]
    for _, row in df_simulacao_completo.iterrows():
        t_val = float(row.get("Tarifa Simulação", 0.0))
        q_val = float(row.get("Quantidade", 0.0))
        tot_val = float(row.get("Valor Total", 0.0))

        linhas_tabela.append([
            Paragraph(str(row.get("Código", "")), td_style_center),
            Paragraph(str(row.get("Descrição", "")), td_style_left),
            Paragraph(str(row.get("Categoria", "")), td_style_left),
            Paragraph(str(row.get("Unidade", "")), td_style_left),
            Paragraph(f"R$ {t_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), td_style_right),
            Paragraph(f"{q_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), td_style_right),
            Paragraph(f"R$ {tot_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), td_style_right)
        ])

    tabela = Table(linhas_tabela, colWidths=[45, 140, 100, 75, 60, 50, 70])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052B4')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>VALOR TOTAL DA SIMULAÇÃO: R$ {valor_total_geral:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), total_style))

    try:
        doc.build(story, onFirstPage=desenhar_cabecalho_rodape_simulador, onLaterPages=desenhar_cabecalho_rodape_simulador)
    except Exception as e:
        st.error(f"Erro ao gerar PDF do simulador: {e}")
        return None

    buffer.seek(0)
    return buffer

def ordenar_categorias(cat):
    c_lower = str(cat).strip().lower()
    if "armazenagem" in c_lower:
        return 1
    elif "seguro" in c_lower:
        return 2
    else:
        return 3

def filtrar_categoria_permitida(cat_str):
    c_lower = str(cat_str).strip().lower()
    if "conexos" in c_lower or "serviços conexos" in c_lower:
        return False
    if "armazenagem" in c_lower or "seguro" in c_lower or "serviço" in c_lower or "movimentação" in c_lower or "handling" in c_lower or "serviços e movimentações" in c_lower:
        return True
    return False

def renderizar_aba_simulacao(carregar_dados_fn, carregar_propostas_salvas_fn):
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
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 15px !important;
            }
            div.stDownloadButton > button:hover {
                background-color: #003380 !important;
                border-color: #002255 !important;
                color: #FFFFFF !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color: #FFFFFF;'>📊 Simulador Comercial & Cenários</h2>", unsafe_allow_html=True)
    st.markdown("<span style='color: #FFFFFF; opacity: 0.85;'>Simule volumes, ajuste tarifas pontualmente ou em massa, visualize gráficos de categoria e exporte relatórios.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        df_historico = carregar_propostas_salvas_fn()
    except Exception:
        df_historico = pd.DataFrame()

    if df_historico.empty or "Proposta" not in df_historico.columns:
        st.info("Nenhuma proposta salva encontrada para iniciar a simulação.")
        return

    mapa_propostas = {}
    for _, row in df_historico.iterrows():
        p = str(row.get("Proposta", "")).strip()
        c = str(row.get("Cliente", "")).strip()
        if p and p != "nan":
            mapa_propostas[p] = c

    propostas_disponiveis = sorted(list(mapa_propostas.keys()))
    
    col_sel_p, _ = st.columns([2, 2])
    with col_sel_p:
        st.markdown("<h3 style='color: #FFFFFF; font-size: 18px;'>Selecione a Proposta e Cliente</h3>", unsafe_allow_html=True)
        opcao_selecionada = st.selectbox(
            "Selecione a Proposta e Cliente",
            options=[""] + propostas_disponiveis,
            format_func=lambda x: f"{x} — {mapa_propostas.get(x, '')}" if x else "Selecione uma proposta...",
            label_visibility="collapsed",
            key="select_prop_simulador"
        )

    if not opcao_selecionada:
        st.warning("Selecione uma proposta acima para carregar os itens no simulador.")
        return

    proposta_selecionada = opcao_selecionada
    df_prop = df_historico[df_historico["Proposta"].astype(str).str.strip() == proposta_selecionada].copy()
    cliente_atual = str(df_prop["Cliente"].iloc[0]) if "Cliente" in df_prop.columns and not df_prop.empty else "Cliente"

    chave_estado_itens = f
