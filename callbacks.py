from dash.dependencies import Output, Input, State
from utils import extract_url_from_markdown
from log_config import get_logger
import json
logger = get_logger(__name__)


def register_callbacks(app, scraper_manager, data_manager):
    @app.callback(
        [Output("scrape-message", "children"),
         Output("scrape-message", "is_open"),
         Output('table-initial', 'data'),
         Output('table-initial', 'columns'),
         Output('trigger-for-detailed-scrape', 'children'),
         Output('temp-data-storage', 'children')
         ],
        [Input("btn-scrape", "n_clicks")],
        [State("input-product", "value")]
    )
    def run_scrape(n_clicks, input_product_name):
        if n_clicks > 0 and input_product_name:
            data, message = scraper_manager.get_product_list(input_product_name)
            msg_open = True
            data, columns = data_manager.prepare_table_data(data)
            trigger = 'updated'
            json_data = json.dumps(data)
            logger.info(f"Cantidad de datos: {len(data)}")
        else:
            message, msg_open, data, columns, json_data = "", False, [], [], None
            trigger = None

        return message, msg_open, data, columns, trigger, json_data

    @app.callback(
        [Output('table-detailed', 'data'),
         Output('table-detailed', 'columns'),
         Output('table-initial-container', 'style')
        ],
        [Input('trigger-for-detailed-scrape', 'children')],
        [State('temp-data-storage', 'children')]
    )
    def run_scrape_detailed(trigger, json_data):
        if trigger and json_data:
            table_data = json.loads(json_data)
            urls = [extract_url_from_markdown(row['post_link']) for row in table_data]
            products = scraper_manager.get_products_details_thread(urls)
            columns = data_manager.generate_columns(products)
            return products, columns, {'display': 'none'}
        else:
            return [], [], {'display': 'block'}
