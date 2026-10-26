# -*- coding: utf-8 -*-
"""
Mini-Projeto Avaliativo - Módulo 1 - Semana 07
Análise de Dados com Python [T9] - SENAI/SC
Aluna: Iriane Soares

Análise Exploratória de Dados (AED) da base "Varejo" (Kaggle):
https://www.kaggle.com/datasets/namespaiva/base-varejo/data

Como rodar:  python Miniprojeto_IrianeSoares_T9.py
(o arquivo "Base Varejo.csv" ou o "Base_Varejo.zip" precisa estar na pasta data/)

Dicionário das colunas (deduzido olhando os dados):
    DATA      -> data da compra (texto no formato dd/mm/aaaa)
    CO_ID     -> identificador da compra (número do cupom)
    CL_ID     -> identificador do cliente
    CL_GENERO -> gênero do cliente (F / M)
    CL_EC     -> estado civil do cliente (código de 1 a 5)
    CL_FHL    -> número de filhos do cliente
    CL_SEG    -> segmento / classe do cliente (A, B, C)
    PR_ID     -> identificador do produto
    PR_CAT    -> categoria do produto
    PR_NOME   -> nome do produto
"""

import csv
import os
import re
import zipfile
from datetime import datetime

import pandas as pd

PASTA_DADOS = "data"
ARQUIVO_CSV = os.path.join(PASTA_DADOS, "Base Varejo.csv")
ARQUIVO_ZIP = os.path.join(PASTA_DADOS, "Base_Varejo.zip")
ARQUIVO_LIMPO = os.path.join(PASTA_DADOS, "df_limpo.csv.gz")

# deixa o pandas mostrar todas as colunas no terminal
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)


def titulo(texto):
    """Só imprime um título bonitinho para separar as etapas no terminal."""
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


# =============================================================================
# SPRINT 1 - IMPORTAÇÃO DOS DADOS
# =============================================================================
titulo("SPRINT 1 - IMPORTAÇÃO DOS DADOS")

# Se o CSV não estiver na pasta, extraio do zip que baixei do Kaggle
if not os.path.exists(ARQUIVO_CSV):
    print("CSV não encontrado, extraindo do arquivo zip...")
    with zipfile.ZipFile(ARQUIVO_ZIP) as z:
        z.extract("Base Varejo.csv", PASTA_DADOS)

# Leitura com o módulo nativo csv (csv.DictReader).
# O arquivo usa ";" como separador e foi salvo em latin-1 (padrão do Excel).
# Cada linha vira um dicionário {coluna: valor}.
linhas = []
with open(ARQUIVO_CSV, encoding="latin-1", newline="") as arquivo:
    leitor = csv.DictReader(arquivo, delimiter=";")
    colunas_originais = leitor.fieldnames
    for linha in leitor:
        linhas.append(linha)

print("Colunas encontradas no cabeçalho:", colunas_originais)
print("Primeira linha lida pelo DictReader:", linhas[0])

# Passo a lista de dicionários para um DataFrame do pandas
df = pd.DataFrame(linhas, columns=colunas_originais)

print("\nNúmero de registros:", len(df))
print("Número de colunas:", len(df.columns))
print("\nTipos de dados (tudo veio como texto, porque o csv lê tudo como string):")
print(df.dtypes)
print("\nPrimeiras linhas:")
print(df.head())


# =============================================================================
# VERIFICAÇÃO DE PROBLEMAS NA BASE (antes de limpar)
# =============================================================================
titulo("VERIFICAÇÃO DE PROBLEMAS NA BASE")

# 1) Colunas sem nome: o cabeçalho termina com ";;;;" então aparecem colunas vazias
colunas_sem_nome = [c for c in df.columns if c is None or c.strip() == ""]
print("1) Colunas sem nome no cabeçalho:", len(colunas_sem_nome))

# 2) Valores nulos / vazios por coluna (string vazia também conta como nulo)
df = df.replace(r"^\s*$", None, regex=True)
print("\n2) Valores nulos por coluna:")
print(df.isna().sum())

# 3) Categorias inválidas: o Excel gravou "#N/D" (erro de PROCV) em vez da categoria
print("\n3) Categorias de produto encontradas:")
print(df["PR_CAT"].value_counts(dropna=False))
qtd_nd = (df["PR_CAT"] == "#N/D").sum()
print('Linhas com categoria "#N/D":', qtd_nd)

# 4) Linhas duplicadas (iguais em todas as colunas)
qtd_duplicadas = df.duplicated().sum()
print("\n4) Linhas duplicadas:", qtd_duplicadas)

# 5) Problema de acentuação nos nomes (ex.: "REFRIGERANTE LIMaO")
nomes_com_minuscula = df.loc[df["PR_NOME"].str.contains("[a-z]", regex=True, na=False), "PR_NOME"].unique()
print("\n5) Nomes de produto com letra minúscula (erro de acento):", list(nomes_com_minuscula))


# =============================================================================
# SPRINT 2 - TRANSFORMAÇÃO DE STRINGS, INTEGER, FLOAT E DATETIME
# =============================================================================
titulo("SPRINT 2 - TRANSFORMAÇÃO DE TIPOS")

# Removo as colunas sem nome (estão 100% vazias, não têm informação nenhuma)
df = df.drop(columns=colunas_sem_nome)
print("Colunas depois de remover as vazias:", list(df.columns))


def limpar_texto(valor):
    """Padroniza textos: tira espaços extras, deixa em maiúsculo e
    corrige o 'aO' que apareceu no lugar de 'ÃO' por erro de encoding."""
    if valor is None or pd.isna(valor):
        return None
    valor = str(valor).strip()
    valor = re.sub(r"\s+", " ", valor)      # vários espaços viram um só
    valor = re.sub(r"aO\b", "AO", valor)    # LIMaO -> LIMAO
    return valor.upper()


def limpar_inteiro(valor):
    """Deixa só os dígitos e converte para int. Se não sobrar nada, retorna None."""
    if valor is None or pd.isna(valor):
        return None
    so_numeros = re.sub(r"[^0-9]", "", str(valor))
    if so_numeros == "":
        return None
    return int(so_numeros)


def limpar_decimal(valor):
    """Converte texto em float aceitando vírgula como separador decimal (padrão BR).
    A base não tem coluna de valor em R$, mas deixei a função pronta caso precise."""
    if valor is None or pd.isna(valor):
        return None
    texto = re.sub(r"[^0-9,.-]", "", str(valor)).replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def converter_data(valor):
    """Converte a string 'dd/mm/aaaa' para datetime usando o módulo datetime.
    Se a data for inválida, retorna None (vira NaT no pandas)."""
    if valor is None or pd.isna(valor):
        return None
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y")
    except ValueError:
        return None


# Aplico as funções nas colunas certas
colunas_texto = ["CL_GENERO", "CL_SEG", "PR_CAT", "PR_NOME"]
colunas_inteiras = ["CO_ID", "CL_ID", "CL_EC", "CL_FHL", "PR_ID"]

for col in colunas_texto:
    df[col] = df[col].apply(limpar_texto)

for col in colunas_inteiras:
    df[col] = df[col].apply(limpar_inteiro).astype("Int64")  # Int64 aceita nulo

df["DATA"] = pd.to_datetime(df["DATA"].apply(converter_data))

print("\nTipos de dados depois da conversão:")
print(df.dtypes)
print("Exemplo de nome corrigido:", df.loc[df["PR_NOME"].str.contains("LIMAO", na=False), "PR_NOME"].unique())
print("Exemplo de float com vírgula -> limpar_decimal('12,50') =", limpar_decimal("12,50"))


# =============================================================================
# SPRINT 3 - LIMPEZA DE NULOS E DUPLICATAS
# =============================================================================
titulo("SPRINT 3 - LIMPEZA DE NULOS E DUPLICATAS")

# --- 3.1 Categorias vazias ou inválidas -> "Sem Categoria" (if/else) ---
def tratar_categoria(cat):
    if cat is None or pd.isna(cat) or cat in ("#N/D", "N/D", "NA", ""):
        return "Sem Categoria"
    else:
        return cat


df["PR_CAT"] = df["PR_CAT"].apply(tratar_categoria)
# O nome do produto também estava "#N/D" nessas linhas, então marco como desconhecido
df["PR_NOME"] = df["PR_NOME"].apply(lambda n: "PRODUTO NAO IDENTIFICADO" if n in (None, "#N/D") else n)
print('Linhas com "Sem Categoria":', (df["PR_CAT"] == "Sem Categoria").sum())

# --- 3.2 Nulos nas colunas numéricas / dimensões do cliente ---
# Escolha: para número de filhos e estado civil uso a MEDIANA (não é afetada
# por valores extremos e continua sendo um número inteiro). Não removo a linha
# porque perderia a compra inteira por causa de um dado cadastral.
# Para IDs e DATA não dá para "inventar" um valor, então se faltar eu removo a linha.
for col in ["CL_FHL", "CL_EC"]:
    qtd_nulos = df[col].isna().sum()
    if qtd_nulos > 0:
        mediana = int(df[col].median())
        df[col] = df[col].fillna(mediana)
        print(f"{col}: {qtd_nulos} nulos preenchidos com a mediana ({mediana})")
    else:
        print(f"{col}: nenhum nulo encontrado, não precisou imputar")

antes = len(df)
df = df.dropna(subset=["DATA", "CO_ID", "CL_ID", "PR_ID"])
print("Linhas removidas por falta de DATA ou ID:", antes - len(df))

print("\nNulos por coluna depois do tratamento:")
print(df.isna().sum())

# --- 3.3 Duplicatas ---
# Uma linha duplicada aqui = mesmo produto, na mesma compra, mesmo cliente e mesma data.
# Como a base não tem coluna de quantidade, antes de apagar eu guardo quantas
# vezes o item apareceu (coluna QTD), assim não perco a informação de volume.
df["QTD"] = df.groupby(list(df.columns), dropna=False)["PR_ID"].transform("size")
antes = len(df)
df = df.drop_duplicates()
print(f"\nDuplicatas removidas: {antes - len(df)} (o volume ficou guardado na coluna QTD)")
print("Registros depois da limpeza:", len(df))


# =============================================================================
# REGRAS DE NEGÓCIO - IDENTIFICADOR DA COMPRA E DATAS
# =============================================================================
titulo("REGRAS DE NEGÓCIO (CO_ID e DATA)")

# Regra: cada número de compra (CO_ID) deve pertencer a UM cliente e UMA data.
regra = df.groupby("CO_ID").agg(clientes=("CL_ID", "nunique"), datas=("DATA", "nunique"))
compras_invalidas = regra[(regra["clientes"] > 1) | (regra["datas"] > 1)]
if len(compras_invalidas) == 0:
    print("OK: todas as compras têm um único cliente e uma única data.")
else:
    print("Atenção! Compras com mais de um cliente ou data:", len(compras_invalidas))
    # separo esses registros para não misturar com os válidos
    df = df[~df["CO_ID"].isin(compras_invalidas.index)]

# Regra: cada cliente deve ter sempre o mesmo cadastro (gênero, filhos, segmento...)
cadastro = df.groupby("CL_ID")[["CL_GENERO", "CL_EC", "CL_FHL", "CL_SEG"]].nunique()
print("Clientes com cadastro inconsistente:", (cadastro > 1).any(axis=1).sum())

# Validação das datas
print("Data mais antiga:", df["DATA"].min().date())
print("Data mais recente:", df["DATA"].max().date())
print("Datas no futuro:", (df["DATA"] > datetime.now()).sum())

# Colunas auxiliares de data para os agrupamentos
df["ANO"] = df["DATA"].dt.year
df["MES"] = df["DATA"].dt.month

print("\nTotal de compras (CO_ID únicos):", df["CO_ID"].nunique())
print("Total de clientes (CL_ID únicos):", df["CL_ID"].nunique())
print("Total de produtos (PR_ID únicos):", df["PR_ID"].nunique())


# =============================================================================
# SPRINT 4 - ESTATÍSTICA DESCRITIVA (NÚMERO DE FILHOS - CL_FHL)
# =============================================================================
titulo("SPRINT 4 - ESTATÍSTICA DESCRITIVA: NÚMERO DE FILHOS")

# Importante: a base tem uma linha por ITEM comprado. Se eu calcular direto,
# clientes que compram muito "pesam" mais. Por isso calculo por CLIENTE
# (uma linha por cliente), que é o correto para uma característica do cliente.
clientes = df.drop_duplicates(subset="CL_ID")[["CL_ID", "CL_GENERO", "CL_EC", "CL_FHL", "CL_SEG"]]
filhos = clientes["CL_FHL"].astype(float)

estatisticas = {
    "Contagem": filhos.count(),
    "Média": filhos.mean(),
    "Mediana": filhos.median(),
    "Moda": filhos.mode()[0],
    "Desvio padrão": filhos.std(),
    "Mínimo": filhos.min(),
    "Q1 (25%)": filhos.quantile(0.25),
    "Q2 (50%)": filhos.quantile(0.50),
    "Q3 (75%)": filhos.quantile(0.75),
    "Máximo": filhos.max(),
}
print("Estatísticas por cliente (1 linha por cliente):")
for nome, valor in estatisticas.items():
    print(f"  {nome:<15}: {valor:.2f}")

print("\nDistribuição de clientes por número de filhos:")
print(clientes["CL_FHL"].value_counts().sort_index())

# Só para comparar: a mesma coluna olhando linha a linha (por item vendido)
print("\nComparação - describe() considerando todas as linhas de itens:")
print(df["CL_FHL"].astype(float).describe())


# =============================================================================
# PADRÕES DE AGRUPAMENTO (groupby / pivot_table)
# =============================================================================
titulo("PADRÕES DE AGRUPAMENTO")

# Agrupamento 1: gênero -> quantidade de itens, compras e clientes
por_genero = df.groupby("CL_GENERO").agg(
    itens=("QTD", "sum"),
    compras=("CO_ID", "nunique"),
    clientes=("CL_ID", "nunique"),
)
por_genero["itens_por_compra"] = (por_genero["itens"] / por_genero["compras"]).round(1)
print("1) Vendas por gênero:")
print(por_genero)

# Agrupamento 2: categoria x gênero (pivot_table)
cat_genero = pd.pivot_table(df, index="PR_CAT", columns="CL_GENERO", values="QTD",
                            aggfunc="sum", margins=True, margins_name="TOTAL")
cat_genero = cat_genero.sort_values("TOTAL", ascending=False)
print("\n2) Itens vendidos por categoria e gênero:")
print(cat_genero)

# Agrupamento 3: segmento do cliente -> compras e itens
por_segmento = df.groupby("CL_SEG").agg(
    clientes=("CL_ID", "nunique"),
    compras=("CO_ID", "nunique"),
    itens=("QTD", "sum"),
)
por_segmento["compras_por_cliente"] = (por_segmento["compras"] / por_segmento["clientes"]).round(1)
print("\n3) Compras por segmento:")
print(por_segmento)

# Agrupamento 4: número de filhos -> itens por compra
por_filhos = df.groupby("CL_FHL").agg(compras=("CO_ID", "nunique"), itens=("QTD", "sum"))
por_filhos["itens_por_compra"] = (por_filhos["itens"] / por_filhos["compras"]).round(1)
print("\n4) Itens por compra conforme o número de filhos:")
print(por_filhos)

# Agrupamento 5: compras por ano
por_ano = df.groupby("ANO").agg(compras=("CO_ID", "nunique"), itens=("QTD", "sum"))
print("\n5) Compras por ano:")
print(por_ano)

# Top 10 produtos mais vendidos
top_produtos = df.groupby("PR_NOME")["QTD"].sum().sort_values(ascending=False).head(10)
print("\n6) Top 10 produtos mais vendidos:")
print(top_produtos)


# =============================================================================
# SPRINT 5 - RELATÓRIO FINAL NO TERMINAL
# =============================================================================
titulo("SPRINT 5 - RELATÓRIO FINAL")

genero_top = por_genero["itens"].idxmax()
categoria_top = cat_genero.drop(index="TOTAL")["TOTAL"].idxmax()
segmento_top = por_segmento["compras"].idxmax()
ano_top = por_ano["compras"].idxmax()

print(f"Registros originais ............: {len(linhas)}")
print(f"Registros após limpeza .........: {len(df)}")
print(f"Duplicatas removidas ...........: {qtd_duplicadas}")
print(f'Linhas "Sem Categoria" .........: {qtd_nd}')
print(f"Compras / clientes / produtos ..: {df['CO_ID'].nunique()} / {df['CL_ID'].nunique()} / {df['PR_ID'].nunique()}")
print(f"Gênero que mais comprou ........: {genero_top}")
print(f"Categoria mais vendida .........: {categoria_top}")
print(f"Segmento com mais compras ......: {segmento_top}")
print(f"Ano com mais compras ...........: {ano_top}")
print(f"Média de filhos por cliente ....: {estatisticas['Média']:.2f} (moda = {estatisticas['Moda']:.0f})")

print("\nCONCLUSÕES:")
print(f"- O gênero {genero_top} concentra a maior parte dos itens vendidos, mas a média de itens por compra é parecida entre os gêneros.")
print(f"- {categoria_top} é de longe a categoria mais vendida; BEBIDAS, PET e ACESSORIOS têm pouca participação.")
print(f"- O segmento {segmento_top} faz a maioria das compras; o segmento A é o menor.")
print("- Mais da metade dos clientes não tem filhos (moda e mediana = 0), e ter filhos quase não muda o tamanho da cesta (~45 itens por compra).")
print(f"- {ano_top} foi o ano com mais compras; 2022 caiu, mas a base termina em 08/12/2022, então o ano está incompleto.")
print("- Problemas que continuam: não existe coluna de valor (R$) nem de quantidade original,")
print("  e as linhas 'Sem Categoria' (produto 107) não têm como ser recuperadas sem outra fonte.")

# Salvo a base limpa (compactada para caber no GitHub)
df.to_csv(ARQUIVO_LIMPO, index=False, sep=";", encoding="utf-8", compression="gzip")
print(f"\nBase limpa salva em: {ARQUIVO_LIMPO}")
