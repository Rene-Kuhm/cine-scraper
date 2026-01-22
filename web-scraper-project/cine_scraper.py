import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse

class CineScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        self.peliculas = []
    
    def get_page(self, url):
        """Obtener contenido de una página con manejo de errores"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error al acceder a {url}: {e}")
            return None
    
    def extract_pelicula_info(self, pelicula_element):
        """Extraer información de una película desde un elemento HTML"""
        pelicula = {}
        
        # Título (ejemplo genérico, ajustar según el sitio)
        titulo_elem = pelicula_element.find('h2') or pelicula_element.find('h3') or pelicula_element.find('span', class_='title')
        pelicula['titulo'] = titulo_elem.get_text(strip=True) if titulo_elem else 'Sin título'
        
        # Género
        genero_elem = pelicula_element.find('span', class_='genre') or pelicula_element.find('div', class_='genero')
        pelicula['genero'] = genero_elem.get_text(strip=True) if genero_elem else 'No especificado'
        
        # Duración
        duracion_elem = pelicula_element.find('span', class_='duration') or pelicula_element.find('div', class_='duracion')
        pelicula['duracion'] = duracion_elem.get_text(strip=True) if duracion_elem else 'No especificada'
        
        # Clasificación
        clasificacion_elem = pelicula_element.find('span', class_='rating') or pelicula_element.find('div', class_='clasificacion')
        pelicula['clasificacion'] = clasificacion_elem.get_text(strip=True) if clasificacion_elem else 'No especificada'
        
        # Sinopsis
        sinopsis_elem = pelicula_element.find('p', class_='synopsis') or pelicula_element.find('div', class_='sinopsis')
        pelicula['sinopsis'] = sinopsis_elem.get_text(strip=True) if sinopsis_elem else 'Sin sinopsis'
        
        return pelicula
    
    def scrape_cine_page(self, url):
        """Scrapear una página de cine específica"""
        print(f"Scrapeando: {url}")
        
        html_content = self.get_page(url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar contenedores de películas (ajustar según el sitio)
        peliculas_elements = soup.find_all('div', class_='pelicula') or soup.find_all('article', class_='movie') or soup.find_all('div', class_='film')
        
        page_peliculas = []
        for element in peliculas_elements:
            pelicula_info = self.extract_pelicula_info(element)
            if pelicula_info['titulo'] != 'Sin título':
                pelicula_info['url_origen'] = url
                page_peliculas.append(pelicula_info)
        
        return page_peliculas
    
    def save_to_csv(self, filename='peliculas.csv'):
        """Guardar películas a archivo CSV"""
        if not self.peliculas:
            print("No hay películas para guardar")
            return
        
        df = pd.DataFrame(self.peliculas)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Guardadas {len(self.peliculas)} películas en {filename}")
    
    def scrape_multiple_urls(self, urls):
        """Scrapear múltiples URLs de cine"""
        for url in urls:
            peliculas = self.scrape_cine_page(url)
            self.peliculas.extend(peliculas)
            
            # Espera aleatoria para no sobrecargar el servidor
            time.sleep(random.uniform(1, 3))
        
        print(f"Total de películas scrapeadas: {len(self.peliculas)}")

# URLs de ejemplo (ajustar según los sitios de cine reales)
CINE_URLS = [
    # Ejemplos genéricos - reemplazar con URLs reales
    # 'https://www.cinepolis.com/cartelera',
    # 'https://www.cinemex.com/cartelera',
    # 'https://www.cinemark.cl/cartelera'
]

if __name__ == "__main__":
    scraper = CineScraper()
    
    # Ejemplo de uso
    if CINE_URLS:
        scraper.scrape_multiple_urls(CINE_URLS)
        scraper.save_to_csv()
    else:
        print("Agrega URLs de sitios de cine en la lista CINE_URLS")