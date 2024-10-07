import streamlit as st
import pandas as pd
import boto3
import io

st.markdown(
    "<h1 style='color: blue;'><strong>Smart Mix</strong></h1>", unsafe_allow_html=True
)
st.markdown(
    "<h4 style='color: blue;'><strong>Informe a localização informada da loja a ser aberta:(Brick, Utc)</strong></h4>",
    unsafe_allow_html=True,
)

# Mock de inputs
# brick_input = 1032
# utc_input = 1500404000
# tamLoja_input = "G"
# regiao_input = "Região Sul"

col1, col2, col3, col4 = st.columns(4)

with col1:
    brick_input = st.number_input("Preencha com o Brick", placeholder="Brick", value = None, step = 1)

with col2:
    utc_input = st.number_input("Preencha com o Utc", placeholder="Utc", value = None, step = 1)

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
        ("Região Norte", "Região Nordeste", "Região Centro-Oeste", "Região Sudeste", "Região Sul"),
        index=None,
        placeholder="Sua região",
    )

st.write(brick_input, utc_input, tamLoja_input, regiao_input)

if st.button("Processamento dos dados"):
    # Configurações do S3
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

    # Criação do cliente S3
    session = boto3.Session(
        aws_access_key_id="AKIARRDSZWDIU3IOGCAW",
        aws_secret_access_key="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",
        region_name="us-east-2",
    )
    s3 = session.client("s3")


    # Função para download e leitura de arquivos do S3
    def baixar_arquivo_s3(nome_arquivo, tipo="excel"):
        st.write(f"Baixando arquivo: {nome_arquivo}...")  # Adicionando print
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=nome_arquivo)
            content = obj["Body"].read()
            st.write(f"Arquivo {nome_arquivo} baixado com sucesso!")  # Adicionando print

            if tipo == "excel":
                return pd.read_excel(io.BytesIO(content))
            elif tipo == "csv":
                return pd.read_csv(
                    io.StringIO(content.decode("utf-8")), sep=";", low_memory=False
                )
        except Exception as e:
            st.error(f"Erro ao baixar {nome_arquivo}: {e}")
            return None


    # Baixar e carregar os dados
    perfil_lojas = baixar_arquivo_s3(arquivos_s3["perfil_lojas"])
    iqvia_med = baixar_arquivo_s3(arquivos_s3["iqvia_med"])
    iqvia_naomed = baixar_arquivo_s3(arquivos_s3["iqvia_naomed"])
    iqvia_consolidado = pd.concat([iqvia_med, iqvia_naomed])

    close_up = baixar_arquivo_s3(arquivos_s3["close_up"], tipo="csv")
    sellout_julho = baixar_arquivo_s3(arquivos_s3["sellout_julho"], tipo="csv")
    fato_pcp = baixar_arquivo_s3(arquivos_s3["fato_pcp"], tipo="csv")
    cadastro_produtos = baixar_arquivo_s3(arquivos_s3["cadastro_produtos"], tipo="csv")

    # Ajuste de categorias no cadastro de produtos
    st.write("Ajustando categorias no cadastro de produtos...")  # Adicionando print
    cadastro_produtos["categoria_ajustada"] = cadastro_produtos.apply(
        lambda row: (
            row["classe_1"]
            if row["nec_1"] == "98 - NOT OTC                  "
            else row["nec_1"]
        ),
        axis=1,
    )
    st.write("Categorias ajustadas com sucesso!")  # Adicionando print


    # Função de classificação Pareto
    def pareto_classification(row):
        if row["cumulative_percentage"] <= 50:
            return "A"
        elif row["cumulative_percentage"] <= 80:
            return "B"
        else:
            return "C"


    # Função para gerar a classificação Pareto
    def df_pareto_func(df, col1, col2, col_unid):
        st.write("Gerando classificação Pareto...")  # Adicionando print
        # Agrupar por 'brick', 'categoria ajustada', e 'ean' e somar 'sum_unidade'
        pareto_out = df.groupby([col1, col2, "ean"])[col_unid].sum().reset_index()

        # Ordenar pelos valores de 'brick', 'categoria ajustada', e 'sum_unidade'
        pareto_out = pareto_out.sort_values(
            by=[col1, col2, col_unid], ascending=[True, True, False]
        )

        # Calcular a soma cumulativa de 'sum_unidade' para cada 'brick' e 'categoria ajustada'
        pareto_out["cumulative_sum"] = pareto_out.groupby([col1, col2])[col_unid].cumsum()

        # Calcular a porcentagem cumulativa
        pareto_out["cumulative_percentage"] = (
            pareto_out["cumulative_sum"]
            / pareto_out.groupby([col1, col2])[col_unid].transform("sum")
        ) * 100

        # Aplicar classificação Pareto
        pareto_out["pareto_classification"] = pareto_out.apply(
            pareto_classification, axis=1
        )

        st.write("Classificação Pareto gerada com sucesso!")  # Adicionando print
        return pareto_out


    # Filtrar perfil de lojas por tamanho e região
    st.write("Filtrando perfil de lojas...")  # Adicionando print
    perfil_lojas_filtrado = perfil_lojas[
        (perfil_lojas["tamanho_sigla"] == tamLoja_input)
        & (perfil_lojas["Região"] == regiao_input)
    ]
    st.write(
        f"Perfil de lojas filtrado: {len(perfil_lojas_filtrado)} registros encontrados."
    )  # Adicionando print

    # Verificar se o DataFrame está vazio
    if perfil_lojas_filtrado.empty:
        st.warning(
            "Nenhuma loja encontrada com o filtro aplicado (tamanho e região). Verifique os inputs."
        )
    else:
        st.write(
            perfil_lojas_filtrado.head()
        )  # Mostrar as primeiras linhas do DataFrame filtrado

    # Merge de classe social com cadastro de produtos e perfil de lojas (filtrado por região e tamanho)
    st.write(
        "Fazendo merge de classe social com cadastro de produtos..."
    )  # Adicionando print

    try:
        # Verificar se os DataFrames têm dados
        st.write(f"Tamanho do DataFrame 'sellout_julho': {sellout_julho.shape}")
        st.write(f"Tamanho do DataFrame 'cadastro_produtos': {cadastro_produtos.shape}")
        st.write(
            f"Tamanho do DataFrame 'perfil_lojas_filtrado': {perfil_lojas_filtrado.shape}"
        )
        
        # Verificar se as colunas de merge existem e têm dados
        st.write(
            f"Checando valores nulos em 'sellout_julho' para 'cod_barras': {sellout_julho['cod_barras'].isnull().sum()}"
        )
        st.write(
            f"Checando valores nulos em 'cadastro_produtos' para 'ean': {cadastro_produtos['ean'].isnull().sum()}"
        )
        st.write(
            f"Checando valores nulos em 'sellout_julho' para 'cnpj': {sellout_julho['cnpj'].isnull().sum()}"
        )
        st.write(
            f"Checando valores nulos em 'perfil_lojas_filtrado' para 'CNPJ': {perfil_lojas_filtrado['CNPJ'].isnull().sum()}"
        )

        # Realizar o primeiro merge entre 'sellout_julho' e 'cadastro_produtos'
        merge_classe_categoria = sellout_julho.merge(
            cadastro_produtos, left_on="cod_barras", right_on="ean", how="left"
        )

        # Realizar o segundo merge com 'perfil_lojas_filtrado'
        merge_classe_categoria = merge_classe_categoria.merge(
            perfil_lojas_filtrado, left_on="cnpj", right_on="CNPJ", how="left"
        )

        # Remover linhas onde o EAN é nulo
        ean_none_count = merge_classe_categoria["ean"].isnull().sum()
        if ean_none_count > 0:
            merge_classe_categoria = merge_classe_categoria[
                merge_classe_categoria["ean"].notnull()
            ]
            st.write(
                f"Linhas com EANs None removidas. Total de linhas restantes: {merge_classe_categoria.shape[0]}"
            )
        else:
            st.write("Nenhum EAN None encontrado.")

        st.write("Merge de classe social realizado com sucesso!")  # Adicionando print
    except Exception as e:
        st.error(f"Erro ao fazer merge de classe social: {e}")


    # Verifique os EANs após o merge
    st.write("EAN no primeiro merge:")
    st.write(merge_classe_categoria[["cod_barras", "ean"]].drop_duplicates())

    # Criar coluna combinada de UF e tamanho da loja
    try:
        merge_classe_categoria["uf_tam"] = (
            merge_classe_categoria["Região"] + merge_classe_categoria["tamanho_sigla"]
        )
        st.write("Coluna UF e tamanho da loja combinada com sucesso!")  # Adicionando print
    except Exception as e:
        st.error(f"Erro ao combinar UF e tamanho da loja: {e}")

    # Aplicar classificação Pareto no DataFrame de classe social filtrado por região e tamanho
    st.write(
        "Aplicando classificação Pareto no DataFrame de classe social..."
    )  # Adicionando print
    try:
        df_classe_categoria = df_pareto_func(
            merge_classe_categoria, "uf_tam", "categoria_ajustada", "sum_unidade"
        )
        st.write("Classificação Pareto aplicada com sucesso!")  # Adicionando print
    except Exception as e:
        st.error(f"Erro ao aplicar classificação Pareto no DataFrame de classe social: {e}")

    st.dataframe(df_classe_categoria)

    # Filtrar Brick e UTC com base nos inputs do usuário
    st.write("Filtrando Brick e UTC")
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
        df_utc_categoria_filtered = df_utc_categoria[df_utc_categoria["UTC"] == utc_input]
        st.write("Filtragem de Brick e UTC concluída com sucesso!")
    except Exception as e:
        st.error(f"Erro ao filtrar Brick e UTC: {e}")

    st.dataframe(df_brick_categoria_filtered)

    # Combinar DataFrames filtrados
    st.write("Combinando DataFrames filtrados")
    try:
        merged_df = df_brick_categoria_filtered.merge(
            df_utc_categoria_filtered, on="ean", how="inner", suffixes=("_brick", "_utc")
        ).merge(df_classe_categoria, on="ean", how="inner", suffixes=("_merged", "_classe"))
        st.write("DataFrames combinados com sucesso!")
        st.dataframe(merged_df)

    except Exception as e:
        st.error(f"Erro ao combinar DataFrames: {e}")

    # Selecionar colunas de saida e adicionar classificações de Pareto
    try:
        df_out = pd.DataFrame(
            columns=[
                "ean",
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification_classe",
            ]
        )
        df_out["ean"] = merged_df["ean"]
        df_out[
            [
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification_classe",
            ]
        ] = merged_df[
            [
                "pareto_classification_brick",
                "pareto_classification_utc",
                "pareto_classification",
            ]
        ]
    except Exception as e:
        st.error(f"Erro ao adicionar classificações de Pareto: {e}")


    st.write("Processo concluído com sucesso!")
    st.dataframe(df_out)
