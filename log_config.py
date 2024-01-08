import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Configurar el nivel de registro a WARNING para evitar mensajes DEBUG
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("scraper").setLevel(logging.INFO)
    logging.getLogger("mercadolibre_scraper").setLevel(logging.INFO)
def get_logger(name):
    setup_logging()
    return logging.getLogger(name)
