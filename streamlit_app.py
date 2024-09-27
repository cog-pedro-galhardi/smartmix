import streamlit as st
import pandas as pd

# Titulo 
st.markdown("<h1 style='color: blue;'><strong>Smart Mix</strong></h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: blue;'><strong>Informe a localização informada da loja a ser aberta:(Brick, Utc)</strong></h4>", unsafe_allow_html=True)

# Colunas e Imputs Labels
col1, col2, col3, col4 = st.columns(4)

with col1:
    brick = st.text_input("Preencha com o Brick", placeholder="Brick")

with col2:
    utc = st.text_input("Preencha com o Utc", placeholder="Utc")
  
with col3:
    tamLoja = st.selectbox(
        "Tamanho de sua loja",
        ("P", "M", "G", "GG"),
        index=None,
        placeholder="Tamanho da loja",
    )

with col4:
    regiao = st.selectbox(
        "Selecionar sua Região:",
        ("Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"),
        index=None,
        placeholder="Sua região",
    )

# Funcao para poder armazenas as variaveis
def processar_dados(brick, utc, tamLoja, regiao):

    st.write("Dados armazenados:")
    st.write(f"Brick: {brick}, UTC: {utc}, Tamanho da Loja: {tamLoja}, Região: {regiao}")
    


# Botao para o processamento de dados
if st.button('Confirmar e Processar Dados'):
    processar_dados(brick, utc, tamLoja, regiao)
