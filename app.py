from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import locale
from df_tags import ler_dataframe

# locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

def setup_driver():
    """
    Configura e retorna uma instância do WebDriver com as opções desejadas.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def navigate_to_support_page(driver, service_tag):
    """
    Navega até a página de suporte da Dell e realiza a pesquisa pela tag de serviço.
    """
    try:
        # driver.get('https://www.dell.com/support/home/pt-br')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'mh-search-input'))
        )
        tag_input = driver.find_element(By.ID, 'mh-search-input')
        tag_input.send_keys(service_tag)
        tag_input.send_keys(Keys.RETURN)
    except Exception as e:
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
    except Exception:
        pass  # Ignorar se o pop-up não aparecer

def click_support_link(driver, tag):
    """
    Clica no link de suporte básico para acessar a página de detalhes da garantia.
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Suporte básico"))
        ).click()
    except TimeoutException as e:  # Se for uma exceção de timeout
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "ProSupport"))
        ).click()
    except Exception as e:  # Para qualquer outro tipo de exceção
        print(f"Erro inesperado ao clicar no link de suporte básico: {e}")
        navigate_to_support_page(driver, tag)
        #raise RuntimeError(f"Erro ao clicar no link de suporte básico: {e}")

def extract_purchase_date(driver):
    """
    Extrai a data de compra da página usando BeautifulSoup.
    """
    meses = {
    "janeiro": "January", "fevereiro": "February", "março": "March",
    "abril": "April", "maio": "May", "junho": "June",
    "julho": "July", "agosto": "August", "setembro": "September",
    "outubro": "October", "novembro": "November", "dezembro": "December"
    }
    
    try:
        # Espera até que o elemento com o ID da data de compra esteja visível
        purchase_date_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'dsk-purchaseDt'))
        )
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        purchase_date_element = soup.find(id='dsk-purchaseDt')
        
        if purchase_date_element:
            purchase_date = purchase_date_element.text.strip()
            
            for mes_pt, mes_link in meses.items():
                purchase_date = purchase_date.replace(mes_pt,mes_link)
            
            return datetime.strptime(purchase_date, "%B %d, %Y").strftime("%d/%m/%Y")
        else:
            return "Data não encontrada"
    except Exception as e:
        raise RuntimeError(f"Erro ao extrair a data de compra: {e}")

def main():
    service_tag = '1035Q34'
    local_arquivo = 'Arquivo_excel\\Lista_ativos.xlsx'
    driver = setup_driver()
    driver.get('https://www.dell.com/support/home/pt-br')
    
    df = ler_dataframe(local_arquivo)
    
    df['DATA_COMPRA'] = None

    try:
        for index, row in df.iterrows():
            tag = row['TAG']
            
            navigate_to_support_page(driver, tag)
            handle_survey_popup(driver)
            click_support_link(driver, tag)
            purchase_date = extract_purchase_date(driver)
            
            #print(f'Data de compra: {purchase_date}')
            print(df)
            df.at[index, 'DATA_COMPRA'] = purchase_date
        #print(df)
                
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
