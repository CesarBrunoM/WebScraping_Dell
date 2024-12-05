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
    Clica no link de suporte adequado (Suporte básico, ProSupport, Gerenciar serviços).
    Caso não consiga clicar em nenhum, retorna None.
    """
    tipo_garantia = None
    links = [
        ("Suporte básico", "Suporte básico"),
        ("ProSupport", "ProSupport"),
        ("Gerenciar serviços", "ProSupport")  # O ProSupport foi repetido, caso não encontre o 'Gerenciar serviços'
    ]
    
    for link_text, tipo in links:
        try:
            # Tenta esperar e clicar no link
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, link_text))
            ).click()
            tipo_garantia = tipo  # Atualiza o tipo de garantia
            break  # Sai do loop após encontrar o link e clicar
        except TimeoutException:
            # Se o link não for clicável dentro do tempo, tenta o próximo
            continue
        except Exception as e:
            # Para qualquer outro erro, imprime e tenta o próximo
            print(f"Erro ao tentar clicar no link '{link_text}': {e}")
            continue
    
    # Se não conseguiu clicar em nenhum link, avisa que não encontrou nenhum válido
    if tipo_garantia is None:
        print(f"Não foi possível encontrar o link de suporte para a tag {tag}.")
        return None
    
    return tipo_garantia


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
        # Espera até que os elementos com IDs das datas estejam visíveis
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'dsk-purchaseDt'))
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'dsk-expirationDt'))
        )
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Busca os elementos com as datas no HTML
        purchase_date_element = soup.find(id='dsk-purchaseDt')
        expiration_date_element = soup.find(id='dsk-expirationDt')    
        
        if purchase_date_element and expiration_date_element:
            purchase_date = purchase_date_element.text.strip().lower()
            expiration_date = expiration_date_element.text.strip().lower()

            # Substitui os meses em português pelos equivalentes em inglês
            for mes_pt, mes_en in meses.items():
                purchase_date = purchase_date.replace(mes_pt, mes_en)
                expiration_date = expiration_date.replace(mes_pt, mes_en)

            # Converte as datas para o formato desejado
            purchase_date = datetime.strptime(purchase_date, "%B %d, %Y").strftime("%d/%m/%Y")
            expiration_date = datetime.strptime(expiration_date, "%B %d, %Y").strftime("%d/%m/%Y")

            return purchase_date, expiration_date
        else:
            return "Data não encontrada"
    except Exception as e:
        raise RuntimeError(f"Erro ao extrair a data de compra: {e}")

def main():
    arquivo_base = 'Arquivos_excel\\Lista_ativos.xlsx'
    destino_dataframe = 'Arquivos_excel\\'
    driver = setup_driver()
    driver.get('https://www.dell.com/support/home/pt-br')
    
    df = ler_dataframe(arquivo_base)    

    try:
        for index, row in df.iterrows():
            tag = row['TAG']
            
            navigate_to_support_page(driver, tag)
            handle_survey_popup(driver)
            tipo_suporte = click_support_link(driver, tag)
            purchase_date,expiration_date  = extract_purchase_date(driver) 
            
                                    
            df.at[index, 'TIPO_GARANTIA'] = tipo_suporte
            df.at[index, 'DATA_COMPRA'] = purchase_date
            df.at[index, 'DATA_FIM_GARANTIA'] = expiration_date
            print(tag)
                
        salvar_dataframe(df,destino_dataframe)
        
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
