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

if st.button("Processamento dos dados"):

    bucket_name = "smartmixfarpoc"
    arquivos_s3 = {
        "perfil_lojas": "Perfil lojas tratado.xlsx",
        "iqvia_med": "IQVIA PCP_MEDICAMENTO - tratado.xlsx",
        "iqvia_naomed": "IQVIA PCP_NÃO MEDICAMENTO - tratado.xlsx",
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
            st.write(f"Arquivo {local_file_path} já existe localmente.")

        if tipo == "excel":
            return pd.read_excel(local_file_path)
        elif tipo == "csv":
            return pd.read_csv(local_file_path, sep=";", low_memory=False)

    if not os.path.exists("data"):
        os.makedirs("data")

    progress = st.progress(0)

    # conectando com a AWS
    load_dotenv()
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
    )
    s3 = session.client("s3")

    total_etapas = len(arquivos_s3)
    progress_contador = 0

    perfil_lojas = baixar_arquivo_s3(
        arquivos_s3["perfil_lojas"], "data/perfil_lojas.xlsx"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    iqvia_med = baixar_arquivo_s3(arquivos_s3["iqvia_med"], "data/iqvia_med.xlsx")
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    iqvia_naomed = baixar_arquivo_s3(
        arquivos_s3["iqvia_naomed"], "data/iqvia_naomed.xlsx"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

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

    fato_pcp = baixar_arquivo_s3(
        arquivos_s3["fato_pcp"], "data/fato_pcp.csv", tipo="csv"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    cadastro_produtos = baixar_arquivo_s3(
        arquivos_s3["cadastro_produtos"], "data/cadastro_produtos.csv", tipo="csv"
    )
    progress_contador += 1
    progress.progress(progress_contador / total_etapas)

    # funcao para download e leitura de arquivos do S3
    # def baixar_arquivo_s3(nome_arquivo, tipo="excel"):
    #     try:
    #         obj = s3.get_object(Bucket=bucket_name, Key=nome_arquivo)
    #         content = obj["Body"].read()

    #         if tipo == "excel":
    #             return pd.read_excel(io.BytesIO(content))
    #             progress.progress(1 / total_etapas)

    #         elif tipo == "csv":
    #             return pd.read_csv(
    #                 io.StringIO(content.decode("utf-8")), sep=";", low_memory=False
    #             )
    #             progress.progress(2 / total_etapas)

    #     except Exception as e:
    #         st.error(f"Erro ao baixar {nome_arquivo}: {e}")
    #         return None

    # total_etapas = 9
    # progress.progress(3 / total_etapas)

    # # baixar e carregar os dados do bucket
    # perfil_lojas = baixar_arquivo_s3(arquivos_s3["perfil_lojas"])
    # iqvia_med = baixar_arquivo_s3(arquivos_s3["iqvia_med"])
    # iqvia_naomed = baixar_arquivo_s3(arquivos_s3["iqvia_naomed"])
    # iqvia_consolidado = pd.concat([iqvia_med, iqvia_naomed])
    # close_up = baixar_arquivo_s3(arquivos_s3["close_up"], tipo="csv")
    # sellout_julho = baixar_arquivo_s3(arquivos_s3["sellout_julho"], tipo="csv")
    # fato_pcp = baixar_arquivo_s3(arquivos_s3["fato_pcp"], tipo="csv")
    # cadastro_produtos = baixar_arquivo_s3(arquivos_s3["cadastro_produtos"], tipo="csv")

    # progress.progress(4 / total_etapas)

    # ajustar as categorias no cadastro de produtos
    cadastro_produtos["categoria_ajustada"] = cadastro_produtos.apply(
        lambda row: (
            row["classe_1"]
            if row["nec_1"] == "98 - NOT OTC                  "
            else row["nec_1"]
        ),
        axis=1,
    )

    # progress.progress(5 / total_etapas)

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

    # progress.progress(6 / total_etapas)

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

    # progress.progress(7 / total_etapas)

    # feiltrar os perfis por tamanho e regiao
    perfil_lojas_filtrado = perfil_lojas[
        (perfil_lojas["tamanho_sigla"] == tamLoja_input)
        & (perfil_lojas["Região"] == regiao_input)
    ]

    colunas_para_excluir = [
        "CD_GEOCODI",
        "CD_GEOCODM",
        "layer",
        "fid",
    ]  # Exemplo de colunas
    perfil_lojas_filtrado = perfil_lojas_filtrado.drop(columns=colunas_para_excluir)

    # Exibir o número de registros filtrados
    st.write(
        f"Perfil de lojas filtrado: {len(perfil_lojas_filtrado)} registros encontrados."
    )
    st.dataframe(perfil_lojas_filtrado)

    # verificar se o data frame esta vazio
    if perfil_lojas_filtrado.empty:
        st.warning(
            "Nenhuma loja encontrada com o filtro aplicado (tamanho e região). Verifique os inputs."
        )
    else:
        merge_classe_categoria = sellout_julho.merge(
            cadastro_produtos, left_on="cod_barras", right_on="ean", how="left"
        )

        # merge com 'perfil_lojas_filtrado'
        merge_classe_categoria = merge_classe_categoria.merge(
            perfil_lojas_filtrado, left_on="cnpj", right_on="CNPJ", how="left"
        )
        (merge_classe_categoria[["cod_barras", "ean"]].drop_duplicates())

        # juntar tamanho e loja em uma coluna
        try:
            merge_classe_categoria["uf_tam"] = (
                merge_classe_categoria["Região"]
                + merge_classe_categoria["tamanho_sigla"]
            )
        except Exception as e:
            st.error(f"Erro ao combinar UF e tamanho da loja: {e}")

        # classificação pareto no dataFrame filtrado por regiao e tamanho
        try:
            df_classe_categoria = df_pareto_func(
                merge_classe_categoria, "uf_tam", "categoria_ajustada", "sum_unidade"
            )
        except Exception as e:
            st.error(
                f"Erro ao aplicar classificação Pareto no DataFrame de classe social: {e}"
            )

    # filtro de brick e utc
    merge_brick_categoria = fato_pcp.merge(
        cadastro_produtos, left_on="ean", right_on="ean", how="left"
    )
    df_brick_categoria = df_pareto_func(
        merge_brick_categoria, "brick", "categoria_ajustada", "sum_unidade"
    )
    merge_utc_categoria = close_up.merge(
        cadastro_produtos, left_on="EAN", right_on="ean", how="left"
    )
    df_utc_categoria = df_pareto_func(
        merge_utc_categoria, "UTC", "categoria_ajustada", "RK UTC (UND.)"
    )
    try:
        df_brick_categoria_filtered = df_brick_categoria[
            df_brick_categoria["brick"] == brick_input
        ]
        df_utc_categoria_filtered = df_utc_categoria[
            df_utc_categoria["UTC"] == utc_input
        ]
    except Exception as e:
        st.error(f"Erro ao filtrar Brick e UTC: {e}")
    # juntar os dataFrames
    try:
        merged_df = (
            df_brick_categoria_filtered.merge(
                df_utc_categoria_filtered,
                on="ean",
                how="outer",
                suffixes=("_brick", "_utc"),
            )
            .merge(
                df_classe_categoria,
                on="ean",
                how="outer",
                suffixes=("_merged", "_classe"),
            )
            .merge(
                cadastro_produtos[["ean", "produto", "categoria_ajustada"]],
                on="ean",
                how="outer",
            )
        )
        merged_df["categoria_ajustada"] = (
            merged_df["categoria_ajustada_brick"]
            .combine_first(merged_df["categoria_ajustada_utc"])
            .combine_first(merged_df["categoria_ajustada_x"])
            .combine_first(merged_df["categoria_ajustada_y"])
        )
        merged_df = merged_df.drop(
            [
                "categoria_ajustada_brick",
                "categoria_ajustada_utc",
                "categoria_ajustada_x",
                "categoria_ajustada_y",
            ],
            axis=1,
        )
        merged_df["pareto_classification_brick"] = df_brick_categoria_filtered[
            "pareto_classification"
        ]
        merged_df["pareto_classification_utc"] = df_utc_categoria_filtered[
            "pareto_classification"
        ]
        merged_df["pareto_classification_uf_tam"] = df_classe_categoria[
            "pareto_classification"
        ]

    except Exception as e:
        st.error(f"Erro ao combinar DataFrames: {e}")

    # progress.progress(8 / total_etapas)

    brick_filter_list = ["A", "B"]
    utc_filter_list = ["A", "B"]
    uftam_filter_list = ["A", "B"]

    # func para definir se recomenda o produto se ele for A ou em tanto em iqivia, close-up ou tamanho/regiao

    def recomendar_func(row, brick_filter_list, utc_filter_list, uftam_filter_list):
        if (
            row["pareto_classification_brick"] in brick_filter_list
            or row["pareto_classification_utc"] in utc_filter_list
            or row["pareto_classification_uf_tam"] in uftam_filter_list
        ):
            return "Sim"
        else:
            return "Não"

    try:
        df_out = pd.DataFrame(
            columns=[
                "ean",
                "medicamentos",
                "grupo do produto",
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification_uf_tam",
                "Recomendar",
            ]
        )

        df_out["ean"] = merged_df["ean"]
        df_out["medicamentos"] = merged_df["produto"]
        df_out["grupo do produto"] = merged_df["categoria_ajustada"]
        df_out[
            [
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification_uf_tam",
            ]
        ] = merged_df[
            [
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification_uf_tam",
            ]
        ]
        df_out["Recomendar"] = df_out.apply(
            lambda row: recomendar_func(
                row, brick_filter_list, utc_filter_list, uftam_filter_list
            ),
            axis=1,
        )

        st.dataframe(df_out)

    except Exception as e:
        st.error(f"Erro ao adicionar classificações de Pareto: {e}")

    # progress.progress(9 / total_etapas)

    st.write("Processamento concluído!")
    # progress.empty()

    csv = df_out.to_csv(index=False)

    # botao para download
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="dados_processados.csv",
        mime="text/csv",
    )
st.markdown("</div>", unsafe_allow_html=True)


# colocar nome do produto, e puxar dado do "cadastro do produto"
# coluna de categoria ajustada no df_out
# Ordem das colunas:
# Código de EAN
# nome do produto
# Grupo do produto
# pareto classificação Brick
# Pareto classificação utc
# Pareto classificação classe

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

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


# pegar a base de vendas, G, SUL e fazer o pareto desse cara no excel, fazer um pareto por categoria, fazer uma soma
