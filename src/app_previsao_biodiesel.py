# app_previsao_biodiesel.py 

import streamlit as st
import pickle
import pandas as pd
import datetime

with open('../outputs/modelo_biodiesel_final.pkl', 'rb') as f:
    artefatos = pickle.load(f)

modelo = artefatos['modelo']
lmbda = artefatos['lmbda']
variaveis_modelo = artefatos['variaveis_modelo']
todos_produtos = artefatos['todos_produtos']
todas_regioes = artefatos['todas_regioes']
tempo_min = artefatos['tempo_min']
tempo_max = artefatos['tempo_max']
produto_referencia = artefatos['produto_referencia']
regiao_referencia = artefatos['regiao_referencia']

st.title("Previsão de Produção de Biodiesel")
st.write("Modelo de regressão múltipla com transformação Box-Cox")

data_escolhida = st.date_input(
    "Mês/Ano de referência",
    value=datetime.date(2023, 8, 1),
    min_value=datetime.date(2017, 1, 1),
    max_value=datetime.date(2027, 12, 1),
    format="DD/MM/YYYY"
)

st.caption("💡 O dia selecionado não afeta a previsão — apenas mês e ano são "
           "considerados pelo modelo. Você pode escolher qualquer mês/ano, "
           "inclusive além de agosto/2023 (último mês observado nos dados de treino).")

tempo = (data_escolhida.year - 2017) * 12 + data_escolhida.month

produto = st.selectbox(
    "Produto (matéria-prima)", 
    options=['(categoria de referência)'] + todos_produtos
)

regiao = st.selectbox(
    "Região", 
    options=['(categoria de referência)'] + todas_regioes
)

# Avisos dinâmicos: aparecem só se a escolha não tiver coeficiente próprio no modelo
if produto != '(categoria de referência)' and f'produto_{produto}' not in variaveis_modelo:
    st.info(f"ℹ️ O produto **{produto}** não foi estatisticamente significante no modelo — "
            f"a previsão vai considerar o mesmo comportamento de **{produto_referencia}** "
            f"(a categoria usada como base de comparação).")

if regiao != '(categoria de referência)' and f'regiao_{regiao}' not in variaveis_modelo:
    st.info(f"ℹ️ A região **{regiao}** não foi estatisticamente significante no modelo — "
            f"a previsão vai considerar o mesmo comportamento de **{regiao_referencia}** "
            f"(a categoria usada como base de comparação).")

if tempo < tempo_min or tempo > tempo_max:
    st.warning(artefatos['aviso_extrapolacao'].format(tempo_min=tempo_min, tempo_max=tempo_max))

if st.button("Calcular Previsão"):
    entrada = {var: 0 for var in variaveis_modelo}
    entrada['tempo'] = tempo
    
    if produto != '(categoria de referência)':
        col_produto = f'produto_{produto}'
        if col_produto in entrada:
            entrada[col_produto] = 1
    
    if regiao != '(categoria de referência)':
        col_regiao = f'regiao_{regiao}'
        if col_regiao in entrada:
            entrada[col_regiao] = 1
    
    nova_obs = pd.DataFrame([entrada])
    pred_bc = modelo.predict(nova_obs).iloc[0]
    pred_original = (pred_bc * lmbda + 1) ** (1 / lmbda)
    
    st.success(f"### Previsão: {pred_original:,.2f} m³")
    st.caption(f"(Valor na escala Box-Cox: {pred_bc:.4f})")
    st.caption(artefatos['aviso_limitacao_modelo'])