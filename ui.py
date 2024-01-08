import dash_bootstrap_components as dbc
from dash import html, dash_table
from dash import dcc


def load_index_html():
    with open('templates/main_template.html', 'r') as file:
        return file.read()


def create_layout():
    layout = dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    html.H1("ML Scraper", className="text-center p-5"),
                    dbc.Input(id="input-product", placeholder="Ingresa el nombre del producto...", type="text"),
                    html.Br(),
                    dbc.Button("Buscar", id="btn-scrape", n_clicks=0),
                    dbc.Alert(id="scrape-message", color="primary", is_open=False),
                    html.Div(id="scrape-progress"),  # Agrega este elemento para mostrar el progreso
                    html.Br(),
                    html.Div(id='trigger-for-detailed-scrape', style={'display': 'none'}),
                    html.Br(),
                    html.Div(id='temp-data-storage', style={'display': 'none'}),
                    html.Div(id='table-initial-container', children=[dash_table.DataTable(id='table-initial', columns=[], data=[])]),
                    dash_table.DataTable(
                        id='table-detailed',
                        columns=[],
                        # Habilita la ordenación para cada columna
                        data=[],
                        filter_action='native',  # Habilita el filtrado nativo
                        sort_action='native',  # Habilita la ordenación nativa
                        sort_mode='multi'  # Permite la ordenación multi-columna
                    )
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
    return dcc.Loading(layout, type="circle")
