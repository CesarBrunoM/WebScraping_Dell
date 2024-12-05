import os
import pandas as pd
import logging

# Configuração do logger para capturar informações de execução
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def ler_dataframe(caminho_excel):
    """
    Lê um arquivo Excel e retorna um DataFrame filtrado com base no comprimento da TAG.
    Apenas as TAGs com comprimento menor ou igual a 7 caracteres são incluídas.
    """
    try:
        # Lê o arquivo Excel
        dataframe = pd.read_excel(caminho_excel)
        logger.info(f"Arquivo {caminho_excel} carregado com sucesso.")

        # Cria o novo DataFrame e filtra as TAGs
        new_dataframe = pd.DataFrame({
            "ID_ITEM": dataframe['ID_ITEM'], 
            "TIPO": dataframe['TABLE'], 
            "TAG": dataframe['TAGSERVICO'] 
        })

        # Filtra as TAGs com comprimento <= 7 caracteres
        new_dataframe = new_dataframe[new_dataframe['TAG'].str.len() <= 7]

        logger.info(f"{len(new_dataframe)} registros encontrados com TAGs válidas (<=7 caracteres).")
        return new_dataframe

    except Exception as e:
        logger.error(f"Erro ao ler o arquivo Excel: {e}")
        raise RuntimeError(f"Erro ao ler o arquivo Excel: {e}")

def salvar_dataframe(dataframe, pasta_destino):
    """
    Salva o DataFrame em um arquivo Excel na pasta de destino especificada.
    Se a pasta não existir, ela será criada.
    """
    try:
        nome_arquivo = "Dados-garantia-dell.xlsx"
        # Verifica se a pasta de destino existe; se não, cria
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
            logger.info(f"Pasta de destino criada: {pasta_destino}")

        # Define o caminho completo do arquivo
        local_arquivo = os.path.join(pasta_destino, nome_arquivo)

        # Salva o DataFrame no formato Excel
        dataframe.to_excel(local_arquivo, index=False)
        logger.info(f"Arquivo salvo em: {local_arquivo}")
    
    except Exception as e:
        logger.error(f"Erro ao salvar o arquivo Excel: {e}")
        raise RuntimeError(f"Erro ao salvar o arquivo Excel: {e}")

