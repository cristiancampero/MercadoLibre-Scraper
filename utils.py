import os
import glob
from config import socketio, DATA_DIRECTORY, CSV_SEPARATOR
import json
import dash
import logging
import re

logging.basicConfig(level=logging.DEBUG)


def format_filename(product_name):
    return product_name.replace(' ', '-').lower()

def format_price(df):
    if "price" in df.columns:
        df = df.copy()
        df["price"] = df["price"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)
    return df


def format_price_for_display(price):
    try:
        # Intentar convertir el precio a un número flotante y luego aplicar el formato
        price_float = float(price)
        return "${:,.2f}".format(price_float).replace(",", "@").replace(".", ",").replace("@", ".")
    except ValueError:
        # Si la conversión falla, devuelve el precio original
        return price


def get_latest_csv(directory):
    list_of_files = glob.glob(
        os.path.join(directory, "*.csv"))  # * significa todos si no hay requisitos específicos
    if not list_of_files:  # Si no hay archivos
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return os.path.basename(latest_file).replace("_scraped_data_detailed.csv", "")


def format_link_to_markdown(link):
    return f"[Link]({link})"

def extract_url_from_markdown(markdown_link):
    # Expresión regular para identificar un enlace Markdown
    # Esto buscará texto que coincida con [algo](url)
    pattern = r'\[.*\]\((.*)\)'
    match = re.search(pattern, markdown_link)
    if match:
        # Extrae y devuelve la URL
        return match.group(1)
    return None

@socketio.on('scrape_status')
def update_scrape_progress(message):
    progress = message['progress']
    total = message['total']
    # Emit the progress to the frontend
    dash.callback_context.response.set_data(json.dumps({
        'response': {
            'progress': progress,
            'total': total
        }
    }))

def export_to_csv(self, product_name):
    try:
        # Reemplazar espacios por guiones en el nombre del producto
        filename = f"{product_name.replace(' ', '-')}.csv"
        logger.info(f"Preparando para exportar datos del producto: {product_name}")

        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            logger.info(f"Creado el directorio de datos: {self.data_directory}")

        df = pd.DataFrame(self.data)
        file_path = os.path.join(self.data_directory, filename)

        df.to_csv(file_path, sep=self.csv_separator)
        logger.info(f"Datos exportados exitosamente a {file_path}")

    except Exception as e:
        logger.error(f"Error al exportar datos a CSV: {e}")
