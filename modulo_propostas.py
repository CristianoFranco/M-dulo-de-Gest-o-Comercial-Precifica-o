# Ao puxar o valor do serviço selecionado para adicionar na proposta:
categoria_servico = str(row_servico.get("Categoria", "")).strip().lower()

if categoria_servico == "seguro":
    # Permite ao usuário digitar livremente o percentual de seguro (ex: 0.30 ou 0.25)
    tarifa_inicial_proposta = 0.30  # ou valor padrão desejado em aberto
    passo_tarifa = 0.01
    formato_tarifa = "%.2f"
else:
    try:
        tarifa_inicial_proposta = float(str(row_servico.get("Tarifa (R$)", 0)).replace(",", "."))
    except Exception:
        tarifa_inicial_proposta = 0.0
    passo_tarifa = 0.01
    formato_tarifa = "%.2f"

# Campo interativo na tabela de itens inseridos da Proposta Rascunho:
tarifa_editavel = st.number_input(
    "Tarifa Editável (R$ / %)",
    value=tarifa_inicial_proposta,
    min_value=0.0,
    step=passo_tarifa,
    format=formato_tarifa,
    key=f"tarifa_proposta_{codigo_item}"
)
