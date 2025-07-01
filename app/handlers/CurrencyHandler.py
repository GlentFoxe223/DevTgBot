from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
from selenium import webdriver
import os

class CurrencyHandler:
    def __init__(self):
        load_dotenv(dotenv_path="/home/gleb/TGbot_projects/.env", override=True)

        self.proxy_address = os.getenv('proxy_address')
        self.proxy_username = os.getenv('proxy_username')
        self.proxy_password = os.getenv('proxy_password')

        self.proxy = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_address}"

        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

    def search_currency(self, amount, to_currency,from_currency):
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless=new')
            options.add_argument(f"user-agent={self.user_agent}")
            # options.add_argument(f"--proxy-server={self.proxy}")

            service = webdriver.ChromeService(executable_path='app/driver/chromedriver')

            driver = webdriver.Chrome(options=options, service=service)
    
            driver.get(f'https://www.google.com/search?q={amount}+{from_currency}+to+{to_currency}')
            time.sleep(10)

            result = driver.page_source
            if result:
                soup = BeautifulSoup(result, features="html.parser")
                if soup:
                    info = soup.find('span',class_='DFlfde SwHCTb')
                    if info:
                        to_amount = info.text
                        driver.quit()
                        try:
                            return f'{amount} {from_currency.upper()} = {to_amount} {to_currency.upper()}'
                        except ValueError:
                            return 'Произошла ошибка, проверьте свой запрос и попробуйте снова'
                    else:
                        return 'Произошла ошибка, проверьте свой запрос и попробуйте снова'
                else:
                    return 'Произошла ошибка, проверьте свой запрос и попробуйте снова'
            else:
                return 'Произошла ошибка, проверьте свой запрос и попробуйте снова'
        except:
            None
        finally:
            driver.close()
            driver.quit()
        
    def get_currency(self, amount, to_currency,from_currency):
        return self.search_currency(amount, to_currency,from_currency)