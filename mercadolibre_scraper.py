import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from config import socketio


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

    def format_price(self, price_element):
        if price_element and isinstance(price_element.text, str):
            return price_element.text.replace('.', '')
        return None

    def extract_post_data(self, post):
        title_element = post.find('h2')
        price_value = self.format_price(post.find('span', class_='andes-money-amount__fraction'))
        post_link_element = post.find("a")
        img_element = post.find("img")

        data = {
            'title': title_element.text if title_element else None,
            'price': price_value,
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

    def scrape_product_page(self, url):
        page_content = self.get_page_content(url)
        if not page_content:
            return False

        soup = BeautifulSoup(page_content, 'html.parser')

        # Buscar el elemento de envío que contiene el texto "Llega"
        envio_element = soup.find('span', string=lambda text: text and "Llega" in text)

        if envio_element:
            envio = envio_element.text
        else:
            envio = None

        return {
            'envio': envio
        }

    def update_product_details(self, product_name):
        file_path = os.path.join(self.DATA_DIRECTORY, f"{product_name}_scraped_data.csv")
        file_path_detailed = os.path.join(self.DATA_DIRECTORY, f"{product_name}_scraped_data_detailed.csv")

        # Cargar el CSV en un DataFrame usando pandas
        df = pd.read_csv(file_path, sep=self.CSV_SEPARATOR).head(10)

        # Crear una columna 'envio_gratis' inicializada con False
        df['envio_gratis'] = False

        # Recorrer cada fila (producto) del DataFrame
        for index, product in df.iterrows():
            details = self.scrape_product_page(product['post link'])

            # Si 'envio' en details contiene la palabra 'gratis', actualiza la columna 'envio_gratis' para ese producto
            if 'envio' in details and details['envio'] and 'gratis' in details['envio'].lower():
                df.at[index, 'envio_gratis'] = True

        # Imprimir las primeras filas del DataFrame para verificar los cambios
        print(df.head())

        # Guardar el DataFrame actualizado nuevamente en el archivo CSV
        df.to_csv(file_path_detailed, sep=self.CSV_SEPARATOR, index=False)

        # Imprimir la ruta del archivo guardado
        print(f"Archivo guardado en: {file_path}")


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

        for i in range(0, self.MAX_PAGES):
            if total_products_scraped >= scraping_limit:
                print(f"\nSe alcanzó el límite de {scraping_limit} productos. Terminando.")
                break

            url = f"{base_url}{cleaned_name}_Desde_{(i * self.PAGE_INCREMENT) + 1}_NoIndex_True"
            if not self.scrape_page(url):
                print("\nTerminó el scraping.")
                break

            total_products_scraped += len(self.data)

            # Emit the progress
            print("Intentando emitir evento...")
            socketio.emit('scrape_status', {'progress': i, 'total': self.MAX_PAGES})
            print("Evento emitido!")

        self.update_product_details(product_name)

    def export_to_csv(self, product_name):
        filename = f"{product_name}_scraped_data.csv"
        if not os.path.exists(self.DATA_DIRECTORY):
            os.makedirs(self.DATA_DIRECTORY)
        df = pd.DataFrame(self.data)
        file_path = os.path.join(self.DATA_DIRECTORY, filename)
        df.to_csv(file_path, sep=self.CSV_SEPARATOR)

