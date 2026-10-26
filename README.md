# Mini-Projeto Avaliativo – Análise Exploratória da Base Varejo

**Curso:** Análise de Dados com Python [T9] – SENAI/SC (Módulo 1 – Semana 07)
**Aluna:** Iriane Soares

Neste projeto fiz uma Análise Exploratória de Dados (AED) usando a base Varejo do Kaggle, com cerca de 830 mil linhas de compras entre 2019 e 2022. A ideia era entender o que tinha nesses dados, encontrar os problemas, limpar a base, calcular estatísticas sobre a quantidade de filhos dos clientes e procurar alguns padrões de comportamento.

## Arquivos

- `Miniprojeto_IrianeSoares_T9.py`: script com toda a análise, comentado e dividido pelas etapas (sprints).
- `data/Base_Varejo.zip`: base original do Kaggle. Fica zipada e o código descompacta na hora de rodar.
- `data/df_limpo.csv.gz`: base final depois da limpeza, compactada e separada por ponto e vírgula.
- `saida_terminal.txt`: resultado completo que o script mostra no terminal.
- `README_IrianeSoares_Analise_de_Dados_T9.md`: passo a passo para rodar o projeto.

Colunas da base: `DATA`, `CO_ID` (código da compra), `CL_ID` (código do cliente), `CL_GENERO`, `CL_EC` (estado civil), `CL_FHL` (quantidade de filhos), `CL_SEG` (segmento A/B/C), `PR_ID`, `PR_CAT` e `PR_NOME` (dados do produto).

## Como eu fiz (sprints)

1. **Importação:** li o CSV original com `csv.DictReader` (abrindo o arquivo com encoding latin-1) e passei tudo para um DataFrame.
2. **Ajuste de tipos:** usei expressões regulares (regex) para tratar textos, inteiros e decimais. A data estava em formato de texto, então converti com `datetime.strptime`.
3. **Nulos e duplicadas:** algumas categorias estavam vazias ou com "#N/D", então troquei por "Sem Categoria". Nas colunas dos clientes deixei pronto um código que preenche dados vazios com a mediana. Também removi as duplicatas.
4. **Estatísticas:** calculei para a coluna de filhos a média, mediana, moda, desvio padrão, mínimo, máximo, contagem e quartis.
5. **Relatório:** usei `groupby()` e `pivot_table()` para os agrupamentos e imprimi um resumo no terminal.
6. **Versionamento:** fui subindo os arquivos para o GitHub aos poucos.

## Problemas encontrados nos dados

- Havia 4 colunas vazias no final do arquivo, que excluí.
- Mais de 3.600 linhas tinham a categoria "#N/D" (parece erro de PROCV do Excel, e era tudo do produto 107). Mudei para "Sem Categoria".
- O maior problema: quase 100 mil linhas duplicadas, com o mesmo produto, na mesma compra, para o mesmo cliente e na mesma data. Para não perder o volume de vendas, criei uma coluna `QTD` (quantidade) antes de remover as repetições.
- Havia erro de acentuação, como "REFRIGERANTE LIMaO", que corrigi com regex.
- Validei uma regra de negócio: cada código de compra (`CO_ID`) só pode ter um cliente e uma data. Deu certo nas 18.471 compras.
- Nas colunas do cliente (como número de filhos), se viesse algum valor nulo, o código usaria a mediana. Preferi a mediana à média porque ela sofre menos com valores extremos e devolve um número inteiro. Linhas sem ID ou sem data seriam removidas, porque não faz sentido inventar um código de compra.

## Estatísticas – número de filhos

Calculei as métricas para os 1.000 clientes, agrupando por cliente e não linha a linha. Se usasse a base inteira, quem compra com mais frequência apareceria mais vezes e distorceria as médias.

| Clientes | Média | Mediana | Moda | Desvio padrão | Mín | Q1 | Q3 | Máx |
|---|---|---|---|---|---|---|---|---|
| 1000 | 1,14 | 0 | 0 | 1,41 | 0 | 0 | 2 | 4 |

## Insights

- **Alimentos:** mais da metade dos itens vendidos (52%) são alimentos. Higiene e limpeza vêm logo atrás. Bebidas, pet e acessórios vendem pouco.
- **Homens x mulheres:** as mulheres compraram mais itens no total (432 mil contra 397 mil), mas só porque há mais mulheres na base. O tamanho da compra é praticamente igual para os dois (cerca de 45 itens).
- **Segmento B:** é o maior público (64% das compras). O segmento A é o menor.
- **Filhos:** a maioria dos clientes (52,7%) não tem filhos, e ter filhos ou não quase não muda o volume da compra.
- **2022:** 2021 foi o ano com mais compras. 2022 parece ter uma queda grande, mas a base termina em 08/12/2022, então o ano está incompleto.
- **O que ficou faltando:** a base não tem coluna de valor em reais nem de quantidade original, então não dá para calcular faturamento. E o produto 107 continuou sem nome.

## Reflexão final – ETL e qualidade de dados

Esse projeto foi um processo de ETL em escala menor:

- **Extract:** pegar os dados brutos e lidar com a formatação e o encoding.
- **Transform:** padronizar, limpar textos, guardar as quantidades antes de apagar as duplicadas e verificar se os dados faziam sentido.
- **Load:** salvar o arquivo limpo, pronto para ser usado em um Power BI, por exemplo.

Deu para ver na prática o quanto a qualidade dos dados muda o resultado. Se eu não tivesse tratado as duplicatas, a análise mostraria um volume de itens maior do que o real. Se não ajustasse as datas, não daria para analisar por ano.

Trabalhei com as dimensões de completude (colunas vazias), validade (#N/D e datas em texto) e unicidade (duplicatas). A principal lição foi que limpar dados não é só apagar o que está errado: cada escolha, como agrupar duplicatas em quantidade ou usar a mediana no lugar da média, muda o número final. Toda alteração precisa ter uma justificativa.
