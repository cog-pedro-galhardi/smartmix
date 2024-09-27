import streamlit as st
import pandas as pd
import boto3 as bt

st.markdown("""
    <style>
        .circle {
            height: 15px;
            width: 15px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 15px;  
        }
        .red { background-color: red; }
        .yellow { background-color: yellow; }
        .green { background-color: green; }
        .circle-container {
            position: absolute;
            display: flex; 
        }
        .logo {
            position: fixed; 
            bottom: 20px; 
            left: 20px; 
            width: 50px; 
            height: auto; 
        }

    </style>
    <div class='circle-container'>
        <div class='circle red'></div>
        <div class='circle yellow'></div>
        <div class='circle green'></div>
    </div>

""", unsafe_allow_html=True)

st.markdown("<h1 style='color: blue;'><strong>Smart Mix</strong></h1>", unsafe_allow_html=True)


st.markdown("<h4 style='color: blue;'><strong>Informe a localização informada da loja a ser aberta:(Brick, Utc)</strong></h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    brick = st.text_input("", placeholder="Brick", label_visibility='hidden')
    st.write(brick)

with col2:
    utc = st.text_input("", placeholder="Utc", label_visibility='hidden')
    st.write(utc)
    
with col3:
    tamLoja = st.selectbox(
    "Tamanho de sua loja",
    ("P", "M", "G", "GG"),
    index=None,
    placeholder="Tamanho da loja",
)

st.write("O tamanho da loja selecionada é:", tamLoja) 
    
with col4:
    regiao = st.selectbox(
    "Selecionar sua Região",
    ("Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"),
    index=None,
    placeholder="Sua região",
)

st.write("A sua região selecionada é:", regiao)  


st.markdown("<img class='logo' src='logo.png' alt='Logo'>", unsafe_allow_html=True)
