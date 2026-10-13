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

def gerar_pdf_proposta_completo(numero_proposta, cliente_nome, cnpj_val, contato_cliente, objeto_proposta, iss_val, prazo_val, vigencia_val, itens_proposta):
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

    # ESTILOS DEDICADOS PARA AS CÉLULAS DAS TABELAS
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
        "apresentaremos na apresentação da proposta uma simulação prática da aplicação dessas tarifas para o período informado, calculada com base no volume "
        "e nas premissas operacionais compartilhadas pela sua equipe. Trata-se de uma projeção ilustrativa desenhada para dar total visibilidade ao custo estimado da operação."
    )
    story.append(Paragraph(texto_intro2, body_justify_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Wilson Santos</b> – Gerente Comercial &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 99888-2855", body_left_style))
    story.append(Paragraph("<b>Richarlles Nascimento</b> – Executivo de Contas &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 3936-8520", body_left_style))
    story.append(Paragraph("<b>Adonis Valias</b> – Diretor Comercial", body_left_style))
    story.append(Spacer(1, 14))
    
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
                Paragraph("Observações", th_style)
            ]
            
            tabela_conteudo = [cabecalho] + linhas
            tabela = Table(tabela_conteudo, colWidths=[45, 165, 125, 85, 120])
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
    story.append(Paragraph(texto_premissas, premissas_style))

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
    
    data_final_termo = "Indaiatuba - SP, _____ de ______________________ de ___________. "
    story.append(Paragraph(data_final_termo, body_left_style))
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
    st.markdown("## Visão Final da Proposta (Cliente)")
    st.caption("Visualização pronta para conferência, geração de PDF e salvamento.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    itens_rascunho = st.session_state.get("rascunho_itens", [])
    
    cliente_nome = str(st.session_state.get("_safe_cliente_nome") or st.session_state.get("input_cli_nome_tela2", "")).strip()
    cnpj_val = str(st.session_state.get("_safe_cnpj_val") or st.session_state.get("proposta_cliente_cnpj", "")).strip()
    
    if st.session_state.get("proposta_id_em_edicao"):
        numero_proposta_atual = str(st.session_state["proposta_id_em_edicao"])
    elif st.session_state.get("proposta_id_ativo"):
        numero_proposta_atual = str(st.session_state["proposta_id_ativo"])
    else:
        agora = datetime.now()
        mes_str = agora.strftime("%m")
        ano_str = agora.strftime("%Y")
        seq = st.session_state.get("sequencial_proposta", 1)
        numero_proposta_atual = mes_str + "/" + "{:05d}".format(seq) + "/" + ano_str

    if not REPORTLAB_DISPONIVEL:
        st.error("⚠️ A biblioteca 'reportlab' não está instalada ou disponível no ambiente. O PDF não pode ser gerado.")
        return

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
            st.rerun()

    st.markdown("### Documento da Proposta")
    if not itens_rascunho:
        st.warning("Nenhum item pendente no rascunho. Monte os itens na Tela 2 (Proposta Rascunho).")
    else:
        col_info1, col_info2, col_info3 = st.columns([2.5, 1.5, 1.5])
        with col_info1:
            lbl_cli = cliente_nome if cliente_nome else "Não Informado"
            st.markdown("Cliente / Razão Social:\n### " + lbl_cli)
        with col_info2:
            lbl_cnpj = cnpj_val if cnpj_val else "Não Informado"
            st.markdown("CNPJ:\n### " + lbl_cnpj)
        with col_info3:
            st.markdown("Número da Proposta:\n### " + numero_proposta_atual)
        st.markdown("<br>", unsafe_allow_html=True)
        
        dados_estaticos = []
        for item in itens_rascunho:
            tarifa_val = item.get("Tarifa (R$)", 0.0)
            try:
                tarifa_float = float(tarifa_val)
                tarifa_fmt = "R$ " + "{:,.5f}".format(tarifa_float).replace(",", "X").replace(".", ",").replace("X", ".")
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
        
        st.dataframe(df_estatico, use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### ⚙️ Parâmetros da Proposta Comercial (PDF)")
        
        with st.form("form_parametros_proposta_pdf"):
            col_pop1, col_pop2 = st.columns(2)
            with col_pop1:
                input_razao_social = st.text_input("Razão Social da Empresa Contratante:", value=cliente_nome, key="input_popup_razao_social")
                input_contato = st.text_input("Contato do Cliente:", placeholder="Ex: Nome do responsável", key="input_popup_contato")
                input_iss = st.text_input("% I.S.S sobre o faturamento (VVVV):", value="5.0", key="input_popup_iss")
            with col_pop2:
                input_objeto = st.text_input("Objeto da Proposta:", placeholder="Ex: Prestação de serviços logísticos", key="input_popup_objeto")
                input_prazo = st.text_input("Prazo de pagamento em dias (ZZZZ):", value="30", key="input_popup_prazo")
                input_vigencia = st.text_input("Vigência mínima em meses (ZZZZ):", value="12", key="input_popup_vigencia")
                st.markdown(f"**Número da Proposta:** `{numero_proposta_atual}`")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted_pdf = st.form_submit_button("💾 Salvar Proposta e Gerar PDF", use_container_width=True, type="primary")

            if submitted_pdf:
                c_nome = str(input_razao_social).strip()
                c_cnpj = str(st.session_state.get("_safe_cnpj_val") or st.session_state.get("proposta_cliente_cnpj", "")).strip()
                c_contato = str(input_contato).strip()
                c_objeto = str(input_objeto).strip()
                c_iss = str(input_iss).strip()
                c_prazo = str(input_prazo).strip()
                c_vigencia = str(input_vigencia).strip()
                
                if not c_nome:
                    st.error("⚠️ O nome da Razão Social é obrigatório!")
                elif not c_contato:
                    st.error("⚠️ O Contato do cliente é obrigatório!")
                elif not c_objeto:
                    st.error("⚠️ O Objeto da proposta é obrigatório!")
                elif not itens_rascunho:
                    st.error("⚠️ Não há itens no rascunho para salvar.")
                elif salvar_proposta_sheets_fn:
                    linhas_para_salvar = []
                    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for item in itens_rascunho:
                        try:
                            t_val = float(item.get("Tarifa (R$)", 0.0))
                        except (ValueError, TypeError):
                            t_val = 0.0
                            
                        linhas_para_salvar.append({
                            "Proposta": numero_proposta_atual,
                            "Data": data_hoje,
                            "Cliente": c_nome,
                            "CNPJ": c_cnpj,
                            "Código": str(item.get("Código", "")),
                            "Descrição": str(item.get("Descrição", "")),
                            "Categoria": str(item.get("Categoria", "")),
                            "Unidade": str(item.get("Unidade", "")),
                            "Tarifa (R$)": t_val,
                            "Observações": str(item.get("Observações", ""))
                        })
                    sucesso = salvar_proposta_sheets_fn(linhas_para_salvar)
                    if sucesso:
                        pdf_bytes = gerar_pdf_proposta_completo(
                            numero_proposta_atual,
                            c_nome,
                            c_cnpj,
                            c_contato,
                            c_objeto,
                            c_iss,
                            c_prazo,
                            c_vigencia,
                            itens_rascunho
                        )
                        nome_arquivo_pdf = "Proposta_" + str(numero_proposta_atual).replace("/", "_") + ".pdf"
                        
                        st.session_state["ultimo_pdf_bytes"] = pdf_bytes
                        st.session_state["ultimo_pdf_nome"] = nome_arquivo_pdf
                        
                        st.session_state["proposta_id_em_edicao"] = None
                        st.session_state["proposta_id_ativo"] = None
                        st.session_state["rascunho_itens"] = []
                        st.session_state["_safe_cliente_nome"] = ""
                        st.session_state["_safe_cnpj_val"] = ""
                        
                        for k in list(st.session_state.keys()):
                            if k.startswith("input_tarifa_"):
                                del st.session_state[k]
                        st.rerun()
                    else:
                        st.error("Falha ao salvar no Google Sheets.")

    st.markdown("---")
    st.markdown("### Consulta Propostas Finalizadas")
    with st.expander("Filtrar e Consultar Propostas Salvas", expanded=True):
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
                if "Proposta" in df_filtrado.columns:
                    if mes_consulta != "Todos":
                        prefixo = str(mes_consulta) + "/"
                        df_filtrado = df_filtrado[df_filtrado["Proposta"].astype(str).str.startswith(prefixo)]
                    if ano_consulta.strip():
                        sufixo = "/" + ano_consulta.strip()
                        df_filtrado = df_filtrado[df_filtrado["Proposta"].astype(str).str.endswith(sufixo)]
                
                colunas_resumo = [c for c in ["Proposta", "Data", "Cliente"] if c in df_filtrado.columns]
                df_resumido = df_filtrado[colunas_resumo].drop_duplicates(subset=["Proposta"]).reset_index(drop=True)
                
                if "Data" in df_resumido.columns:
                    df_resumido["Data"] = df_resumido["Data"].astype(str).str.split().str[0]

                def parse_ordenacao_proposta(prop_str):
                    try:
                        partes = str(prop_str).split('/')
                        if len(partes) == 3:
                            mes_val = int(partes[0])
                            cod_val = int(partes[1])
                            ano_val = int(partes[2])
                            return (ano_val, mes_val, cod_val)
                    except ValueError:
                        pass
                    return (9999, 12, 99999)

                if not df_resumido.empty and "Proposta" in df_resumido.columns:
                    df_resumido["_sort_key"] = df_resumido["Proposta"].apply(parse_ordenacao_proposta)
                    df_resumido = df_resumido.sort_values(by="_sort_key", ascending=True).drop(columns=["_sort_key"]).reset_index(drop=True)

                st.markdown("Propostas Encontradas: " + str(len(df_resumido)))
                st.dataframe(df_resumido, use_container_width=True, hide_index=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                df_resumido["Opcao_Select"] = df_resumido["Proposta"].astype(str) + " - " + df_resumido["Cliente"].astype(str)
                propostas_unicas = [""] + df_resumido["Opcao_Select"].tolist()
                
                col_sel_prop, col_btn_carregar = st.columns([3, 1])
                with col_sel_prop:
                    prop_escolhida_completa = st.selectbox(
                        "Selecione uma proposta para editar:",
                        options=propostas_unicas,
                        key="select_proposta_para_editar"
                    )
                
                prop_escolhida = prop_escolhida_completa.split(" - ")[0].strip() if prop_escolhida_completa else ""

                with col_btn_carregar:
                    st.write("")
                    st.write("")
                    if st.button("Carregar Proposta", type="primary", use_container_width=True):
                        if prop_escolhida:
                            df_prop_sel = df_historico[df_historico["Proposta"].astype(str).str.strip() == prop_escolhida.strip()]
                            
                            if not df_prop_sel.empty:
                                st.session_state["proposta_id_em_edicao"] = prop_escolhida.strip()
                                st.session_state["proposta_id_ativo"] = prop_escolhida.strip()
                                
                                primeiro_reg = df_prop_sel.iloc[0]
                                c_nome_carregado = str(primeiro_reg.get("Cliente", ""))
                                c_cnpj_carregado = str(primeiro_reg.get("CNPJ", "")) if "CNPJ" in primeiro_reg else ""
                                
                                st.session_state["_safe_cliente_nome"] = c_nome_carregado
                                st.session_state["_safe_cnpj_val"] = c_cnpj_carregado
                                
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
                                st.success("Proposta carregada com sucesso!")
                                st.rerun()
                        else:
                            st.warning("Selecione uma proposta válida na lista.")
            else:
                st.info("Nenhuma proposta gravada na folha Propostas_Salvas.")
