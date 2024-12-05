import pandas as pd
import os


def ler_dataframe(caminho_excel):
    # Lê o arquivo Excel
    dataframe = pd.read_excel(caminho_excel)
    
    # Cria o novo DataFrame de forma eficiente
    new_dataframe = pd.DataFrame({
        "ID_ITEM": dataframe['ID_ITEM'], 
        "TIPO": dataframe['TABLE'], 
        "TAG": dataframe['TAGSERVICO'] 
    })
    
    new_dataframe = new_dataframe[new_dataframe['TAG'].str.len() <= 7]

    return new_dataframe

def salvar_dataframe(dataframe, pasta_destino):
    nome_arquivo="Dados-garantia-dell.xlsx"
    # Verifica se a pasta de destino existe; se não, cria
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Define o caminho completo do arquivo
    local_arquivo = os.path.join(pasta_destino, nome_arquivo)

    # Salva o DataFrame no formato Excel
    dataframe.to_excel(local_arquivo, index=False)

    print(f"Arquivo salvo em: {local_arquivo}")