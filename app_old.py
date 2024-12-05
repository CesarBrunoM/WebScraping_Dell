from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

chrome_options = Options()

chrome_options.add_argument("--start-maximized")  # Iniciar maximizado
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Desabilitar detecção de automação
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.add_argument("--headless")  # Isso faz com que o navegador seja invisível

#chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Configuração do WebDriver
driver = webdriver.Chrome(options=chrome_options) 

try:
    # Acesse o site da Dell
    driver.get('https://www.dell.com/support/home/pt-br')

    # Aguarde a página carregar
    time.sleep(5)  

    # Localize o campo de entrada para a Tag de Serviço.
    tag_input = driver.find_element(By.ID,'mh-search-input')  # Inspecione o ID correto no site
 
    # Insere a tag de serviço no campo de pesquisa.
    service_tag = '1035Q34'
    tag_input.send_keys(service_tag)
    tag_input.send_keys(Keys.RETURN)
    
    
    time.sleep(5)
    
    # Pagina 2 - Clica no texto de link para mostrar a pagina da garantia
    try:        
        link = driver.find_element(By.LINK_TEXT, "Suporte básico")
        link.click()
    except Exception as e:
        
        # Alternar para o IFrame
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iframeSurvey"))  # Substitua pelo ID do IFrame
        )
        driver.switch_to.frame(iframe)

        # clica no pop-up de pesquisa que não aparece todas as vezes.
        btnpesquisa = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id="noButtonIPDell"]'))
        )
        #btnpesquisa = driver.find_element(By.ID, "noButtonIPDell")
        btnpesquisa.click()
        
        time.sleep(5)
        
        driver.switch_to.default_content()
        
        link = driver.find_element(By.LINK_TEXT, "Suporte básico")
        link.click()

    time.sleep(5)

    # Pegue o HTML da página
    html = driver.page_source

    # Use BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    print(soup)

    # Extraia a data de compra
    purchase_date_element = soup.find(id='dsk-purchaseDt')
 
    
    print(purchase_date_element)
    purchase_date = purchase_date_element.text if purchase_date_element else 'Data não encontrada'
    
    if(purchase_date != 'Data não encontrada'):
        purchase_date = datetime.strptime(purchase_date, "%B %d, %Y").strftime("%d/%m/%Y") 

    print(f'Data de compra: {purchase_date}')
    
except Exception as e:
    print(f'Ocorreu um erro: {e}')

finally:
    # Feche o navegador
    driver.quit()
