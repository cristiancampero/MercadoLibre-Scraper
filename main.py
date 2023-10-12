import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from tqdm import tqdm
import time


class MercadoLibreScraper:

    BASE_URL = 'https://listado.mercadolibre.com.{domain}/'
    DATA_DIRECTORY = "data"
    CSV_SEPARATOR = ";"
    PAGE_INCREMENT = 50
    MAX_PAGES = 200

    def __init__(self):
        self.data = []

    def get_page_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Error al obtener la página {url}: {e}")

    def extract_post_data(self, post):
        # Simplificar y mejorar legibilidad
        title_element = post.find('h2')
        price_element = post.find('span', class_='andes-money-amount__fraction')
        post_link_element = post.find("a")
        img_element = post.find("img")

        data = {
            'title': title_element.text if title_element else None,
            'price': price_element.text if price_element else None,
            'post link': post_link_element['href'] if post_link_element else None,
            'image link': img_element.get('data-src', img_element.get('src')) if img_element else None
        }
        return data

    def get_total_results(self, soup):
        results_element = soup.find('span', class_='ui-search-search-result__quantity-results')
        if results_element:
            return int(results_element.text.split()[0].replace('.', '').replace(',', ''))
        return 0  # o cualquier valor predeterminado

    def scrape_page(self, url):
        page_content = self.get_page_content(url)
        if not page_content:
            return False

        soup = BeautifulSoup(page_content, 'html.parser')
        content = soup.find_all('li', class_='ui-search-layout__item')
        for post in content:
            post_data = self.extract_post_data(post)
            self.data.append(post_data)
        return True

    def scrape_product(self, domain, product_name, user_scraping_limit=1000):
        cleaned_name = product_name.replace(" ", "-").lower()
        base_url = self.BASE_URL.format(domain=domain)

        # Obtener el contenido de la primera página para extraer el número total de resultados
        page_content = self.get_page_content(base_url + cleaned_name)
        soup = BeautifulSoup(page_content, 'html.parser')
        total_results = self.get_total_results(soup)

        # Usa el límite más pequeño: total_results, user_scraping_limit, o el límite por defecto (1000)
        scraping_limit = min(total_results, user_scraping_limit, 1000)

        total_products_scraped = 0
        with tqdm(total=self.MAX_PAGES, desc="Páginas escrapeadas") as progress_bar:
            for i in range(0, self.MAX_PAGES):
                if total_products_scraped >= scraping_limit:
                    print(f"\nSe alcanzó el límite de {scraping_limit} productos. Terminando.")
                    break

                url = f"{base_url}{cleaned_name}_Desde_{(i * self.PAGE_INCREMENT) + 1}_NoIndex_True"
                loop_start_time = time.time()

                if not self.scrape_page(url):
                    print("\nTerminó el scraping.")
                    break

                loop_elapsed_time = time.time() - loop_start_time
                total_products_scraped += len(self.data)
                progress_bar.update(1)
                progress_bar.set_postfix({"Tiempo loop": f"{loop_elapsed_time:.2f} s"})

    def export_to_csv(self, product_name):
        filename = f"{product_name}_scraped_data.csv"
        if not os.path.exists(self.DATA_DIRECTORY):
            os.makedirs(self.DATA_DIRECTORY)
        df = pd.DataFrame(self.data)
        file_path = os.path.join(self.DATA_DIRECTORY, filename)
        df.to_csv(file_path, sep=self.CSV_SEPARATOR)


class UserInterface:

    BASE_URLS = {
        1: {'country': 'Argentina', 'domain': 'ar'},
        2: {'country': 'Bolivia', 'domain': 'bo'},
        3: {'country': 'Brasil', 'domain': 'br'},
        4: {'country': 'Chile', 'domain': 'cl'},
        5: {'country': 'Colombia', 'domain': 'co'},
        6: {'country': 'Costa Rica', 'domain': 'cr'},
        7: {'country': 'Dominicana', 'domain': 'do'},
        8: {'country': 'Ecuador', 'domain': 'ec'},
        9: {'country': 'Guatemala', 'domain': 'gt'},
        10: {'country': 'Honduras', 'domain': 'hn'},
        11: {'country': 'México', 'domain': 'mx'},
        12: {'country': 'Nicaragua', 'domain': 'ni'},
        13: {'country': 'Panamá', 'domain': 'pa'},
        14: {'country': 'Paraguay', 'domain': 'py'},
        15: {'country': 'Perú', 'domain': 'pe'},
        16: {'country': 'Salvador', 'domain': 'sv'},
        17: {'country': 'Uruguay', 'domain': 'uy'},
        18: {'country': 'Venezuela', 'domain': 've'},
    }

    def __init__(self, scraper):
        self.scraper = scraper

    def menu(self):
        print("\nSeleccioná el país:")
        for number, country_info in self.BASE_URLS.items():
            print(f"{number}. {country_info['country']}")

        try:
            opcion = int(input('Número de país (Ejemplo: 5): '))
        except ValueError:
            print("Por favor, elegí un número válido.")
            return

        if opcion not in self.BASE_URLS:
            print("Elegí un número válido del 1 al 18.")
            return

        domain = self.BASE_URLS[opcion]['domain']
        product_name = input("\nProducto: ")

        try:
            scraping_limit = int(input(f"\nCantidad máxima de productos a escrapear (por defecto: 1000): "))
        except ValueError:
            print("Valor inválido. Se usará el límite por defecto de 1000.")
            scraping_limit = 1000

        self.scraper.scrape_product(domain, product_name, scraping_limit)
        self.scraper.export_to_csv(product_name)


if __name__ == "__main__":
    scraper = MercadoLibreScraper()
    ui = UserInterface(scraper)
    ui.menu()
