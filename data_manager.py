from utils import format_price_for_display, format_link_to_markdown, format_filename
from config import DATA_DIRECTORY, CSV_SEPARATOR
import pandas as pd
import os
from log_config import get_logger

logger = get_logger(__name__)


class DataManager:

    def __init__(self):
        self.df = pd.DataFrame()

    def prepare_table_data(self):
        data = []
        columns = []
        if not self.df.empty:
            print(self.df.head())

            # Ordena por una columna común o por la primera columna si 'price' no está presente
            sort_column = 'price' if 'price' in self.df.columns else self.df.columns[0]
            sorted_df = self.df.sort_values(by=sort_column, ascending=True)

            # Aplica formatos específicos si las columnas existen
            if 'price' in sorted_df.columns:
                sorted_df["price"] = sorted_df["price"].apply(format_price_for_display)
            if 'post link' in sorted_df.columns:
                sorted_df["post link"] = sorted_df["post link"].apply(format_link_to_markdown)

            data = sorted_df.to_dict('records')
            columns = [{'name': col, 'id': col} for col in sorted_df.columns]

        return data, columns

    def load_data(self, product_name):
        try:
            filename = f'{format_filename(product_name)}.csv'
            file_path = os.path.join(DATA_DIRECTORY, filename)
            self.df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
            logger.info(f"Datos cargados exitosamente desde {file_path}")
        except Exception as e:
            logger.error(f"Error al cargar datos desde {file_path}: {e}")
