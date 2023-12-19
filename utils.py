import os
import glob
from config import socketio, DATA_DIRECTORY, CSV_SEPARATOR
import json
import pandas as pd
import dash
import logging

logging.basicConfig(level=logging.DEBUG)


def load_data(product_name):
    filename = f"{product_name}_scraped_data_detailed.csv"
    file_path = os.path.join(DATA_DIRECTORY, filename)
    return pd.read_csv(file_path, sep=CSV_SEPARATOR)


def format_price(df):
    if "price" in df.columns:
        df = df.copy()
        df["price"] = df["price"].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)
    return df


def format_price_for_display(price):
    # return "${:,.2f}".format(price).replace(",", "@").replace(".", ",").replace("@", ".")
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
