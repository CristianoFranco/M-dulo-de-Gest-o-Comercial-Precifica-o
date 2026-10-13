import streamlit as st
import pandas as pd
from datetime import datetime
import io
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def gerar_pdf_proposta_completo(numero_proposta, cliente_nome, cnpj_val, contato_cliente, objeto_proposta, itens_proposta):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    body_style = ParagraphStyle(
        'CorpoTexto',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=10
    )
    
    bold_style = ParagraphStyle(
        'CorpoNegrito',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    titulo_style = ParagraphStyle(
        'TituloSecao',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0052B4'),
        spaceBefore=12,
        spaceAfter=6
    )

    # Data atual por extenso
    meses = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    agora = datetime.now()
    data_extenso = f"Indaiatuba - SP, {agora.day:02d} de {meses[agora.month - 1]} de {agora.year}."
    
    story.append(Paragraph(data_extenso, body_style))
    story.append(Spacer(1, 8))
    
    # Cabeçalho da Proposta com as variáveis WWWWW, XXXXXXXX, ZZZZZZZ, yyyyyyyyy
    story.append(Paragraph(f"<b>PROPOSTA Nº {numero_proposta}</b>", body_style))
    story.append(Paragraph(f"À<br/><b>{cliente_nome}</b>", body_style))
    story.append(Paragraph(f"<b>REF:</b> {objeto_proposta}", body_style))
    story.append(Paragraph(f"<b>Contato:</b> {contato_cliente}", body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Prezados,", body_style))
    texto_intro = (
        f"Apresentamos a proposta comercial da Globex Multimodal para a gestão de armazenagem e movimentação de cargas da <b>{cliente_nome}</b>. "
        "Sediada estrategicamente no polo logístico de Indaiatuba-SP, a Globex combina infraestrutura moderna, rigor técnico e agilidade operacional. "
        "Desenvolvemos operações sob medida para cadeias de suprimentos exigentes, assegurando controle de ponta a ponta, total conformidade regulatória e integridade máxima dos seus produtos."
    )
    story.append(Paragraph(texto_intro, body_style))
    
    texto_intro2 = (
        f"Apresentamos a seguir nossa tabela de serviços e tarifas. Para facilitar a compreensão e o planejamento financeiro da <b>{cliente_nome}</b>, "
        "apresentaremos na apresentação da proposta uma simulação prática da aplicação dessas tarifas para o período informado, calculada com base no volume "
        "e nas premissas operacionais compartilhadas pela sua equipe. Trata-se de uma projeção ilustrativa desenhada para dar total visibilidade ao custo estimado da operação."
    )
    story.append(Paragraph(texto_intro2, body_style))
    story.append(Spacer(1, 10))
    
    # Assinaturas / Equipe Comercial
    story.append(Paragraph("<b>Wilson Santos</b> – Gerente Comercial &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 99888-2855", body_style))
    story.append(Paragraph("<b>Richarlles Nascimento</b> – Executivo de Contas &nbsp;&nbsp;|&nbsp;&nbsp; Tel.: (19) 3936-8520", body_style))
    story.append(Paragraph("<b>Adonis Valias</b> – Diretor Comercial", body_style))
    story.append(Spacer(1, 15))
    
    # Categorização e Divisão em Blocos Separados
    categorias_map = {
        "Armazenagem": "ARMAZENAGEM",
        "Seguro": "SEGURO",
        "Serviço": "SERVIÇOS",
        "Serviços e Movimentações": "SERVIÇOS",
        "Movimentação (Handling)": "MOVIMENTAÇÃO",
        "Outros": "TARIFÁRIO DE SERVIÇOS CONEXOS"
    }

    # Agrupar itens por categoria mapeada
    blocos_dados = {
        "ARMAZENAGEM": [],
        "SEGURO": [],
        "SERVIÇOS": [],
        "MOVIMENTAÇÃO": [],
        "TARIFÁRIO DE SERVIÇOS CONEXOS": []
    }

    for item in itens_proposta:
        cat_original = str(item.get("Categoria", "")).strip()
        cat_chave = categorias_map.get(cat_original, "TARIFÁRIO DE SERVIÇOS CONEXOS")
        
        tarifa_val = item.get("Tarifa (R$)", 0.0)
        try:
            tarifa_float = float(tarifa_val)
            tarifa_str = "R$ " + "{:,.5f}".format(tarifa_float).replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            tarifa_str = str(tarifa_val)

        blocos_dados[cat_chave].append([
            str(item.get("Código", "")),
            str(item.get("Descrição", "")),
            str(item.get("Unidade", "")),
            tarifa_str,
            str(item.get("Observações", ""))
        ])

    # Renderizar cada bloco com espaçamento de 3 linhas (Spacers)
    for nome_bloco, linhas in blocos_dados.items():
        if linhas:
            story.append(Paragraph(nome_bloco, titulo_style))
            story.append(Spacer(1, 4))
            
            tabela_conteudo = [["Código", "Descrição", "Unidade", "Tarifa", "Observações"]] + linhas
            tabela = Table(tabela_conteudo, colWidths=[55, 170, 90, 85, 140])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052B4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(tabela)
            # Espaçamento correspondente a 3 linhas entre os blocos
            story.append(Spacer(1, 36))

    # Termo de Aceite
    story.append(PageBreak())
    story.append(Paragraph("TERMO DE ACEITE PARA PRESTAÇÃO DE SERVIÇOS", titulo_style))
    story.append(Spacer(1, 6))
    
    termo_p1 = (
        f"Com a assinatura do presente termo, a empresa cliente, por meio de seu representante, responsável pelo fechamento da venda, "
        f"declara que aceita todas as condições dispostas na proposta <b>{numero_proposta}</b> apresentada pela <b>GLOBEX MULTIMODAL</b>, "
        "ficando ciente que: A prestação dos serviços inicia-se na data expressa no presente termo."
    )
    story.append(Paragraph(termo_p1, body_style))
    
    termo_p2 = (
        "A assinatura do presente termo autoriza a GLOBEX MULTIMODAL a iniciar a prestação dos serviços e consequente faturamento, "
        "seguindo os valores e condições descritas na proposta comercial ora aceita."
    )
    story.append(Paragraph(termo_p2, body_style))
    
    clausulas = [
        "1) Caso seja detectado o inadimplemento da empresa cliente em efetuar os pagamentos, fica permitida a cobrança do débito atualizado pelo IPCA/IBGE, acrescido de multa de mora de 2% e juros de 1% ao mês, pro rata tempore.",
        "2) O presente termo é parte integrante e acessória do contrato de prestação de serviços, prevalecendo como documento principal até a assinatura do mesmo.",
        "3) Os dados cadastrais abaixo especificados poderão ser utilizados pela GLOBEX MULTIMODAL para emissão dos documentos fiscais correspondentes."
    ]
    for c in clausulas:
        story.append(Paragraph(c, body_style))
    
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
        story.append(Paragraph(campo, body_style))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Indaiatuba - SP, _____ de ______________________ de {agora.year}.", body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("______________________________________________________", body_style))
    story.append(Paragraph("<b>Nome:</b><br/><b>Função:</b><br/><b>RG:</b>", body_style))

    doc.build(story)
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
        
        # POP-UP / FORMULÁRIO DE CAMPOS ADICIONAIS ANTES DE GERAR O PDF E SALVAR
        st.markdown("---")
        st.markdown("### ⚙️ Parâmetros da Proposta Comercial (PDF)")
        
        col_pop1, col_pop2 = st.columns(2)
        with col_pop1:
            input_razao_social = st.text_input("Razão Social da Empresa Contratante (XXXXXXXX):", value=cliente_nome, key="input_popup_razao_social")
            input_contato = st.text_input("Contato do Cliente (yyyyyyyyy):", placeholder="Ex: Nome do responsável", key="input_popup_contato")
        with col_pop2:
            input_objeto = st.text_input("Objeto da Proposta (ZZZZZZZ):", placeholder="Ex: Prestação de serviços logísticos", key="input_popup_objeto")
            st.markdown(f"**Número da Proposta (WWWWW):** `{numero_proposta_atual}`")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Salvar proposta e gerar PDF", type="primary", use_container_width=True):
            c_nome = str(input_razao_social).strip()
            c_cnpj = str(st.session_state.get("_safe_cnpj_val") or st.session_state.get("proposta_cliente_cnpj", "")).strip()
            c_contato = str(input_contato).strip()
            c_objeto = str(input_objeto).strip()
            
            if not c_nome:
                st.error("⚠️ O nome da Razão Social é obrigatório!")
            elif not c_contato:
                st.error("⚠️ O Contato do cliente é obrigatório!")
            elif not c_objeto:
                st.error("⚠️ O Objeto da proposta é obrigatório!")
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
                    st.success("Proposta salva com sucesso no Google Sheets!")
                    
                    if REPORTLAB_DISPONIVEL:
                        pdf_bytes = gerar_pdf_proposta_completo(numero_proposta_atual, c_nome, c_cnpj, c_contato, c_objeto, itens_rascunho)
                        nome_arquivo_pdf = "Proposta_" + numero_proposta_atual.replace("/", "_") + ".pdf"
                        
                        st.download_button(
                            label="📥 Baixar / Visualizar PDF Gerado",
                            data=pdf_bytes,
                            file_name=nome_arquivo_pdf,
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    st.session_state["proposta_id_em_edicao"] = None
                    st.session_state["proposta_id_ativo"] = None
                    st.session_state["rascunho_itens"] = []
                    st.session_state["_safe_cliente_nome"] = ""
                    st.session_state["_safe_cnpj_val"] = ""
                    
                    for k in list(st.session_state.keys()):
                        if k.startswith("input_tarifa_"):
                            del st.session_state[k]
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
