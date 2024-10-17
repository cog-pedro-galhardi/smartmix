import streamlit as st
import pandas as pd
import boto3
import io
import os
from dotenv import load_dotenv


st.markdown(
    """
    <style>

    div.stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    
    div.stDownloadButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }

    div.stDownloadButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(
    "<h1 style='color: blue;'><strong>Smart Mix</strong></h1>", unsafe_allow_html=True
)
st.markdown(
    "<h4 style='color: blue;'><strong>Informe a localização informada da loja a ser aberta:</strong></h4>",
    unsafe_allow_html=True,
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    brick_input = st.number_input(
        "Preencha com o Brick", placeholder="Brick", value=None, step=1
    )

with col2:
    utc_input = st.number_input(
        "Preencha com o Utc", placeholder="Utc", value=None, step=1
    )

with col3:
    tamLoja_input = st.selectbox(
        "Tamanho de sua loja",
        ("P", "M", "G", "GG"),
        index=None,
        placeholder="Tamanho da loja",
    )

with col4:
    regiao_input = st.selectbox(
        "Selecionar sua Região:",
        (
            "Região Norte",
            "Região Nordeste",
            "Região Centro-Oeste",
            "Região Sudeste",
            "Região Sul",
        ),
        index=None,
        placeholder="Sua região",
    )

# Mock de inputs
# brick_input = 1032
# utc_input = 1500404000
# tamLoja_input = "G"
# regiao_input = "Região Sul"

# st.write(brick_input, utc_input, tamLoja_input, regiao_input)


if st.button("Processar dados"):

    # ajustar as categorias no cadastro de produtos
    bucket_name = "smartmixfarpoc"
    arquivos_s3 = {
        "perfil_lojas": "Perfil lojas tratado.xlsx",
        # "iqvia_med": "IQVIA PCP_MEDICAMENTO - tratado.xlsx",
        # "iqvia_naomed": "IQVIA PCP_NÃO MEDICAMENTO - tratado.xlsx",
        "close_up": "utcs_concatenados.csv",
        "sellout_julho": "sellout.ft_venda_202407_202408261021.csv",
        "fato_pcp": "fato_pcp_cubo_farmarcas_iqvia_202409192107.csv",
        "cadastro_produtos": "cadastro_produtos_iqvia_202409192057.csv",
    }
    # progress = st.progress(0)

    def baixar_arquivo_s3(nome_arquivo, local_file_path, tipo="excel"):
        if not os.path.exists(local_file_path):
            try:
                obj = s3.get_object(Bucket=bucket_name, Key=nome_arquivo)
                content = obj["Body"].read()
                with open(local_file_path, "wb") as file:
                    file.write(content)
            except Exception as e:
                st.error(f"Erro ao baixar {nome_arquivo}: {e}")
                return None
        else:
            st.write("")

        if tipo == "excel":
            return pd.read_excel(local_file_path)
        elif tipo == "csv":
            return pd.read_csv(local_file_path, sep=";", low_memory=False)

    if not os.path.exists("data"):
        os.makedirs("data")

    progress = st.progress(0)

    #load_dotenv()

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
    )
    s3 = session.client("s3")

    total_etapas = 14
    progress_contador = 0

    perfil_lojas = baixar_arquivo_s3(
        arquivos_s3["perfil_lojas"], "data/perfil_lojas.xlsx"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # iqvia_med = baixar_arquivo_s3(arquivos_s3["iqvia_med"], "data/iqvia_med.xlsx")
    # progress_contador += 1
    # progress.progress(progress_contador / total_etapas)

    # iqvia_naomed = baixar_arquivo_s3(
    #    arquivos_s3["iqvia_naomed"], "data/iqvia_naomed.xlsx"
    # )
    # progress_contador += 1
    # progress.progress(progress_contador / total_etapas)

    close_up = baixar_arquivo_s3(
        arquivos_s3["close_up"], "data/close_up.csv", tipo="csv"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    sellout_julho = baixar_arquivo_s3(
        arquivos_s3["sellout_julho"], "data/sellout_julho.csv", tipo="csv"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    iqvia = baixar_arquivo_s3(arquivos_s3["fato_pcp"], "data/fato_pcp.csv", tipo="csv")
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    cadastro_produtos = baixar_arquivo_s3(
        arquivos_s3["cadastro_produtos"], "data/cadastro_produtos.csv", tipo="csv"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    cadastro_produtos["categoria_ajustada"] = cadastro_produtos.apply(
        lambda row: (
            row["classe_1"]
            if row["nec_1"] == "98 - NOT OTC                  "
            else row["nec_1"]
        ),
        axis=1,
    )

    # classificação Pareto
    def pareto_classification(row):
        if row["cumulative_percentage"] <= 50:
            return "A"
        elif row["cumulative_percentage"] <= 80:
            return "B"
        elif row["cumulative_percentage"] <= 90:
            return "C"
        else:
            return "D"

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # gerar a classificação Pareto
    def df_pareto_func(df, col1, col2, col_unid):

        pareto_out = df.groupby([col1, col2, "ean"])[col_unid].sum().reset_index()

        # ordenar pelos valores de 'brick', 'categoria ajustada', e 'sum_unidade'
        pareto_out = pareto_out.sort_values(
            by=[col1, col2, col_unid], ascending=[True, True, False]
        )

        # soma cumulativa de 'sum_unidade' para cada 'brick' e 'categoria ajustada'
        pareto_out["cumulative_sum"] = pareto_out.groupby([col1, col2])[
            col_unid
        ].cumsum()

        # porcentagem cumulativa
        pareto_out["cumulative_percentage"] = (
            pareto_out["cumulative_sum"]
            / pareto_out.groupby([col1, col2])[col_unid].transform("sum")
        ) * 100

        # classificacao de pareto
        pareto_out["pareto_classification"] = pareto_out.apply(
            pareto_classification, axis=1
        )

        return pareto_out

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # Relacionar fatos de UTC, BRICK e Sellout com as dimensoes de categoria, região e tamanho (no caso de sellout)

    sellout_categoria = sellout_julho.merge(
        cadastro_produtos, left_on="cod_barras", right_on="ean", how="left"
    )

    # unir com dimensao
    sellout_categoria = sellout_categoria.merge(
        perfil_lojas, left_on="cnpj", right_on="CNPJ", how="left"
    )

    iqvia_categoria = iqvia.merge(
        cadastro_produtos, left_on="ean", right_on="ean", how="left"
    )

    close_up_categoria = close_up.merge(
        cadastro_produtos, left_on="EAN", right_on="ean", how="left"
    )

    # Filtrar os fatos para os inputs dado

    sellout_categoria = sellout_categoria[
        (sellout_categoria["tamanho_sigla"] == tamLoja_input)
        & (sellout_categoria["Região"] == regiao_input)
    ]

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    iqvia_categoria = iqvia_categoria[(iqvia_categoria["brick"] == brick_input)]

    close_up_categoria = close_up_categoria[(close_up_categoria["UTC"]) == utc_input]

    # nova coluna para concatenar regiao e tamanho (nova chave de agrupamento)
    sellout_categoria.loc[:, "regiao_tam"] = (
        sellout_categoria["Região"] + "_" + sellout_categoria["tamanho_sigla"]
    )

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # Selecionar somente as colunas necessárias

    sellout_categoria = sellout_categoria[
        ["ean", "cnpj", "regiao_tam", "categoria_ajustada", "sum_unidade"]
    ]
    iqvia_categoria = iqvia_categoria[
        ["ean", "brick", "categoria_ajustada", "sum_unidade"]
    ]
    close_up_categoria = close_up_categoria[
        ["ean", "UTC", "categoria_ajustada", "MAT ATUAL UTC (UND.)"]
    ].rename(columns={"MAT ATUAL UTC (UND.)": "sum_unidade"})

    # Invocar função Pareto

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    pareto_sellout = df_pareto_func(
        sellout_categoria, "regiao_tam", "categoria_ajustada", "sum_unidade"
    )

    pareto_iqvia = df_pareto_func(
        iqvia_categoria, "brick", "categoria_ajustada", "sum_unidade"
    )

    pareto_close_up = df_pareto_func(
        close_up_categoria, "UTC", "categoria_ajustada", "sum_unidade"
    )

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # Unir os dataframes em um único

    merged_df = pareto_sellout.merge(
        pareto_iqvia,
        on="ean",
        how="outer",
        suffixes=("_sellout", "_iqvia"),
    )

    merged_df = merged_df.merge(
        pareto_close_up,
        on="ean",
        how="outer",
        suffixes=("_merged", "close_up"),
    ).rename(columns={"pareto_classification": "pareto_classification_close_up"})

    merged_df = merged_df.merge(
        cadastro_produtos,
        on="ean",
        how="left",
        suffixes=("_merged", "_cadastro"),
    )

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # Coluna de recomendacao conforme a regra de negócio

    sellout_filter_list = ["A", "B", "C"]
    brick_filter_list = ["A", "B"]
    utc_filter_list = ["A", "B", "C"]

    # func para definir se recomenda o produto se ele for A ou em tanto em iqivia, close-up ou tamanho/regiao
    def recomendar_func(row, brick_filter_list, utc_filter_list, sellout_filter_list):
        if (
            row["pareto_classification_iqvia"] in brick_filter_list
            or row["pareto_classification_close_up"] in utc_filter_list
            or row["pareto_classification_sellout"] in sellout_filter_list
        ):
            return "Sim"
        else:
            return "Não"

    merged_df["Recomendar"] = merged_df.apply(
        lambda row: recomendar_func(
            row, brick_filter_list, utc_filter_list, sellout_filter_list
        ),
        axis=1,
    )

    merged_df = merged_df[
        [
            "ean",
            "produto",
            "categoria_ajustada_cadastro",
            "pareto_classification_sellout",
            "pareto_classification_iqvia",
            "pareto_classification_close_up",
            "Recomendar",
        ]
    ]
    merged_df = merged_df.rename(
        columns={"categoria_ajustada_cadastro": "categoria_ajustada"}
    )

    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    st.write("Processamento concluído!")
    # progress.empty()
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    csv = merged_df.to_csv(index=False)

    # botao para download
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="dados_processados.csv",
        mime="text/csv",
    )

st.image(
    "farm.png", width=150, use_column_width="never", caption="", output_format="auto"
)

st.markdown(
    """
    <style>
    img {
        position: fixed;
        bottom: 20px;  /* Ajuste a distância do fundo */
        right: 20px;   /* Ajuste a distância do lado direito */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
