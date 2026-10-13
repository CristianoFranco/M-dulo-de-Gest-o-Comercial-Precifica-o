import streamlit as st
import pandas as pd
from datetime import datetime
import io
import html
import os

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY, TA_CENTER, TA_LEFT
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def desenhar_cabecalho_rodape(canvas, doc):
    canvas.saveState()
    
    # CABEÇALHO - Logo centralizada
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, x=236, y=730, width=140, height=45, preserveAspectRatio=True, mask='auto')
    
    # RODAPÉ - Endereço e Contato centralizados em todas as páginas
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(612 / 2.0, 35, "Avenida Vitoria Rossi Martini, 31")
    canvas.drawCentredString(612 / 2.0, 25, "Distrito Industrial Indaiatuba - SP - CEP: 13.347-613")
    canvas.drawCentredString(612 / 2.0, 15, "+55 19 3936-8520 / www.globexmultimodal.com.br")
    
    canvas.restoreState()

def gerar_pdf_proposta_completo(numero_proposta, cliente_nome, cnpj_val, contato_cliente, objeto_proposta, iss_val, prazo_val, vigencia_val, fat_minimo_val, itens_proposta):
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
    
    num_prop_esc = html.escape(str(numero_proposta))
    c_nome_esc = html.escape(str(cliente_nome))
    c_objeto_esc = html.escape(str(objeto_proposta))
    c_contato_esc = html.escape(str(contato_cliente))
    iss_esc = html.escape(str(iss_val))
    prazo_esc = html.escape(str(prazo_val))
    vigencia_esc = html.escape(str(vigencia_val))
    fat_minimo_esc = html.escape(str(fat_minimo_val)).strip()
    
    # ESTILOS DE PARÁGRAFO
    style_data_direita = ParagraphStyle(
        'DataDireita',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )

    style_proposta_direita = ParagraphStyle(
        'PropostaNumDireita',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        leading=15,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#0052B4'),
        spaceAfter=12
    )
    
    body_left_style = ParagraphStyle(
        'CorpoTextoEsquerda',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )

    body_justify_style = ParagraphStyle(
        'CorpoTextoJustificado',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#222222'),
        spaceAfter=8
    )

    titulo_bloco_style = ParagraphStyle(
        'TituloBlocoCategoria',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        textColor=colors.HexColor('#0052B4'),
        spaceBefore=10,
        spaceAfter=4
    )

    titulo_tabelas_style = ParagraphStyle(
        'TituloTabelasServicos',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        textColor=colors.HexColor('#0052B4'),
        spaceBefore=14,
        spaceAfter=8
    )

    titulo_termo_center = ParagraphStyle(
        'TituloTermoCentralizado',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0052B4'),
        spaceBefore=10,
        spaceAfter=12
    )

    premissas_style = ParagraphStyle(
        'PremissasStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#333333'),
        spaceBefore=10,
        spaceAfter=10
    )

    # ESTILOS DEDICADOS PARA O DESTAQUE DO FATURAMENTO MÍNIMO
    fat_min_title_style = ParagraphStyle(
        'FatMinTitle',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0052B4'),
        alignment=TA_LEFT
    )
    
    fat_min_text_style = ParagraphStyle(
        'FatMinText',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#222222'),
        alignment=TA_LEFT
    )

    # ESTILOS DEDICADOS PARA AS CÉLULAS DAS TABELAS
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_LEFT)
    th_style_right = ParagraphStyle('THRight', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_RIGHT)
    
    td_style_left = ParagraphStyle('TDLeft', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_LEFT)
    td_style_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_CENTER)
    td_style_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_RIGHT)

    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    agora = datetime.now()
    data_extenso = f"Indaiatuba - SP, {agora.day:02d} de {meses[agora.month - 1]} de {agora.year}."
    
    # ==========================================
    # PÁGINA 1: APENAS TEXTO INTRODUTÓRIO E CONTATOS
    # ==========================================
    story.append(Paragraph(data_extenso, style_data_direita))
    story.append(Paragraph(f"PROPOSTA Nº {num_prop_esc}", style_proposta_direita))
    
    story.append(Paragraph(f"À<br/><b>{c_nome_esc}</b>", body_left_style))
    story.append(Paragraph(f"<b>REF:</b> {c_objeto_esc}", body_left_style))
    story.append(Paragraph(f"<b>Contato:</b> {c_contato_esc}", body_left_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Prezados,", body_left_style))
    
    texto_intro = (
        f"Apresentamos a proposta comercial da Globex Multimodal para a gestão de armazenagem e movimentação de cargas da <b>{c_nome_esc}</b>. "
        "Sediada estrategicamente no polo logístico de Indaiatuba-SP, a Globex combina infraestrutura moderna, rigor técnico e agilidade operacional. "
        "Desenvolvemos operações sob medida para cadeias de suprimentos exigentes, assegurando controle de ponta a ponta, total conformidade regulatória e integridade máxima dos seus produtos."
    )
    story.append(Paragraph(texto_intro, body_justify_style))
    
    texto_intro2 = (
        f"Apresentamos a seguir nossa tabela de serviços e tarifas. Para facilitar a compreensão e o planejamento financeiro da <b>{c_nome_esc}</b>, "
        "na apresentação da proposta haverá uma simulação prática da aplicação dessas tarifas para o período informado, calculada com base no volume "
        "e nas premissas operacionais compartilhadas pela sua equipe. Trata-se de uma projeção ilustrativa desenhada para dar total visibilidade ao custo estimado da operação."
    )
    story.append(Paragraph(texto_intro2, body_justify_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Richarlles Nascimento</b> – Executivo de Contas &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 99959-9894", body_left_style))
    story.append(Paragraph("<b>Wilson Santos</b> – Gerente Comercial &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 99888-2855", body_left_style))
    
    story.append(PageBreak())

    # ==========================================
    # PÁGINA 2: TARIFÁRIO, FATURAMENTO MÍNIMO E PREMISSAS
    # ==========================================
    story.append(Paragraph("Tabela de Preços e Serviços", titulo_tabelas_style))
    story.append(Spacer(1, 4))

    blocos_dados = {
        "ARMAZENAGEM": [],
        "SEGURO": [],
        "SERVIÇOS": [],
        "MOVIMENTAÇÃO (HANDLING)": [],
        "TARIFÁRIO DE SERVIÇOS CONEXOS": []
    }

    for item in itens_proposta:
        cat_original = str(item.get("Categoria", "")).strip().lower()
        
        if "armazenagem" in cat_original:
            cat_chave = "ARMAZENAGEM"
        elif "seguro" in cat_original:
            cat_chave = "SEGURO"
        elif "movimentação" in cat_original or "handling" in cat_original or "movimentacao" in cat_original:
            cat_chave = "MOVIMENTAÇÃO (HANDLING)"
        elif "serviço" in cat_original or "servico" in cat_original:
            cat_chave = "SERVIÇOS"
        else:
            cat_chave = "TARIFÁRIO DE SERVIÇOS CONEXOS"
        
        tarifa_val = item.get("Tarifa (R$)", 0.0)
        try:
            tarifa_float = float(tarifa_val)
            tarifa_str = "R$ " + "{:,.5f}".format(tarifa_float).replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            tarifa_str = str(tarifa_val)

        p_cod = Paragraph(html.escape(str(item.get("Código", ""))), td_style_center)
        p_desc = Paragraph(html.escape(str(item.get("Descrição", ""))), td_style_left)
        p_und = Paragraph(html.escape(str(item.get("Unidade", ""))), td_style_left)
        p_tar = Paragraph(html.escape(tarifa_str), td_style_right)
        p_obs = Paragraph(html.escape(str(item.get("Observações", ""))), td_style_left)

        blocos_dados[cat_chave].append([p_cod, p_desc, p_und, p_tar, p_obs])

    primeiro_bloco = True
    for nome_bloco, linhas in blocos_dados.items():
        if linhas:
            if not primeiro_bloco:
                story.append(Spacer(1, 14))
            
            story.append(Paragraph(nome_bloco, titulo_bloco_style))
            story.append(Spacer(1, 4))
            
            cabecalho = [
                Paragraph("Código", th_style),
                Paragraph("Descrição", th_style),
                Paragraph("Unidade", th_style),
                Paragraph("Tarifa", th_style_right),
