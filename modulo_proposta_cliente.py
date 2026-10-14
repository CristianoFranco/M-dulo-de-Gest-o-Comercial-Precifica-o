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
    td_style_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#222222'), alignment=TA_RIGHT)

    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    agora = datetime.now()
    data_extenso = f"Indaiatuba - SP, {agora.day:02d} de {meses[agora.month - 1]} de {agora.year}."
    
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

    story.append(Paragraph("Tabela de Preços e Serviços", titulo_tabelas_style))
    story.append(Spacer(1, 4))

    # Separamos em dicionários distintos para controlar a ordem de exibição exata
    blocos_principais = {
        "ARMAZENAGEM": [],
        "SEGURO": [],
        "MOVIMENTAÇÃO (HANDLING)": [],
        "SERVIÇOS": []
    }
    
    bloco_conexos = {
        "SERVIÇOS CONEXOS": []
    }

    for item in itens_proposta:
        cat_original = str(item.get("Categoria", "")).strip().lower()
        if "armazenagem" in cat_original:
            cat_chave = "ARMAZENAGEM"
        elif "seguro" in cat_original:
            cat_chave = "SEGURO"
        elif "conexos" in cat_original or "outros" in cat_original or "serviços conexos" in cat_original:
            cat_chave = "SERVIÇOS CONEXOS"
        elif "movimentação" in cat_original or "handling" in cat_original or "movimentacao" in cat_original:
            cat_chave = "MOVIMENTAÇÃO (HANDLING)"
        elif "serviço" in cat_original or "servico" in cat_original:
            cat_chave = "SERVIÇOS"
        else:
            cat_chave = "SERVIÇOS CONEXOS"
        
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

        linha_tabela = [p_cod, p_desc, p_und, p_tar, p_obs]
        if cat_chave == "SERVIÇOS CONEXOS":
            bloco_conexos["SERVIÇOS CONEXOS"].append(linha_tabela)
        else:
            blocos_principais[cat_chave].append(linha_tabela)

    def adicionar_tabelas_ao_story(dicionario_blocos):
        nonlocal primeiro_bloco
        for nome_bloco, linhas in dicionario_blocos.items():
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
                    Paragraph("Observações", th_style)
                ]
                tabela = Table([cabecalho] + linhas, colWidths=[45, 165, 125, 85, 120])
                tabela.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052B4')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(tabela)
                primeiro_bloco = False

    primeiro_bloco = True
    # 1. Adiciona Armazenagem, Seguro, Movimentação e Serviços
    adicionar_tabelas_ao_story(blocos_principais)

    if fat_minimo_esc:
        story.append(Spacer(1, 12))
        conteudo_fat_min = [
            [Paragraph("<b>Faturamento Mínimo Mensal:</b>", fat_min_title_style)],
            [Paragraph(fat_minimo_esc, fat_min_text_style)]
        ]
        tabela_fat_min = Table(conteudo_fat_min, colWidths=[540])
        tabela_fat_min.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0052B4')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tabela_fat_min)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Premissas:</b>", premissas_style))
    texto_premissas = (
        f"1. Impostos: {iss_esc}% I.S.S sobre o faturamento não incluso. A incluir nos preços no total da NF de serviços;<br/>"
        f"2. Prazo de pagamento: {prazo_esc} dias corridos após a data de emissão da NF;<br/>"
        "3. Validade da proposta: A presente proposta tem validade de 30 dias;<br/>"
        f"4. Vigência Min: {vigencia_esc} meses;<br/>"
        "5. Os serviços não discriminados nesta tabela serão acordados entre as partes;<br/>"
        "6. O faturamento e cobrança dos serviços serão MENSAIS;<br/>"
        "7. Mão de obra inclusa para prestação dos serviços: Ajudante, Separador, Conferente, Líder e Operador. Não dedicadas.<br/>"
        "8. Cubagem padrão: posição palete: 1,74m³ / posição gaveta: 0,72m³<br/>"
        "9. Dimensões padrão: posição palete: 1,00 x 1,20 x 1,45 / posição gaveta: 1,00 x 1,20 x 0,60"
    )
    if outras_premissas_esc:
        texto_premissas += f"<br/>10. {outras_premissas_esc}"

    story.append(Paragraph(texto_premissas, premissas_style))

    # 2. Adiciona o bloco de Serviços Conexos LOGO ABAIXO das premissas
    adicionar_tabelas_ao_story(bloco_conexos)

    story.append(PageBreak())
    
    story.append(Paragraph("<b>TERMO DE ACEITE PARA PRESTAÇÃO DE SERVIÇOS</b>", titulo_termo_center))
    story.append(Spacer(1, 6))
    
    termo_p1 = (
        f"Com a assinatura do presente termo, a empresa cliente, por meio de seu representante, responsável pelo fechamento da venda, "
        f"declara que aceita todas as condições dispostas na proposta <b>{num_prop_esc}</b> apresentada pela <b>GLOBEX MULTIMODAL</b>, "
        "ficando ciente que: A prestação dos serviços inicia-se na data expressa no presente termo."
    )
    story.append(Paragraph(termo_p1, body_justify_style))
    
    termo_p2 = (
        "A assinatura do presente termo autoriza a GLOBEX MULTIMODAL a iniciar a prestação dos serviços e consequente faturamento, "
        "seguindo os valores e condições descritas na proposta comercial ora aceita."
    )
    story.append(Paragraph(termo_p2, body_justify_style))
    
    clausulas = [
        "1) Caso seja detectado o inadimplemento da empresa cliente em efetuar os pagamentos, fica permitida a cobrança do débito atualizado pelo IPCA/IBGE, acrescido de multa de mora de 2% e juros de 1% ao mês, pro rata tempore.",
        "2) O presente termo é parte integrante e acessória do contrato de prestação de serviços, prevalecendo como documento principal até a assinatura do mesmo.",
        "3) Os dados cadastrais abaixo especificados poderão ser utilizados pela GLOBEX MULTIMODAL para emissão dos documentos fiscais correspondentes."
    ]
    for c in clausulas:
        story.append(Paragraph(c, body_justify_style))
    
    story.append(Spacer(1, 8))
    
    campos_cadastro = [
        "<b>NOME/RAZÃO SOCIAL:</b> ____________________________________________________________________",
        "<b>CPF/CNPJ:</b> ____________________________________________________________________________",
        "<b>RG/INSCRIÇÃO ESTADUAL:</b> ________________________________________________________________",
        "<b>DATA DE CONSTITUIÇÃO DA EMPRESA:</b> ____________________________________________________",
        "<b>RAMO DE ATIVIDADE:</b> ____________________________________________________________________",
        "<b>E-MAIL:</b> ________________________________________________________________________________",
        "<b>ENDEREÇO:</b> ______________________________________________________________________________",
        "<b>BAIRRO:</b> ________________________________________________________________________________",
        "<b>CIDADE:</b> ________________________________________________________________________________",
        "<b>CEP:</b> ____________________________________________________________________________________",
        "<b>TELEFONE:</b> ______________________________________________________________________________",
        "<b>CONTATO:</b> ________________________________________________________________________________"
    ]
    for campo in campos_cadastro:
        story.append(Paragraph(campo, body_left_style))
        
    story.append(Spacer(1, 8))
    story.append(Paragraph("Indaiatuba - SP, _____ de ______________________ de ___________. ", body_left_style))
    story.append(Spacer(1, 18))
    story.append(Paragraph("______________________________________________________", body_left_style))
    story.append(Paragraph("<b>Nome:</b><br/><b>Função:</b><br/><b>RG:</b>", body_left_style))

    try:
        doc.build(story, onFirstPage=desenhar_cabecalho_rodape, onLaterPages=desenhar_cabecalho_rodape)
    except Exception as e:
        st.error(f"Erro ao compilar o PDF no ReportLab: {e}")
        return None

    buffer.seek(0)
    return buffer

def renderizar_aba_proposta_cliente(salvar_proposta_sheets_fn=None, carregar_propostas_salvas_fn=None):
    st.markdown("""
        <style>
            div.stButton > button[kind="secondary"] {
                background-color: #0052B4 !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                border: 1px solid #0052B4 !important;
                border-radius: 6px !important;
            }
            div.stButton > button[kind="secondary"]:hover {
                background-color: #003B82 !important;
                color: #FFFFFF !important;
                border: 1px solid #003B82 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## Visão Final da Proposta (Cliente)")
    st.caption("Visualização pronta para conferência, geração de PDF e salvamento.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "form_prop_cliente_version" not in st.session_state:
        st.session_state["form_prop_cliente_version"] = 1

    ver_form = st.session_state["form_prop_cliente_version"]

    if carregar_propostas_salvas_fn and st.session_state.get("btn_carregar_proposta_clicado"):
        st.session_state["btn_carregar_proposta_clicado"] = False
        prop_escolhida_raw = str(st.session_state.get("proposta_selecionada_temp", "")).strip()
        if prop_escolhida_raw:
            prop_escolhida = prop_escolhida_raw.split(" - ")[0].strip()
            try:
                df_historico_tmp = carregar_propostas_salvas_fn()
                if isinstance(df_historico_tmp, pd.DataFrame) and not df_historico_tmp.empty:
                    df_prop_sel = df_historico_tmp[df_historico_tmp["Proposta"].astype(str).str.strip() == prop_escolhida]
                    if not df_prop_sel.empty:
                        st.session_state["proposta_id_em_edicao"] = prop_escolhida
                        st.session_state["proposta_id_ativo"] = prop_escolhida
                        
                        primeiro_reg = df_prop_sel.iloc[0]
                        c_nome_carregado = str(primeiro_reg.get("Cliente", ""))
                        c_cnpj_carregado = str(primeiro_reg.get("CNPJ", "")) if "CNPJ" in primeiro_reg else ""
                        
                        st.session_state["_safe_cliente_nome"] = c_nome_carregado
                        st.session_state["_safe_cnpj_val"] = c_cnpj_carregado
                        
                        st.session_state["form_prop_cliente_version"] += 1
                        ver_form = st.session_state["form_prop_cliente_version"]

                        st.session_state[f"input_popup_razao_social_{ver_form}"] = c_nome_carregado
                        st.session_state[f"input_popup_contato_{ver_form}"] = ""
                        st.session_state[f"input_popup_objeto_{ver_form}"] = ""
                        st.session_state[f"input_popup_iss_{ver_form}"] = "2.5"
                        st.session_state[f"input_popup_prazo_{ver_form}"] = "30"
                        st.session_state[f"input_popup_vigencia_{ver_form}"] = "12"
                        st.session_state[f"input_popup_fat_minimo_{ver_form}"] = ""
                        st.session_state[f"input_popup_outras_premissas_{ver_form}"] = ""
                        
                        novos_itens = []
                        for _, row in df_prop_sel.iterrows():
                            try:
                                tarifa_val = float(row.get("Tarifa (R$)", 0.0))
                            except (ValueError, TypeError):
                                tarifa_val = 0.0
                                
                            novos_itens.append({
                                "Código": str(row.get("Código", "")),
                                "Descrição": str(row.get("Descrição", "")),
                                "Tarifa (R$)": tarifa_val,
                                "Unidade": str(row.get("Unidade", "")),
                                "Observações": str(row.get("Observações", "")),
                                "Categoria": str(row.get("Categoria", "")),
                                "Cat_Code": "GEN"
                            })
                            
                        st.session_state["rascunho_itens"] = novos_itens
                        st.session_state["mensagem_sucesso_carregar"] = f"Proposta '{prop_escolhida}' carregada com sucesso!"
                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar proposta: {e}")

    if st.session_state.get("ultimo_pdf_bytes"):
        st.success("✅ Proposta salva com sucesso no Google Sheets e documento PDF gerado!")
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Baixar / Visualizar Proposta em PDF",
            data=st.session_state["ultimo_pdf_bytes"],
            file_name=st.session_state.get("ultimo_pdf_nome", "Proposta.pdf"),
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Iniciar Nova Proposta", use_container_width=True):
            st.session_state.pop("ultimo_pdf_bytes", None)
            st.session_state.pop("ultimo_pdf_nome", None)
            st.session_state["proposta_id_em_edicao"] = None
            st.session_state["proposta_id_ativo"] = None
            st.session_state["rascunho_itens"] = []
            st.session_state["_safe_cliente_nome"] = ""
            st.session_state["_safe_cnpj_val"] = ""
            st.session_state["form_prop_cliente_version"] += 1
            st.rerun()
        
        st.markdown("---")
        return

    itens_rascunho = st.session_state.get("rascunho_itens", [])
    cliente_nome = str(st.session_state.get("_safe_cliente_nome") or st.session_state.get("input_cli_nome_tela2", "")).strip()
    cnpj_val = str(st.session_state.get("_safe_cnpj_val") or st.session_state.get("proposta_cliente_cnpj", "")).strip()
    
    key_rz = f"input_popup_razao_social_{ver_form}"
    key_ct = f"input_popup_contato_{ver_form}"
    key_is = f"input_popup_iss_{ver_form}"
    key_obj = f"input_popup_objeto_{ver_form}"
    key_pz = f"input_popup_prazo_{ver_form}"
    key_vg = f"input_popup_vigencia_{ver_form}"
    key_fm = f"input_popup_fat_minimo_{ver_form}"
    key_op = f"input_popup_outras_premissas_{ver_form}"

    if key_rz not in st.session_state:
        st.session_state[key_rz] = cliente_nome
    if key_ct not in st.session_state:
        st.session_state[key_ct] = ""
    if key_is not in st.session_state:
        st.session_state[key_is] = "2.5"
    if key_obj not in st.session_state:
        st.
