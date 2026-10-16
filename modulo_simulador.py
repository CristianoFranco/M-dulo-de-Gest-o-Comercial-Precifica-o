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
            Paragraph(f"R$ {t_val:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."), td_style_right),
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

def renderizar_aba_simulacao(carregar_dados_fn, carregar_propostas_salvas_fn):
    st.markdown("## 📊 Simulador Comercial & Cenários")
    st.caption("Simule volumes, ajuste tarifas pontualmente ou em massa, visualize gráficos de categoria e exporte relatórios.")
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        df_historico = carregar_propostas_salvas_fn()
    except Exception:
        df_historico = pd.DataFrame()

    if df_historico.empty or "Proposta" not in df_historico.columns:
        st.info("Nenhuma proposta salva encontrada para iniciar a simulação.")
        return

    propostas_disponiveis = [str(p).strip() for p in df_historico["Proposta"].dropna().unique() if str(p).strip() and str(p) != "nan"]
    
    col_sel_p, _ = st.columns([2, 2])
    with col_sel_p:
        proposta_selecionada = st.selectbox("Selecione a Proposta para Simulação:", options=[""] + propostas_disponiveis, key="select_prop_simulador")

    if not proposta_selecionada:
        st.warning("Selecione uma proposta acima para carregar os itens no simulador.")
        return

    df_prop = df_historico[df_historico["Proposta"].astype(str).str.strip() == proposta_selecionada].copy()
    cliente_atual = str(df_prop["Cliente"].iloc[0]) if "Cliente" in df_prop.columns and not df_prop.empty else "Cliente"

    chave_estado_itens = f"simulador_itens_{proposta_selecionada}"
    if chave_estado_itens not in st.session_state:
        itens_iniciais = []
        for _, row in df_prop.iterrows():
            try:
                t_orig = float(row.get("Tarifa (R$)", 0.0))
            except (ValueError, TypeError):
                t_orig = 0.0
            
            itens_iniciais.append({
                "Código": str(row.get("Código", "")),
                "Descrição": str(row.get("Descrição", "")),
                "Categoria": str(row.get("Categoria", "Serviço")),
                "Unidade": str(row.get("Unidade", "")),
                "Tarifa Original": t_orig,
                "Tarifa Simulação": t_orig,
                "Quantidade": 0.0
            })
        st.session_state[chave_estado_itens] = itens_iniciais

    lista_itens = st.session_state[chave_estado_itens]

    st.markdown("---")
    st.markdown("### ⚡ Reajuste em Massa de Tarifas")
    col_m1, col_m2, col_m3 = st.columns([2, 2, 2])
    with col_m1:
        perc_massa = st.number_input("Aumento / Redução (%):", value=0.0, step=0.5, format="%.2f", key="input_perc_massa_sim")
    with col_m2:
        categorias_disponiveis = ["Todas"] + list(set([item["Categoria"] for item in lista_itens]))
        cat_massa = st.selectbox("Aplicar na Categoria:", options=categorias_disponiveis, key="select_cat_massa_sim")
    with col_m3:
        st.write("")
        st.write("")
        if st.button("🚀 Aplicar Reajuste em Massa", use_container_width=True):
            fator = 1.0 + (float(perc_massa) / 100.0)
            for item in lista_itens:
                if cat_massa == "Todas" or item["Categoria"] == cat_massa:
                    item["Tarifa Simulação"] = round(item["Tarifa Simulação"] * fator, 5)
            st.success(f"Reajuste de {perc_massa}% aplicado com sucesso!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Itens e Simulação de Quantidades / Tarifas")
    st.caption("Você pode alterar livremente a Tarifa de Simulação e informar a Quantidade prevista para cada item.")

    categorias_unicas = sorted(list(set([item["Categoria"] for item in lista_itens])))
    
    valor_total_geral = 0.0
    dados_tabela_final = []

    for idx_cat, cat in enumerate(categorias_unicas):
        st.markdown(f"**Categoria: {cat}**")
        
        # Exibe o cabeçalho vermelho em letras maiúsculas apenas no primeiro bloco
        if idx_cat == 0:
            h_cod, h_desc, h_cat_col, h_und, h_tar, h_qtd, h_tot = st.columns([1, 3, 2, 1.5, 2, 1.5, 2])
            with h_cod: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>CÓDIGO</span>", unsafe_allow_html=True)
            with h_desc: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>DESCRIÇÃO</span>", unsafe_allow_html=True)
            with h_cat_col: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>CATEGORIA</span>", unsafe_allow_html=True)
            with h_und: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>UNIDADE</span>", unsafe_allow_html=True)
            with h_tar: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>TARIFA (R$)</span>", unsafe_allow_html=True)
            with h_qtd: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>QTD. (SIMULAÇÃO)</span>", unsafe_allow_html=True)
            with h_tot: st.markdown("<span style='color: #FF4B4B; font-weight: bold;'>VALOR TOTAL (R$)</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 2px 0 6px 0;'>", unsafe_allow_html=True)

        for i, item in enumerate(lista_itens):
            if item["Categoria"] == cat:
                c_cod, c_desc, c_cat, c_und, c_tar, c_qtd, c_tot = st.columns([1, 3, 2, 1.5, 2, 1.5, 2])
                with c_cod:
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: 500;'>{item['Código']}</span>", unsafe_allow_html=True)
                with c_desc:
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: 500;'>{item['Descrição']}</span>", unsafe_allow_html=True)
                with c_cat:
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: 500;'>{item['Categoria']}</span>", unsafe_allow_html=True)
                with c_und:
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: 500;'>{item['Unidade']}</span>", unsafe_allow_html=True)
                with c_tar:
                    key_tar = f"sim_tar_{proposta_selecionada}_{item['Código']}_{i}"
                    val_str = st.text_input("Tarifa", value=str(item["Tarifa Simulação"]), key=key_tar, label_visibility="collapsed")
                    try:
                        t_num = float(val_str.replace(",", ".")) if val_str.strip() else 0.0
                    except ValueError:
                        t_num = 0.0
                    item["Tarifa Simulação"] = t_num
                with c_qtd:
                    key_qtd = f"sim_qtd_{proposta_selecionada}_{item['Código']}_{i}"
                    qtd_str = st.text_input("Qtd", value=str(item["Quantidade"]), key=key_qtd, label_visibility="collapsed")
                    try:
                        q_num = float(qtd_str.replace(",", ".")) if qtd_str.strip() else 0.0
                    except ValueError:
                        q_num = 0.0
                    item["Quantidade"] = q_num
                with c_tot:
                    v_tot = item["Tarifa Simulação"] * item["Quantidade"]
                    valor_total_geral += v_tot
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: 600; line-height: 2.4rem;'>R$ {v_tot:,.2f}</span>".replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

                dados_tabela_final.append({
                    "Código": item["Código"],
                    "Descrição": item["Descrição"],
                    "Categoria": item["Categoria"],
                    "Unidade": item["Unidade"],
                    "Tarifa Simulação": item["Tarifa Simulação"],
                    "Quantidade": item["Quantidade"],
                    "Valor Total": item["Tarifa Simulação"] * item["Quantidade"]
                })
        
        # Espaçamento reduzido entre os blocos (de <br><br> para espaçamento compacto)
        if idx_cat < len(categorias_unicas) - 1:
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 💰 Valor Total Geral da Simulação: **R$ {valor_total_geral:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown("<br>", unsafe_allow_html=True)

    df_simulacao_completo = pd.DataFrame(dados_tabela_final)

    if MATPLOTLIB_DISPONIVEL and valor_total_geral > 0:
        st.markdown("### 🥧 Distribuição de Custos por Categoria")
        df_cat_grp = df_simulacao_completo.groupby("Categoria")["Valor Total"].sum().reset_index()
        df_cat_grp = df_cat_grp[df_cat_grp["Valor Total"] > 0]

        if not df_cat_grp.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(
                df_cat_grp["Valor Total"],
                labels=df_cat_grp["Categoria"],
                autopct='%1.1f%%',
                startangle=140,
                colors=['#0052B4', '#60A5FA', '#1E3A8A', '#93C5FD', '#1E40AF']
            )
            ax.axis('equal')
            st.pyplot(fig)

    st.markdown("---")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_simulacao_completo.to_excel(writer, index=False, sheet_name='Simulação')
        output_excel.seek(0)

        st.download_button(
            label="📥 Exportar Simulação em Excel (.xlsx)",
            data=output_excel,
            file_name=f"Simulacao_{proposta_selecionada.replace('/', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_exp2:
        if REPORTLAB_DISPONIVEL:
            pdf_bytes = gerar_pdf_simulador(proposta_selecionada, cliente_atual, df_simulacao_completo, valor_total_geral)
            if pdf_bytes:
                st.download_button(
                    label="📄 Gerar PDF da Simulação",
                    data=pdf_bytes,
                    file_name=f"Simulacao_{proposta_selecionada.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
