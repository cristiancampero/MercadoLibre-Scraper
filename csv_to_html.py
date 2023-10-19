
import csv
import os

def create_html_page(page_number=1, properties_per_page=60, file_path='data\mercadolibre_scraped_data.csv'):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            if float(row['price'].replace(',', '')) <= 100000 and 'departamento' in row['title'].lower():
                data.append(row)

    start_index = (page_number - 1) * properties_per_page
    end_index = start_index + properties_per_page
    page_data = data[start_index:end_index]

    os.makedirs('html', exist_ok=True)
    with open(f'html/properties_{page_number}.html', 'w', encoding='utf-8') as file:
        file.write('<style>.property-card {display: flex; margin: 10px;}</style>\n')
        file.write('<style>.property-text {margin-left: 10px;}</style>\n')
        for index, property in enumerate(page_data):
            file.write('<div class="property-card">\n')
            file.write('<img src="' + property['first_photo'] + '" alt="Property photo" style="width: 400px; height: 250px;">\n')
            file.write('<div class="property-text">\n')
            file.write('<h1>' + property['title'] + '</h1>\n')
            file.write('<p>Price: ' + property['price'] + '</p>\n')
            file.write('<p>Rooms: ' + property['rooms'] + '</p>\n')
            file.write('<p>Bathrooms: ' + property['bathrooms'] + '</p>\n')
            file.write('<p>Square Meters: ' + property['square_meters'] + '</p>\n')
            file.write('<p>Price per m2: ' + property['price_per_m2'] + '</p>\n')
            file.write('<p>Location: ' + property['location'] + '</p>\n')
            file.write('<a href="' + property['link'] + '" target="_blank">Link</a>\n')
            file.write('</div>\n')
            file.write('</div>\n')
            file.write('<hr>\n')
        file.write('<div style="text-align:center; margin: 50px;">\n')
        if page_number > 1:
            file.write('<a href="properties_' + str(page_number - 1) + '.html" style="margin-right: 20px; font-size: 20px;">Previous</a>\n')
        if len(data) > end_index:
            file.write('<a href="properties_' + str(page_number + 1) + '.html" style="font-size: 20px;">Next</a>\n')
        file.write('</div>\n')
for i in range(1, 6):  # Create first 10 pages
    create_html_page(i)
