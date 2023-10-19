import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import subprocess
import shutil

class Scraper():

    def menu(self):
        self.base_url = 'https://listado.mercadolibre.com.ar/'


    def extract_property_info(self, soup):
        property_info = {}

        try:
            property_info['title'] = soup.find('h2', class_='ui-search-item__title').text
        except AttributeError:
            property_info['title'] = None

        try:
            price_text = soup.find('span', class_='andes-money-amount__fraction').text
            property_info['price'] = float(price_text.replace('.', ''))
        except (AttributeError, ValueError):
            property_info['price'] = None

        try:
            attributes = soup.find_all('li', class_='ui-search-card-attributes__attribute')
            for attribute in attributes:
                attribute_text = attribute.text
                if 'm²' in attribute_text:
                    property_info['square_meters'] = ''.join(filter(str.isdigit, attribute_text.split(' ')[0]))
                elif 'amb.' in attribute_text:
                    property_info['rooms'] = attribute_text
                elif 'baño' in attribute_text:
                    property_info['bathrooms'] = attribute_text
        except AttributeError:
            property_info['rooms'] = None
            property_info['bathrooms'] = None
            property_info['square_meters'] = None

        try:
            price = property_info.get('price')
            square_meters = property_info.get('square_meters')
            if price and square_meters:
                property_info['price_per_m2'] = float(price) / float(square_meters)
            else:
                property_info['price_per_m2'] = None
        except (AttributeError, ValueError, IndexError):
            property_info['price_per_m2'] = None

        try:
            property_info['location'] = soup.find('span', class_='ui-search-item__location-label').text
        except AttributeError:
            property_info['location'] = None

        try:
            link_element = soup.find('a', class_='ui-search-link')
            if link_element is not None and 'href' in link_element.attrs:
                property_info['link'] = link_element['href']
            else:
                property_info['link'] = None
        except AttributeError:
            property_info['link'] = None

        try:
            first_photo_element = soup.find('img', class_='ui-search-result-image__element')
            property_info['first_photo'] = first_photo_element['data-src'] if first_photo_element else None
        except AttributeError:
            property_info['first_photo'] = None

        return property_info

    def scraping(self, product_name):
        # Clean the user input
        cleaned_name = product_name.replace(" ", "-").lower()
        # Create the urls to scrap
        urls = [self.base_url + cleaned_name]

        page_number = 50
        for i in range(0, 10000, 50):
            urls.append(f"{self.base_url}{cleaned_name}_Desde_{page_number + 1}_NoIndex_True")
            page_number += 50

        # create a list to save the data
        self.data = []
        # create counter
        c = 1
            
        # Iterate over each url
        for i, url in enumerate(urls, start=1):

            # Get the html of the page
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
                
            # take all posts
            content = soup.find_all('li', class_='ui-search-layout__item')
            
            # Check if there's no content to scrape
            if not content:
                print("\nTermino el scraping.")
                break

            print(f"\nScrapeando pagina numero {i}. {url}")
            
            
            # iteration to scrape posts
            for post in content:
                post_data = self.extract_property_info(post)
                # save the dictionaries in a list
                self.data.append(post_data)
                c += 1

        for i, post_data in enumerate(self.data):
            if post_data['price_per_m2'] == 1000:
                print(f"Scrappeando propiedad numero {i}: {post_data['link']}")
                response = requests.get(post_data['link'])
                soup = BeautifulSoup(response.text, 'html.parser')
                new_post_data = self.extract_property_info(soup)
                post_data.update(new_post_data)

                    
    def export_to_csv(self):
        # export to a csv file
        df = pd.DataFrame(self.data)
        # prevent the index to be stored in the csv
        df.to_csv(r"data/mercadolibre_scraped_data.csv", sep=";", index=False)

if __name__ == "__main__":
    s = Scraper()
    s.menu()
    s.scraping('inmuebles en venta en monte grande')
    # Sort self.data by price_per_m2 from lowest to highest
    from datetime import date
    # Filter out entries where 'price_per_m2' is None
    s.data = [x for x in s.data if x['price_per_m2'] is not None]
    # Sort the data by 'price_per_m2' from lowest to highest
    s.data.sort(key=lambda x: x['price_per_m2'])
    # Add the processing date to the data
    processing_date = date.today().strftime("%Y-%m-%d")
    for item in s.data:
        item['processing_date'] = processing_date
    # Export the data to a CSV file
    s.export_to_csv()

    # Run the analytics.py script
#    subprocess.run(["python", "analytics.py"])

