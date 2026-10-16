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

    title_style = ParagraphStyle('TitleStyle
