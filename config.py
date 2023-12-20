from flask import Flask
from flask_socketio import SocketIO
import dash_bootstrap_components as dbc

server = Flask(__name__)
socketio = SocketIO(server)
DATA_DIRECTORY = "data"
CSV_SEPARATOR = ";"
EXTERNAL_STYLESHEETS = [dbc.themes.BOOTSTRAP]
SERVER_CONFIG = {
    "debug": True,
    "allow_unsafe_werkzeug": True,
    "port": 5002
    # Otros parámetros de configuración del servidor
}