import logging
from app import main

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if __name__ == "__main__":
    try:
        # Executa a função principal do aplicativo
        main()
    except Exception as e:
        # Registra um erro crítico caso a execução da aplicação falhe
        logger.error(f"Erro crítico na execução da aplicação: {e}")
