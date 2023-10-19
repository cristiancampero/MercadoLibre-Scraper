import sqlite3
import pandas as pd
from datetime import datetime

def store_csv_to_sqlite(csv_path):
    # Connect to the SQLite database
    conn = sqlite3.connect('properties.db')
    # Create the table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            title TEXT,
            price REAL,
            square_meters REAL,
            price_per_m2 REAL,
            location TEXT,
            link TEXT,
            first_photo TEXT,
            processing_date TEXT,
            bathrooms TEXT,
            rooms TEXT,
            tracking_id TEXT,
            creation_date TEXT,
            last_update_date TEXT
        )
    """)
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    # Filter out entries where 'price_per_m2' is not None
    df = df[df['price_per_m2'].notna()]

    # Extract the base url from the link
    df['tracking_id'] = df['link'].apply(lambda x: x.split('#')[0])
    # Add the creation_date and last_update_date fields
    df['creation_date'] = datetime.now().strftime('%Y-%m-%d')
    df['last_update_date'] = datetime.now().strftime('%Y-%m-%d')
    # Check if record exists and if price_per_m2 has changed
    df.to_sql('temp_table', conn, if_exists='replace', index=False)
    cursor = conn.cursor()
    res = cursor.execute("""
        INSERT INTO properties (title, price, square_meters, price_per_m2, location, link, first_photo, processing_date, bathrooms, rooms, tracking_id, creation_date, last_update_date)
        SELECT title, price, square_meters, price_per_m2, location, link, first_photo, processing_date, bathrooms, rooms, tracking_id, creation_date, last_update_date
        FROM temp_table
        WHERE NOT EXISTS (SELECT 1 FROM properties WHERE properties.tracking_id = temp_table.tracking_id AND properties.price_per_m2 = temp_table.price_per_m2)
        OR NOT EXISTS (SELECT 1 FROM properties);
    """)
    conn.commit()
    res = cursor.execute("""
        UPDATE properties
        SET last_update_date = (SELECT last_update_date FROM temp_table WHERE temp_table.tracking_id = properties.tracking_id)
        WHERE EXISTS (SELECT 1 FROM temp_table WHERE temp_table.tracking_id = properties.tracking_id);
    """)
    conn.commit()
    res = cursor.execute("DROP TABLE temp_table;")
    conn.commit()

    res = cursor.execute("DROP TABLE IF EXISTS properties_fact;")
    res = cursor.execute("""
    CREATE TABLE properties_fact AS 
    WITH latest_properties AS (
        SELECT 
            title, price, square_meters, price_per_m2, location, link, first_photo, processing_date, bathrooms, rooms, tracking_id, creation_date, last_update_date, 
            FIRST_VALUE(price_per_m2) OVER (PARTITION BY tracking_id ORDER BY creation_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS first_price_per_m2, 
            FIRST_VALUE(creation_date) OVER (PARTITION BY tracking_id ORDER BY creation_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS first_price_date, 
            LAST_VALUE(price_per_m2) OVER (PARTITION BY tracking_id ORDER BY creation_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS last_price_per_m2, 
            LAST_VALUE(creation_date) OVER (PARTITION BY tracking_id ORDER BY creation_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS last_price_date, 
            MIN(price_per_m2) OVER (PARTITION BY tracking_id) AS min_price_per_m2, 
            FIRST_VALUE(creation_date) OVER (PARTITION BY tracking_id ORDER BY price_per_m2 ASC, creation_date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS min_price_date
        FROM properties
    )
    SELECT * FROM (
        SELECT *, 
        ROW_NUMBER() OVER(PARTITION BY tracking_id ORDER BY processing_date DESC) rn 
        FROM latest_properties
    ) 
    WHERE rn = 1
    """)
    conn.commit()

    # Close the connection to the SQLite database
    conn.close()

store_csv_to_sqlite('data/mercadolibre_scraped_data.csv')
