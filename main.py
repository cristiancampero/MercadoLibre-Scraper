import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

class Scraper():

    def menu(self):
        menu = ("""
    Escoge el país:
    1. Argentina
    2. Bolivia
    3. Brasil
    4. Chile
    5. Colombia
    6. Costa Rica
    7. Dominicana
    8. Ecuador
    9. Guatemala
    10. Honduras
    11. México
    12. Nicaragua
    13. Panamá
    14. Paraguay
    15. Perú
    16. Salvador
    17. Uruguay
    18. Venezuela
        """)

        valid_options = list(range(1, 19))

        while True:
            print(menu)
            opcion = int(input('Número de país (Ejemplo: 5): '))

            if opcion in valid_options:

                urls = {
                1: 'https://listado.mercadolibre.com.ar/',
                2: 'https://listado.mercadolibre.com.bo/',
                3: 'https://listado.mercadolibre.com.br/',
                4: 'https://listado.mercadolibre.cl/',
                5: 'https://listado.mercadolibre.com.co/',
                6: 'https://listado.mercadolibre.com.cr/',
                7: 'https://listado.mercadolibre.com.do/',
                8: 'https://listado.mercadolibre.com.ec/',
                9: 'https://listado.mercadolibre.com.gt/',
                10: 'https://listado.mercadolibre.com.hn/',
                11: 'https://listado.mercadolibre.com.mx/',
                12: 'https://listado.mercadolibre.com.ni/',
                13: 'https://listado.mercadolibre.com.pa/',
                14: 'https://listado.mercadolibre.com.py/',
                15: 'https://listado.mercadolibre.com.pe/',
                16: 'https://listado.mercadolibre.com.sv/',
                17: 'https://listado.mercadolibre.com.uy/',
                18: 'https://listado.mercadolibre.com.ve/',
                }

                self.base_url = urls[opcion]
                break
            else:
                print("Escoge un número del 1 al 18")



    def scraping(self):
        # User search
        product_name = input("\nProducto: ")
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
                # get the title
                title = post.find('h2').text
                # get the price
                price = post.find('span', class_='andes-money-amount__fraction').text
                # get the url post
                post_link = post.find("a")["href"]
                # get the url image
                try:
                    img_link = post.find("img")["data-src"]
                except:
                    img_link = post.find("img")["src"]
                
                # show the data already scraped
                # print(f"{c}. {title}, {price}, {post_link}, {img_link}")

                # save in a dictionary
                post_data = {
                    "title": title,
                    "price": price,
                    "post link": post_link,
                    "image link": img_link            
                }
                # save the dictionaries in a list
                self.data.append(post_data)
                c += 1

    def export_to_csv(self):
        # export to a csv file
        df = pd.DataFrame(self.data)
        df.to_csv(r"data/mercadolibre_scraped_data.csv", sep=";")

if __name__ == "__main__":
    s = Scraper()
    s.menu()
    s.scraping()
    s.export_to_csv()
