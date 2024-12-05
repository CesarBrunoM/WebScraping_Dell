import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
from df_tags import ler_dataframe, salvar_dataframe

# Configura o logger para registrar as informações do processo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def setup_driver():
    """
    Configura e retorna uma instância do WebDriver com as opções desejadas.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("Driver configurado e iniciado.")
    return driver

def navigate_to_support_page(driver, service_tag):
    """
    Navega até a página de suporte da Dell e realiza a pesquisa pela tag de serviço.
    """
    try:
        handle_modal_popup(driver)        
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'mh-search-input'))
        )
        tag_input = driver.find_element(By.ID, 'mh-search-input')
        tag_input.send_keys(service_tag)
        tag_input.send_keys(Keys.RETURN)
        logger.info(f"Navegação para a tag de serviço {service_tag} realizada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao navegar até a página de suporte: {e}")
        raise RuntimeError(f"Erro ao navegar até a página de suporte: {e}")

def handle_survey_popup(driver):
    """
    Fecha o pop-up de pesquisa, se estiver presente.
    """
    try:
        iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "iframeSurvey"))
        )
        driver.switch_to.frame(iframe)
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[id="noButtonIPDell"]'))
        )
        close_button.click()
        driver.switch_to.default_content()
        logger.info("Pop-up de pesquisa fechado.")
    except Exception:
        logger.info("Pop-up de pesquisa não apareceu ou foi ignorado.")
        
def handle_modal_popup(driver):
    """
    Fecha o modal de garantia, caso ele esteja presente.
    """
    try:
        # Espera até que o modal esteja visível
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'warrantyDetailsPopup'))  # Modal com o ID 'warrantyDetailsPopup'
        )
        
        # Encontrando o botão de fechar do modal (geralmente o botão tem a classe 'close' ou algum outro identificador)
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'warranty-cancel'))  # Ajuste caso o botão tenha uma classe específica
        )
        close_button.click()
        logging.info("Modal de garantia fechado com sucesso.")
        
    except Exception as e:
        # Caso o modal não apareça ou qualquer outro erro
        logging.warning(f"Erro ao tentar fechar o modal de garantia: {e}")
        

def click_support_link(driver, tag):
    """
    Clica no link de suporte adequado (Suporte básico, ProSupport, Gerenciar serviços).
    Caso não consiga clicar em nenhum, retorna None.
    """
    tipo_garantia = None
    links = [
        ("Suporte básico", "Suporte básico"),
        ("ProSupport", "ProSupport"),
        ("Gerenciar serviços", "ProSupport")
    ]
    
    for link_text, tipo in links:
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, link_text))
            ).click()
            tipo_garantia = tipo
            logger.info(f"Clicado no link de {tipo}.")
            break
        except TimeoutException:
            continue
        except Exception as e:
            logger.warning(f"Erro ao tentar clicar no link '{link_text}': {e}")
            continue
    
    if tipo_garantia is None:
        logger.error(f"Não foi possível encontrar o link de suporte para a tag {tag}.")
        return None
    
    return tipo_garantia

def extract_purchase_date(driver):
    """
    Extrai a data de compra e data de expiração da página usando BeautifulSoup.
    """
    meses = {
        "janeiro": "January", "fevereiro": "February", "março": "March",
        "abril": "April", "maio": "May", "junho": "June",
        "julho": "July", "agosto": "August", "setembro": "September",
        "outubro": "October", "novembro": "November", "dezembro": "December"
    }
    
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'dsk-purchaseDt'))
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'dsk-expirationDt'))
        )
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        purchase_date_element = soup.find(id='dsk-purchaseDt')
        expiration_date_element = soup.find(id='dsk-expirationDt')    
        
        if purchase_date_element and expiration_date_element:
            purchase_date = purchase_date_element.text.strip().lower()
            expiration_date = expiration_date_element.text.strip().lower()

            for mes_pt, mes_en in meses.items():
                purchase_date = purchase_date.replace(mes_pt, mes_en)
                expiration_date = expiration_date.replace(mes_pt, mes_en)

            purchase_date = datetime.strptime(purchase_date, "%B %d, %Y").strftime("%d/%m/%Y")
            expiration_date = datetime.strptime(expiration_date, "%B %d, %Y").strftime("%d/%m/%Y")
            
            logger.info("Datas de compra e expiração extraídas com sucesso.")
            return purchase_date, expiration_date
        else:
            logger.error("Data de compra ou expiração não encontrada.")
            return "Data não encontrada", "Data não encontrada"
    except Exception as e:
        logger.error(f"Erro ao extrair a data de compra: {e}")
        raise RuntimeError(f"Erro ao extrair a data de compra: {e}")

def main():
    arquivo_base = 'Arquivos_excel\\Lista_ativos.xlsx'
    destino_dataframe = 'Arquivos_excel\\'
    driver = setup_driver()
    driver.get('https://www.dell.com/support/home/pt-br')
    
    df = ler_dataframe(arquivo_base)    
    logger.info("Início da extração de dados.")
    
    try:
        for index, row in df.iterrows():
            tag = row['TAG']
            
            navigate_to_support_page(driver, tag)
            handle_survey_popup(driver)
            tipo_suporte = click_support_link(driver, tag)
            purchase_date, expiration_date = extract_purchase_date(driver) 
            
            df.at[index, 'TIPO_GARANTIA'] = tipo_suporte
            df.at[index, 'DATA_COMPRA'] = purchase_date
            df.at[index, 'DATA_FIM_GARANTIA'] = expiration_date
            logger.info(f"Tag {tag} processada com sucesso.")
                
        salvar_dataframe(df, destino_dataframe)
        logger.info("Dados salvos com sucesso.")
        
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()
        logger.info("Driver fechado.")

if __name__ == "__main__":
    main()
