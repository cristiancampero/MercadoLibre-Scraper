from time import sleep
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import warnings



class Scraper():

    def __init__(self):
        if os.path.isfile("chromedriver.exe"):
            pass
        else:
            print("********* No se encuentra cromedriver.exe *********")
            sys.exit()

    def preferences(self):
        self.search_term = input("\nProducto a buscar: ")


    def setUp(self):
        # Desactivar advertencia de deprecación
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # Especificar la ruta de Chromedriver
        chromedriver_path = 'chromedriver.exe'
        # Crear objeto Service usando ruta de Chromedriver
        service = Service(chromedriver_path)
        # Crear objeto WebDriver y pasar el objeto Service al constructor de ChromeDriver
        self.driver = webdriver.Chrome(service=service)
        # maximizar la ventana
        self.driver.maximize_window()
        # ir a  mercadolibre.com
        self.driver.get("https://www.mercadolibre.com")


    def choise_country(self):
        #Seleccionar Argentina
        country = self.driver.find_element(By.ID, value="AR")
        country.click()
        sleep(3)


    def close_cookie_banner(self):
        cookie = self.driver.find_element(By.CLASS_NAME, value="cookie-consent-banner-opt-out__action")
        cookie.click()


    def search(self):
        search_bar = self.driver.find_element(By.CLASS_NAME, value="nav-search-input")
        search_bar.clear()
        search_bar.send_keys(self.search_term)

        search_buttom = self.driver.find_element(By.CLASS_NAME, value="nav-search-btn")
        search_buttom.click()
        sleep(3)


    def get_data(self):
        # get data from each posts
        # save the html of the page
        content = self.driver.page_source

        # parser the html
        soup = BeautifulSoup(content, 'html.parser')

        #scroll to the bottom of the page to load all images
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # create a dic to save the data
        self.meli_data = []

        # take all posts
        content = soup.find_all('li', class_='ui-search-layout__item')

        # iteration to scrape posts
        for post in content:
            # get the title
            title = post.find('h2').text
            # get the price
            price = post.find('span', class_='price-tag-fraction').text
            # get the url image
            try:
                img_url = post.find("img")["data-src"]
            except:
                img_url = post.find("img")["src"]
            # get the url post
            post_url = post.find("a")["href"]

            # save in a dic
            data = {
                "title": title,
                "price": price,
                "image": img_url,
                "url posts": post_url
            }

            # save the dictionaries in a list
            self.meli_data.append(data)


    def export_to_csv(self):
        # export to a csv file
        df = pd.DataFrame(self.meli_data)
        df.to_csv("data/data_mercadolibre.csv", sep=";")


    def tearDown(self):
        print("\nCerrando Google Chrome...")
        sleep(1)
        print("\nRevisa el archivo 'data/data_mercadolibre.csv'")
        self.driver.close()


if __name__ == "__main__":
    s = Scraper()
    s.preferences()
    s.setUp()
    s.choise_country()
    s.close_cookie_banner()
    s.search()
    s.get_data()
    s.export_to_csv()
    s.tearDown()
