import dash_bootstrap_components as dbc
from dash import html, dash_table

def load_index_html():
    with open('templates/main_template.html', 'r') as file:
        return file.read()


def create_layout():
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