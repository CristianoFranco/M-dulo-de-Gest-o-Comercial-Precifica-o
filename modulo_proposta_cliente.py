import streamlit as st
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 40, 35, page_text)
        self.restoreState()

def desenhar_cabecalho_rodape(canvas, doc):
    canvas.saveState()
    
    # Caminho absoluto seguro para encontrar o Logo.png na mesma pasta do script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(diretorio_atual, 'Logo.png')
    
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, x=236, y=730, width=140, height=45, preserveAspectRatio=True, mask='auto')
    else:
        print(f"⚠️ Atenção: Logo não encontrado em {logo_path}")

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(612 / 2.0, 35, "Avenida Vitoria Rossi Martini, 31")
    canvas.drawCentredString(612 / 2.0, 25, "Distrito Industrial Indaiatuba - SP - CEP: 13.347-613")
    canvas.drawCentredString(612 / 2.0, 15, "+55 19 3936-8520 / www.globexmultimodal.com.br")
    canvas.restoreState()

def gerar_pdf_proposta(cliente, cnpj, itens, numero_proposta):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=95,
        bottomMargin=55
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    estilo_titulo = ParagraphStyle(
        'TituloProposta',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=15
    )
    
    estilo_normal = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333')
    )
    
    estilo_cabecalho_tabela = ParagraphStyle(
        'CabecalhoTabela',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=1
    )

    story = []
    
    # Informações da Proposta
    story.append(Paragraph(f"<b>PROPOSTA COMERCIAL Nº:</b> {numero_proposta}", estilo_titulo))
    story.append(Spacer(1, 10))
    
    dados_cliente = [
        [Paragraph(f"<b>Cliente:</b> {cliente}", estilo_normal), Paragraph(f"<b>CNPJ:</b> {cnpj}", estilo_normal)]
    ]
    tabela_cliente = Table(dados_cliente, colWidths=[300, 232])
    tabela_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tabela_cliente)
    story.append(Spacer(1, 20))
    
    # Tabela de Itens
    tabela_dados = [[
        Paragraph("<b>Código</b>", estilo_cabecalho_tabela),
        Paragraph("<b>Descrição dos Serviços</b>", estilo_cabecalho_tabela),
        Paragraph("<b>Unidade</b>", estilo_cabecalho_tabela),
        Paragraph("<b>Tarifa (R$)</b>", estilo_cabecalho_tabela)
    ]]
    
    for item in itens:
        tarifa_formatada = f"R$ {float(item.get('Tarifa (R$)', 0)):,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tabela_dados.append([
            Paragraph(str(item.get("Código", "")), estilo_normal),
            Paragraph(str(item.get("Descrição", "")), estilo_normal),
            Paragraph(str(item.get("Unidade", "")), estilo_normal),
            Paragraph(tarifa_formatada, estilo_normal)
        ])
        
    tabela_itens = Table(tabela_dados, colWidths=[60, 272, 100, 100])
    tabela_itens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0052B4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tabela_itens)
    
    doc.build(story, onFirstPage=desenhar_cabecalho_rodape, onLaterPages=desenhar_cabecalho_rodape, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

def renderizar_aba_proposta_cliente(salvar_proposta_final_fn=None, *args, **kwargs):
    st.markdown("## 📄 Proposta Final / Visualização do Cliente")
    st.caption("Revise os dados da proposta, visualize o documento formatado e gere o PDF final.")
    
    cliente = st.session_state.get("_safe_cliente_nome", "")
    cnpj = st.session_state.get("_safe_cnpj_val", "")
    itens = st.session_state.get("rascunho_itens", [])
    numero_proposta = st.session_state.get("proposta_id_ativo", "10/00001/2026")
    
    if not cliente or not itens:
        st.warning("⚠️ Nenhum cliente ou item encontrado no rascunho atual. Por favor, volte à aba 'Proposta Rascunho' e preencha os dados.")
        if st.button("⬅️ Voltar para Rascunho"):
            st.session_state["aba_ativa"] = "proposta"
            st.rerun()
        return

    st.markdown(f"### Proposta para: **{cliente}** (CNPJ: {cnpj or 'Não informado'})")
    st.markdown(f"**Número:** `{numero_proposta}`")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Exibir tabela visual na tela
    df_preview = pd.DataFrame(itens)
    if "Tarifa (R$)" in df_preview.columns:
        df_preview["Tarifa (R$)"] = df_preview["Tarifa (R$)"].apply(lambda x: f"R$ {float(x):,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    colunas_visiveis = [c for c in ["Código", "Descrição", "Unidade", "Tarifa (R$)", "Observações"] if c in df_preview.columns]
    st.dataframe(df_preview[colunas_visiveis], use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    pdf_bytes = gerar_pdf_proposta(cliente, cnpj, itens, numero_proposta)
    
    col_dl, col_salvar = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥 Descarregar Proposta em PDF",
            data=pdf_bytes,
            file_name=f"Proposta_{numero_proposta.replace('/', '-')}_{cliente}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
    with col_salvar:
        if st.button("💾 Salvar Proposta no Histórico", use_container_width=True):
            if salvar_proposta_final_fn:
                sucesso = salvar_proposta_final_fn(numero_proposta, cliente, cnpj, itens)
                if sucesso:
                    st.success("Proposta salva com sucesso no histórico!")
                else:
                    st.error("Erro ao salvar a proposta no histórico.")
            else:
                st.success("Proposta gravada com sucesso!")
