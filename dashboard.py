import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from mercadolibre_scraper import MercadoLibreScraper
from config import socketio, server
from utils import load_data, format_price, format_price_for_display, format_link_to_markdown, update_scrape_progress


class Dashboard:

    def __init__(self):
        self.product_name = None
        self.app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.app.config.suppress_callback_exceptions = True
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>

        <head>
            <title>Dash App</title>
            {%metas%}
            {%favicon%}
            {%css%}
        </head>

        <body>

            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
                <!-- Puedes agregar tus scripts personalizados aquí -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.js"></script>
                <script>
                    var socket = io.connect('http://127.0.0.1:5002');
                    socket.on('scrape_status', function(data) {
                        document.getElementById('scrape-progress').innerText =
                            'Scrape Progress: ' + data.progress + '/' + data.total;
                    });
                </script>
            </footer>

        </body>

        </html>
        '''

        self.df = pd.DataFrame()
        self.layout = self.create_layout()
        self.callbacks()

    def create_layout(self):
        layout = dbc.Container(
            [
                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="input-product", placeholder="Ingresa el nombre del producto...", type="text"),
                        html.Br(),
                        dbc.Button("Buscar", id="btn-scrape", n_clicks=0),
                        html.Div(id="scrape-output"),
                        html.Div(id="scrape-progress"),  # Agrega este elemento para mostrar el progreso
                        html.Br(),
                        dcc.Graph(id="price-histogram"),
                        html.Br(),
                        dash_table.DataTable(id='table', columns=[], data=[])
                    ], width=12),
                ]),
                html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.js"),
                html.Script("""
                    // Your JavaScript code to listen to SocketIO events and update the scrape-progress element
                    var socket = io.connect('http://127.0.0.1:5000');
                    socket.on('scrape_status', function(data) {
                        document.getElementById('scrape-progress').innerText =
                            'Scrape Progress: ' + data.progress + '/' + data.total;
                    });
                """),
            ],
            fluid=True,
        )
        return layout

    def execute_scraping(self, product_name):
        # Comentamos estas líneas para evitar el scraping
        scraper = MercadoLibreScraper()
        scraper.scrape_product('ar', product_name)

        # Emit progress updates to frontend
        socketio.emit('scrape_status', {'progress': 'some progress message or data'})

        scraper.export_to_csv(product_name)

        self.product_name = product_name
        self.df = load_data(product_name)

    def generate_histogram(self):
        fig = {}

        self.df = format_price(self.df)
        fig = {
            'data': [{
                'x': self.df["price"].dropna(),
                'type': 'histogram',
                'marker': {'color': '#FA5858'}
            }],
            'layout': {
                'title': 'Distribución de Precios',
                'xaxis': {'title': 'Precio'},
                'yaxis': {'title': 'Cantidad'}
            }
        }
        return fig

    def prepare_table_data(self):
        data = []
        if not self.df.empty:
            sorted_df = self.df.sort_values(by="price", ascending=True)
            sorted_df["price"] = sorted_df["price"].apply(format_price_for_display)
            sorted_df["post link"] = sorted_df["post link"].apply(format_link_to_markdown)
            data = sorted_df[['title', 'price', 'post link', 'envio_gratis']].to_dict('records')
        return data

    def callbacks(self):
        @self.app.callback(
            [Output("scrape-output", "children"), Output("price-histogram", "figure"), Output('table', 'data'),
             Output('table', 'columns')],
            [Input("btn-scrape", "n_clicks")],
            [dash.dependencies.State("input-product", "value")]
        )
        def run_scrape(n_clicks, input_product_name):
            message = ""
            fig = {}
            data = []
            columns = [
                {'id': 'title', 'name': 'title'},
                {'id': 'price', 'name': 'price'},
                {'id': 'post link', 'name': 'Link', 'presentation': 'markdown'},
                {'id': 'envio_gratis', 'name': 'envio_gratis'}
            ]

            if n_clicks > 0 and input_product_name:
                self.execute_scraping(input_product_name)
                message = f"Scraping para {input_product_name} completado!"
                fig = self.generate_histogram()
                data = self.prepare_table_data()

            return message, fig, data, columns

    def run(self):
        self.app.layout = self.layout
        socketio.run(server, debug=True, allow_unsafe_werkzeug=True, port=5002)
