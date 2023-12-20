from mercadolibre_scraper import MercadoLibreScraper
from config import socketio


class ScraperManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    def execute_scraping(self, product_name):
        # Comentamos estas líneas para evitar el scraping
        scraper = MercadoLibreScraper()
        scraper.scrape_product('ar', product_name)

        # Emit progress updates to frontend
        socketio.emit('scrape_status', {'progress': 'some progress message or data'})

        scraper.export_to_csv(product_name)

        self.product_name = product_name
        self.data_manager.load_data(product_name)