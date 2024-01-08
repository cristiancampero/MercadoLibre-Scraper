from bs4 import BeautifulSoup
from config import socketio, SCRAPER_CONFIG, DATA_DIRECTORY, CSV_SEPARATOR
from scraper import Scraper
from utils import format_filename, format_link_to_markdown
from log_config import get_logger

logger = get_logger(__name__)


class MercadoLibreScraper(Scraper):

    def __init__(self):
        self.data = []
        self.base_url = SCRAPER_CONFIG['base_url']
        self.data_directory = DATA_DIRECTORY
        self.csv_separator = CSV_SEPARATOR
        self.page_increment = SCRAPER_CONFIG['page_increment']
        self.max_pages = SCRAPER_CONFIG['max_pages']

    def format_price(self, price_element):
        if price_element and isinstance(price_element.text, str):
            return price_element.text.replace('.', '')
        return None

    def extract_product_year_km_and_publication_date(self, soup):
        subtitle_element = soup.find('span', class_='ui-pdp-subtitle')
        if subtitle_element:
            parts = subtitle_element.text.split('·')
            year_km_part = parts[0].strip() if len(parts) > 0 else ""
            year, km = year_km_part.split('|') if '|' in year_km_part else (None, None)
            publication_date = parts[1].strip() if len(parts) > 1 else None

            return year.strip() if year else None, km.strip() if km else None, publication_date
        return None, None, None

    def extract_post_data(self, post):
        title_element = post.find('h2')
        price_value = self.format_price(post.find('span', class_='andes-money-amount__fraction'))
        post_link_element = post.find("a")
        img_element = post.find("img")

        data = {
            'title': title_element.text if title_element else None,
            'price': price_value if price_value else None,
            'post_link': post_link_element['href'] if post_link_element else None,
            'image link': img_element.get('data-src', img_element.get('src')) if img_element else None
        }
        return data

    def get_total_results(self, soup):
        results_element = soup.find('span', class_='ui-search-search-result__quantity-results')
        if results_element:
            return int(results_element.text.split()[0].replace('.', '').replace(',', ''))
        return 0  # o cualquier valor predeterminado

    def scrape_page_results(self, url):
        logger.debug(f"Comenzando scrape_page_results para URL: {url}")
        soup = self.get_page_content(url)

        if not soup:
            logger.warning("No se pudo obtener el contenido de la página.")
            return []

        content = soup.find_all('li', class_='ui-search-layout__item')
        logger.debug(f"Encontrados {len(content)} elementos en la página.")

        page_data = []
        for post in content:
            post_data = self.extract_post_data(post)
            page_data.append(post_data)
            logger.debug(f"Datos del post agregados: {post_data}")

        logger.debug("Scrape de la página completado exitosamente.")
        return page_data

    def scrape_product_details(self, soup):
        title = soup.find('h1', class_='ui-pdp-title')
        price_simbol = soup.find('span', class_='andes-money-amount__currency-symbol')
        price = soup.find('span', class_='andes-money-amount__fraction')
        year, km, publication_date = self.extract_product_year_km_and_publication_date(soup)
        link = soup.find('link', rel='canonical')
        author = soup.find('div', class_='ui-pdp-seller-validated')

        envio_element = soup.find('span', string=lambda text: text and "Llega" in text)

        data = {
            'title': title.text if title else None,
            'envio': envio_element.text if envio_element else None,
            'price': f"{price_simbol.text} {price.text}" if price_simbol and price else None,
            'year': year,
            'km': km,
            'publication_date': publication_date,
            'author': author.text if author else None,
            'link': format_link_to_markdown(link['href']) if link else None,
        }

        return data

    def scrape_product_list(self, domain, product_name, user_scraping_limit=1000):
        cleaned_name = format_filename(product_name)
        base_url = self.base_url.format(domain=domain)

        # Obtener el contenido de la primera página para extraer el número total de resultados
        soup = self.get_page_content(base_url + cleaned_name)
        total_results = self.get_total_results(soup)

        # Estimar la cantidad de productos por página
        products_per_page = len(soup.find_all('li', class_='ui-search-layout__item'))
        estimated_total_pages = total_results // products_per_page + (total_results % products_per_page > 0)

        scraping_limit = min(total_results, user_scraping_limit, 1000)
        logger.info(f"Se obtuvieron {total_results} resultados. Se limitará el scraping a {scraping_limit} resultados.")

        all_data = []

        for i in range(0, min(estimated_total_pages, self.max_pages)):
            if len(all_data) >= scraping_limit:
                logger.info(f"Se alcanzó el límite de {scraping_limit} productos. Terminando.")
                break

            url = f"{base_url}{cleaned_name}_Desde_{(i * self.page_increment) + 1}_NoIndex_True"
            scraped_page_data = self.scrape_page_results(url)
            if not scraped_page_data:
                logger.warning(f"La página {i + 1} no devolvió datos. Terminando.")
                break

            all_data.extend(scraped_page_data)
            logger.info(f"Scraping de página {i + 1} de {estimated_total_pages} completado")

            # Emitir el progreso
            socketio.emit('scrape_status', {'progress': i, 'total': estimated_total_pages})

        return all_data

