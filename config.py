from flask import Flask
from flask_socketio import SocketIO

server = Flask(__name__)
socketio = SocketIO(server)
DATA_DIRECTORY = "data"
CSV_SEPARATOR = ";"