import dash
from config import socketio, server, SERVER_CONFIG, EXTERNAL_STYLESHEETS
from ui import load_index_html, create_layout
from data_manager import DataManager
from mercadolibre_scraper import MercadoLibreScraper
from scraper import ScraperManager
from callbacks import register_callbacks

class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__, server=server, external_stylesheets=EXTERNAL_STYLESHEETS)
        self.app.config.suppress_callback_exceptions = True
        self.app.index_string = load_index_html()
        self.app.layout = create_layout()

        self.data_manager = DataManager()
        self.mercado_libre_scraper = MercadoLibreScraper()
        self.scraper_manager = ScraperManager(self.data_manager, self.mercado_libre_scraper)
        register_callbacks(self.app, self.scraper_manager, self.data_manager)

    def run(self):
        socketio.run(server, **SERVER_CONFIG)
