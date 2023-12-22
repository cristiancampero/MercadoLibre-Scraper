class UserInterface:

    BASE_URLS = {
        1: {'country': 'Argentina', 'domain': 'ar'},
        2: {'country': 'Bolivia', 'domain': 'bo'},
        3: {'country': 'Brasil', 'domain': 'br'},
        4: {'country': 'Chile', 'domain': 'cl'},
        5: {'country': 'Colombia', 'domain': 'co'},
        6: {'country': 'Costa Rica', 'domain': 'cr'},
        7: {'country': 'Dominicana', 'domain': 'do'},
        8: {'country': 'Ecuador', 'domain': 'ec'},
        9: {'country': 'Guatemala', 'domain': 'gt'},
        10: {'country': 'Honduras', 'domain': 'hn'},
        11: {'country': 'México', 'domain': 'mx'},
        12: {'country': 'Nicaragua', 'domain': 'ni'},
        13: {'country': 'Panamá', 'domain': 'pa'},
        14: {'country': 'Paraguay', 'domain': 'py'},
        15: {'country': 'Perú', 'domain': 'pe'},
        16: {'country': 'Salvador', 'domain': 'sv'},
        17: {'country': 'Uruguay', 'domain': 'uy'},
        18: {'country': 'Venezuela', 'domain': 've'},
    }

    def __init__(self, scraper):
        self.scraper = scraper

    def menu(self):
        print("\nSeleccioná el país:")
        for number, country_info in self.BASE_URLS.items():
            print(f"{number}. {country_info['country']}")

        try:
            opcion = int(input('Número de país (Ejemplo: 5): '))
        except ValueError:
            print("Por favor, elegí un número válido.")
            return

        if opcion not in self.BASE_URLS:
            print("Elegí un número válido del 1 al 18.")
            return

        domain = self.BASE_URLS[opcion]['domain']
        product_name = input("\nProducto: ")

        try:
            scraping_limit = int(input(f"\nCantidad máxima de productos a escrapear (por defecto: 1000): "))
        except ValueError:
            print("Valor inválido. Se usará el límite por defecto de 1000.")
            scraping_limit = 1000

        self.scraper.scrape_product_list(domain, product_name, scraping_limit)
        self.scraper.export_to_csv(product_name)