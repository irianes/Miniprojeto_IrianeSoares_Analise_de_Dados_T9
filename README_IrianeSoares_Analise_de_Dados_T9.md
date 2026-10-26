# Como rodar – Miniprojeto Iriane Soares (Análise de Dados T9)

## No VS Code (ou terminal)

1. Instale o pandas (se ainda não tiver):
   ```
   pip install pandas
   ```
2. Deixe a pasta `data/` com o arquivo `Base_Varejo.zip` (já está no repositório)
   ou com o `Base Varejo.csv` baixado do Kaggle.
3. Na pasta do projeto, rode:
   ```
   python Miniprojeto_IrianeSoares_T9.py
   ```
4. O resultado aparece no terminal e a base limpa é salva em `data/df_limpo.csv.gz`.

## No Google Colab

1. Faça upload do `Miniprojeto_IrianeSoares_T9.py` e crie a pasta `data/` com o `Base_Varejo.zip`.
2. Em uma célula, rode:
   ```
   !python Miniprojeto_IrianeSoares_T9.py
   ```

Leva uns 30 segundos para rodar (são 830 mil linhas).
