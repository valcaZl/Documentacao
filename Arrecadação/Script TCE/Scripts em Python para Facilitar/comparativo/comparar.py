import pandas as pd

arquivo_completo = 'LauroMullerCompleto.csv'
arquivo_corrigido = 'LauroMullerCorrigido.csv'

def normalizar(inscricao):
    if pd.isna(inscricao):
        return ""
    return (inscricao
            .replace('–', '-') 
            .replace('—', '-')  
            .replace('.', '')   
            .replace(' ', '')   
            .strip())

df_imoveis = pd.read_csv(arquivo_completo, sep=';', dtype=str)
df_dionisio = pd.read_csv(arquivo_corrigido, sep=';', dtype=str)

df_imoveis.columns = df_imoveis.columns.str.strip()
df_dionisio.columns = df_dionisio.columns.str.strip()

df_imoveis['inscricao_normalizada'] = df_imoveis['Inscrição imobiliária'].apply(normalizar)
df_dionisio['inscricao_normalizada'] = df_dionisio['Inscrição imobiliária'].apply(normalizar)

inscricoes_imoveis = set(df_imoveis['inscricao_normalizada'])
df_dionisio['esta_no_imoveis'] = df_dionisio['inscricao_normalizada'].apply(lambda x: x in inscricoes_imoveis)

faltantes = df_dionisio[df_dionisio['esta_no_imoveis'] == False]

faltantes.to_csv('inscricoes_faltantes.csv', sep=';', index=False, encoding='utf-8')

print("✅ Comparação concluída. Verifique o arquivo 'inscricoes_faltantes.csv'.")