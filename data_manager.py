from utils import format_price_for_display, format_filename, format_link_to_markdown
from config import DATA_DIRECTORY, CSV_SEPARATOR
import pandas as pd
import os
from log_config import get_logger

logger = get_logger(__name__)


class DataManager:

    def __init__(self):
        self.df = pd.DataFrame()

    def prepare_table_data(self, data):

        self.df = pd.DataFrame(data)
        columns = []
        if not self.df.empty:
            # Aplica formatos específicos si las columnas existen
            if 'post_link' in self.df.columns:
                self.df['post_link'] = self.df['post_link'].apply(format_link_to_markdown)

            # Ordena por una columna común o por la primera columna si 'price' no está presente
            sort_column = 'price' if 'price' in self.df.columns else self.df.columns[0]
            sorted_df = self.df.sort_values(by=sort_column, ascending=True)

            # Aplica formatos específicos si las columnas existen
            if 'price' in sorted_df.columns:
                sorted_df["price"] = sorted_df["price"].apply(format_price_for_display)

                # Configurar las columnas
                columns = [
                    {'name': 'Title', 'id': 'title', 'type': 'text'},
                    {'name': 'Price', 'id': 'price', 'type': 'text'},
                    {'name': 'Link', 'id': 'post_link', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Image', 'id': 'image link', 'type': 'text'}
                ]

                # Convertir el DataFrame a un formato adecuado para Dash DataTable
                data = sorted_df.to_dict('records')

        return data, columns

    def generate_columns(self, data):
        columns = []
        for key in data[0].keys():
            if "link" in key.lower():  # Detecta si la clave es un enlace
                columns.append({'name': key.capitalize(), 'id': key, 'type': 'text', 'presentation': 'markdown', 'sortable': True})
            else:
                columns.append({'name': key.capitalize(), 'id': key, 'sortable': True})
        return columns

    def load_data(self, product_name):
        try:
            filename = f'{format_filename(product_name)}.csv'
            file_path = os.path.join(DATA_DIRECTORY, filename)
            self.df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
            logger.info(f"Datos cargados exitosamente desde {file_path}")
        except Exception as e:
            logger.error(f"Error al cargar datos desde {file_path}: {e}")
