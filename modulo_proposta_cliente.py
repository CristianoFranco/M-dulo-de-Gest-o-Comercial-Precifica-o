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
    
    # Caminho absoluto seguro para localizar o Logo.png na raiz do projeto
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(diretorio_atual, 'Logo.png')
    
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, x=236, y=730, width=140, height=45, preserveAspectRatio=True, mask='auto')
    else:
        print(f"⚠️ Atenção: Logótipo não encontrado em: {logo_path}")

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(612 / 2.0, 35, "Avenida Vitoria Rossi Martini, 31")
    canvas.drawCentredString(612 / 2.0, 25, "Distrito Industrial Indaiatuba - SP - CEP: 13.347-613")
    canvas.drawCentredString(612 / 2.0, 15, "+55 19 3936-8520 / www.globexmultimodal.com.br")
    canvas.restoreState()

def gerar_pdf_proposta_completo(numero_proposta, cliente_nome, cnpj_val, contato_cliente, objeto_proposta, iss_val, prazo_val, vigencia_val, fat_minimo_val, outras_premissas_val, itens_proposta):
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
    outras_premissas_esc = html.escape(str(outras_premissas_val)).strip()
    
    style_data_direita = ParagraphStyle('DataDireita', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_RIGHT, textColor=colors.HexColor('#222222'), spaceAfter=6)
    style_proposta_direita = ParagraphStyle('PropostaNumDireita', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', leading=15, alignment=TA_RIGHT, textColor=colors.HexColor('#0052B4'), spaceAfter=12)
    body_left_style = ParagraphStyle('CorpoTextoEsquerda', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_LEFT, textColor=colors.HexColor('#222222'), spaceAfter=6)
    body_justify_style = ParagraphStyle('CorpoTextoJustificado', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY, textColor=colors.HexColor('#222222'), spaceAfter=8)
    titulo_bloco_style = ParagraphStyle('TituloBlocoCategoria', parent=styles['Heading2'], fontSize=11, leading=15, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#0052B4'), spaceBefore=10, spaceAfter=4)
    titulo_tabelas_style = ParagraphStyle('TituloTabelasServicos', parent=styles['Heading2'], fontSize=13, leading=17, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#0052B4'), spaceBefore=14, spaceAfter=8)
    titulo_termo_center = ParagraphStyle('TituloTermoCentralizado', parent=styles['Heading2'], fontSize=12, leading=16, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0052B4'), spaceBefore=10, spaceAfter=12)
    premissas_style = ParagraphStyle('PremissasStyle', parent=styles['Normal'], fontSize=8, leading=11, alignment=TA_JUSTIFY, textColor=colors.HexColor('#333333'), spaceBefore=10, spaceAfter=10)

    fat_min_title_style = ParagraphStyle('FatMinTitle', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0052B4'), alignment=TA_LEFT)
    fat_min_text_style = ParagraphStyle('FatMinText', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#222222'), alignment=TA_LEFT)

    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_LEFT)
    th_style_right = ParagraphStyle('THRight', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=TA_RIGHT)
    td_style_left = ParagraphStyle('TDLeft', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_LEFT)
    td_style_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_CENTER)
    td_style_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.
