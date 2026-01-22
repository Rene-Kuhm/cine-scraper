import requests
from bs4 import BeautifulSoup
import csv
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
        
        # Título - Selectores múltiples para diferentes sitios
        titulo_elem = (
            pelicula_element.find('h2') or 
            pelicula_element.find('h3') or 
            pelicula_element.find('span', class_='title') or
            pelicula_element.find('h3', class_='title') or
            pelicula_element.find('a', class_='title') or
            pelicula_element.find('div', class_='Title') or
            pelicula_element.find(['h2', 'h3', 'h1'], class_='title')
        )
        pelicula['titulo'] = titulo_elem.get_text(strip=True) if titulo_elem else 'Sin título'
        
        # Género - Selectores específicos para diferentes sitios
        genero_elem = (
            pelicula_element.find('span', class_='genre') or 
            pelicula_element.find('div', class_='genero') or
            pelicula_element.find('div', class_='Genre') or
            pelicula_element.find('span', class_='genres') or
            pelicula_element.find('p', class_='genre')
        )
        pelicula['genero'] = genero_elem.get_text(strip=True) if genero_elem else 'No especificado'
        
        # Duración
        duracion_elem = (
            pelicula_element.find('span', class_='duration') or 
            pelicula_element.find('div', class_='duracion') or
            pelicula_element.find('span', class_='runtime') or
            pelicula_element.find('time') or
            pelicula_element.find('div', class_='Duration')
        )
        pelicula['duracion'] = duracion_elem.get_text(strip=True) if duracion_elem else 'No especificada'
        
        # Clasificación/Rating
        clasificacion_elem = (
            pelicula_element.find('span', class_='rating') or 
            pelicula_element.find('div', class_='clasificacion') or
            pelicula_element.find('div', class_='user_score_chart') or
            pelicula_element.find('span', class_='vote_average') or
            pelicula_element.find('div', class_='Rating')
        )
        pelicula['clasificacion'] = clasificacion_elem.get_text(strip=True) if clasificacion_elem else 'No especificada'
        
        # Sinopsis
        sinopsis_elem = (
            pelicula_element.find('p', class_='synopsis') or 
            pelicula_element.find('div', class_='sinopsis') or
            pelicula_element.find('p', class_='overview') or
            pelicula_element.find('div', class_='overview') or
            pelicula_element.find('div', class_='Description')
        )
        pelicula['sinopsis'] = sinopsis_elem.get_text(strip=True) if sinopsis_elem else 'Sin sinopsis'
        
        # Enlace a página de detalle
        link_elem = (
            pelicula_element.find('a', href=True) or
            pelicula_element.find('a', class_='image') or
            pelicula_element.find('a', class_='title')
        )
        pelicula['link_detalle'] = link_elem['href'] if link_elem else 'No disponible'
        
        # Imagen
        img_elem = pelicula_element.find('img')
        pelicula['imagen'] = img_elem['src'] if img_elem and img_elem.get('src') else 'No disponible'
        
        # Año
        year_elem = (
            pelicula_element.find('span', class_='release_date') or
            pelicula_element.find('div', class_='year') or
            pelicula_element.find('span', class_='date')
        )
        pelicula['anio'] = year_elem.get_text(strip=True) if year_elem else 'No especificado'
        
        return pelicula
    
    def scrape_cine_page(self, url):
        """Scrapear una página de cine específica"""
        print(f"Scrapeando: {url}")
        
        html_content = self.get_page(url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar contenedores de películas - Selectores múltiples para diferentes sitios
        peliculas_elements = (
            soup.find_all('div', class_='pelicula') or 
            soup.find_all('article', class_='movie') or 
            soup.find_all('div', class_='film') or
            soup.find_all('div', class_='card') or
            soup.find_all('div', class_='item') or
            soup.find_all('div', class_='movie-item') or
            soup.find_all('li', class_='movie') or
            soup.find_all('div', class_='post') or
            soup.find_all('article') or
            soup.find_all('div', class_='result')
        )
        
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
        
        # Obtener los encabezados (keys) del primer diccionario
        if self.peliculas:
            fieldnames = self.peliculas[0].keys()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.peliculas)
                
        print(f"Guardadas {len(self.peliculas)} películas en {filename}")
    
    def scrape_multiple_urls(self, urls):
        """Scrapear múltiples URLs de cine"""
        for url in urls:
            peliculas = self.scrape_cine_page(url)
            self.peliculas.extend(peliculas)
            
            # Espera aleatoria para no sobrecargar el servidor
            time.sleep(random.uniform(1, 3))
        
        print(f"Total de películas scrapeadas: {len(self.peliculas)}")

# URLs de sitios de streaming y torrents populares
CINE_URLS = [
    # The Movie Database (TMDB) - Popular movies
    'https://www.themoviedb.org/movie',
    
    # Cuevana - Streaming (dominios pueden cambiar)
    'https://znr.cuevana.pro/',
    'https://cuevana3.site/',
    'https://www.cuevana.to/',
    
    # PelisPlus - Alternativa streaming
    'https://pelisplus.so/',
    'https://pelisplus2.me/',
    
    # Series y películas alternativas
    'https://www.pelis24.se/',
    'https://repelisplus.so/',
    
    # Torrent sites (para magnet links)
    'https://yts.mx/browse-movies',
    'https://1337x.to/movies/',
    'https://thepiratebay.org/browse/201',
]

if __name__ == "__main__":
    scraper = CineScraper()
    
    # Ejemplo de uso
    if CINE_URLS:
        scraper.scrape_multiple_urls(CINE_URLS)
        scraper.save_to_csv()
    else:
        print("Agrega URLs de sitios de cine en la lista CINE_URLS")