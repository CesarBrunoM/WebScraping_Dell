from app import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro crítico na execução da aplicação: {e}")
