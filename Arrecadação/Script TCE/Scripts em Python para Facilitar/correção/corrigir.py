import pandas as pd

# Lê o arquivo CSV
df = pd.read_csv("lauroMuller.csv", sep=None, engine="python")

# Remove espaços extras dos nomes das colunas
df.columns = df.columns.str.strip()

# Função para remover zeros à esquerda da última parte
def limpar_inscricao(inscricao):
    if pd.isna(inscricao):
        return inscricao
    partes = inscricao.split(".")
    if partes:
        partes[-1] = str(int(partes[-1]))  # remove zeros à esquerda
    return ".".join(partes)

# Aplica a função e substitui na própria coluna
df["Inscrição imobiliária"] = df["Inscrição imobiliária"].apply(limpar_inscricao)

# Salva o resultado em um novo arquivo
df.to_csv("LauroMullerCorrigido.csv", index=False, sep=";")