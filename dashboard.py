import dash
from dash.dependencies import Input, Output
from mercadolibre_scraper import MercadoLibreScraper
from config import socketio, server, SERVER_CONFIG, EXTERNAL_STYLESHEETS
from ui import load_index_html, create_layout
from data_manager import DataManager


class Dashboard:

    def __init__(self):
        self.product_name = None
        self.app = dash.Dash(__name__, server=server, external_stylesheets=EXTERNAL_STYLESHEETS)
        self.app.config.suppress_callback_exceptions = True
        self.app.index_string = load_index_html()
        self.app.layout = create_layout()
        self.data_manager = DataManager()
        self.callbacks()

    def execute_scraping(self, product_name):
        # Comentamos estas líneas para evitar el scraping
        scraper = MercadoLibreScraper()
        scraper.scrape_product('ar', product_name)

        # Emit progress updates to frontend
        socketio.emit('scrape_status', {'progress': 'some progress message or data'})

        scraper.export_to_csv(product_name)

        self.product_name = product_name
        self.data_manager.load_data(product_name)

    def callbacks(self):
        @self.app.callback(
            [Output("scrape-output", "children"),
             Output('table', 'data'),
             Output('table', 'columns')],
            [Input("btn-scrape", "n_clicks")],
            [dash.dependencies.State("input-product", "value")]
        )
        def run_scrape(n_clicks, input_product_name):
            message = ""
            if n_clicks > 0 and input_product_name:
                self.execute_scraping(input_product_name)
                message = f"Scraping para {input_product_name} completado!"
                data, columns = self.data_manager.prepare_table_data()
            else:
                data, columns = [], []

            return message, data, columns

    def run(self):
        socketio.run(server, **SERVER_CONFIG)
