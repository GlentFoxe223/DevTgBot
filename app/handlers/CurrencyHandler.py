from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expect
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

class CurrencyHandler():
    def __init__(self):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        self.proxy_address = os.getenv('proxy_address')
        self.proxy_username = os.getenv('proxy_username')
        self.proxy_password = os.getenv('proxy_password')

        self.proxy = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_address}"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_page(self, answer):
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={self.proxy}')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        try:
            url = f"https://www.google.com/search?q={answer}"
            driver.get(url)

            time.sleep(1)

            wait = WebDriverWait(driver, 30)
            wait.until(expect.presence_of_element_located((By.CLASS_NAME, 'b1hJbf')))
            
            time.sleep(1)

            html = driver.page_source
            return html
        except Exception as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None
        finally:
            driver.quit()

    def get_num(self, from_currency, to_currency, amount):
        try:
            amount = float(amount.replace(",", "."))
        except ValueError:
            return "Ошибка: введите корректное число."
        
        answer=f"{amount} {from_currency} to {to_currency}"
        answer=answer.replace(' ', '+')
        html=self.fetch_page(answer)
        if html:
            soup=BeautifulSoup(html, 'html.parser')
            result_div = soup.find('div', class_='b1hJbf')
            if result_div:
                result_text = result_div.text.strip()
                return f"{amount} {from_currency} = {result_text}"