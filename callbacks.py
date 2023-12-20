# callbacks.py
from dash.dependencies import Output, Input, State


# callbacks.py

def register_callbacks(app, scraper_manager, data_manager):
    @app.callback(
        [Output("scrape-output", "children"),
         Output('table', 'data'),
         Output('table', 'columns')],
        [Input("btn-scrape", "n_clicks")],
        [State("input-product", "value")]
    )
    def run_scrape(n_clicks, input_product_name):
        message = ""
        if n_clicks > 0 and input_product_name:
            scraper_manager.execute_scraping(input_product_name)
            message = f"Scraping para {input_product_name} completado!"
            data, columns = data_manager.prepare_table_data()
        else:
            data, columns = [], []

        return message, data, columns
