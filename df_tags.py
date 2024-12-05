import pandas as pd


import pandas as pd

def ler_dataframe(caminho_excel):
    # Lê o arquivo Excel
    dataframe = pd.read_excel(caminho_excel)
    
    # Cria o novo DataFrame de forma eficiente
    new_dataframe = pd.DataFrame({
        "ID_ITEM": dataframe['ID_ITEM'],  # Remove espaços em branco
        "TIPO": dataframe['TABLE'],  # Remove espaços e converte para maiúsculas
        "TAG": dataframe['TAGSERVICO']  # Apenas copia a coluna
    })
    
    new_dataframe = new_dataframe[new_dataframe['TAG'].str.len() <= 7]
        #f not len(tag_servico) > 7:
        #    taglist.append(tag_servico)
    
    return new_dataframe


def gravaarquivo(dataframe):
    pass