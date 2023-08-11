# <center>Proyecto de Web Scraping</center>



Este proyecto consiste en un script de Python que utiliza las librerías BeautifulSoup4 y Pandas y tiene como objetivo extraer datos de Mercado Libre utilizando técnicas de web scraping. El resultado final será un conjunto de datos estructurados en un archivo CSV que se pueden analizar y visualizar.

</br>

---
## Requisitos

Este proyecto requiere que se tenga instalado Python 3.x en el sistema y que se cuente con las siguientes librerías instaladas:

* BeautifulSoup4
* Pandas

Puedes instalar estas librerías usando pip. Para instalar todas las librerías requeridas, puedes usar cualquiera de los siguientes comandos:

```console
pip install -r requirements.txt
```

</br>

Este proyecto requiere que se cuente con el archivo `chromedriver.exe` en la ruta donde se ejecutará el script.

El archivo `chromedriver.exe` se utiliza para automatizar el navegador Google Chrome y se puede descargar desde el sitio web oficial de [ChromeDriver](https://chromedriver.chromium.org/downloads). Asegúrate de descargar la versión correcta de `chromedriver.exe` según la versión de Google Chrome que tengas instalada.

</br>

Tecnologías utilizadas

* Python
* Requests
* Beautiful Soup
* Pandas
* chromedriver.exe

</br>

---

## Uso

Para ejecutar el proyecto, primero abra un terminal y navegue hasta el directorio raíz del proyecto. Luego, ejecute el archivo main.py:

```console
python main.py
```



Esto abrira en navegador Google Chrome, iniciará el proceso de scraping y creará un archivo "data_mercadolibre.csv" en el directorio "data" con los datos extraídos.

