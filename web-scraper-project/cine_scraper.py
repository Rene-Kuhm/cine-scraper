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
        """Extraer información de una película desde un elemento HTML - Optimizado para sitios piratas latino"""
        pelicula = {}
        
        # Título - Selectores para sitios piratas (Cuevana, RepelisPlus, PelisPlus, etc.)
        titulo_elem = (
            pelicula_element.find('h2') or 
            pelicula_element.find('h3') or 
            pelicula_element.find('h4') or  # Para RepelisPlus
            pelicula_element.find('span', class_='title') or
            pelicula_element.find('h3', class_='title') or
            pelicula_element.find('a', class_='title') or
            pelicula_element.find('div', class_='Title') or
            pelicula_element.find(['h2', 'h3', 'h4', 'h1'], class_='title') or
            pelicula_element.find('a', href=True)  # Último recurso: tomar primer link
        )
        
        # Extraer texto del título
        if titulo_elem:
            titulo = titulo_elem.get_text(strip=True)
            if not titulo and titulo_elem.name == 'a':
                # Si es un link sin texto, intentar del alt de la imagen interna
                img_inside = titulo_elem.find('img')
                if img_inside and img_inside.get('alt'):
                    titulo = img_inside['alt']
            pelicula['titulo'] = titulo if titulo else 'Sin título'
        else:
            pelicula['titulo'] = 'Sin título'
        
        # Calidad/Resolución - Específico para sitios HD
        calidad_elem = (
            pelicula_element.find('span', class_='quality') or
            pelicula_element.find('span', class_='calidad') or
            pelicula_element.find('div', class_='quality') or
            pelicula_element.find('span', class_='hd') or
            pelicula_element.find('div', class_='hd')
        )
        pelicula['calidad'] = calidad_elem.get_text(strip=True) if calidad_elem else 'No especificada'
        
        # Género - Selectores para sitios en español
        genero_elem = (
            pelicula_element.find('span', class_='genre') or 
            pelicula_element.find('div', class_='genero') or
            pelicula_element.find('div', class_='Genre') or
            pelicula_element.find('span', class_='genres') or
            pelicula_element.find('p', class_='genre') or
            pelicula_element.find('span', class_='category')
        )
        pelicula['genero'] = genero_elem.get_text(strip=True) if genero_elem else 'No especificado'
        
        # Año/fecha - Múltiples formatos
        year_elem = (
            pelicula_element.find('span', class_='year') or
            pelicula_element.find('span', class_='date') or
            pelicula_element.find('span', class_='release_date') or
            pelicula_element.find('div', class_='year') or
            pelicula_element.find('span', class_='anio')
        )
        pelicula['anio'] = year_elem.get_text(strip=True) if year_elem else 'No especificado'
        
        # Duración
        duracion_elem = (
            pelicula_element.find('span', class_='duration') or 
            pelicula_element.find('div', class_='duracion') or
            pelicula_element.find('span', class_='runtime') or
            pelicula_element.find('time') or
            pelicula_element.find('div', class_='Duration')
        )
        pelicula['duracion'] = duracion_elem.get_text(strip=True) if duracion_elem else 'No especificada'
        
        # Rating/Calificación
        rating_elem = (
            pelicula_element.find('span', class_='rating') or 
            pelicula_element.find('div', class_='clasificacion') or
            pelicula_element.find('div', class_='user_score_chart') or
            pelicula_element.find('span', class_='vote_average') or
            pelicula_element.find('div', class_='Rating') or
            pelicula_element.find('div', class_='vote') or
            pelicula_element.find('span', class_='imdb') or
            pelicula_element.find('div', class_='score') or
            pelicula_element.find('span', class_='stars')
        )
        pelicula['rating'] = rating_elem.get_text(strip=True) if rating_elem else 'No especificado'
        
        # Idioma/Calidad específica para latino
        idioma_elem = (
            pelicula_element.find('span', class_='language') or
            pelicula_element.find('span', class_='audio') or
            pelicula_element.find('div', class_='idioma') or
            pelicula_element.find('span', class_='latino') or
            pelicula_element.find('span', class_='espanol') or
            pelicula_element.find('div', class_='quality')  # A veces incluye idioma
        )
        pelicula['idioma'] = idioma_elem.get_text(strip=True) if idioma_elem else 'No especificado'
        
        # Enlace directo al video o página de detalle
        link_elem = (
            pelicula_element.find('a', href=True) or
            pelicula_element.find('a', class_='image') or
            pelicula_element.find('a', class_='title') or
            pelicula_element.find('a', class_='play-button')
        )
        if link_elem and link_elem.get('href'):
            pelicula['link_streaming'] = link_elem['href']
        else:
            pelicula['link_streaming'] = 'No disponible'
        
        # Imagen del poster
        img_elem = pelicula_element.find('img')
        if img_elem:
            # Priorizar data-src para lazy loading
            pelicula['imagen'] = (
                img_elem.get('data-src') or 
                img_elem.get('src') or
                img_elem.get('data-srcset', '').split()[0] or
                'No disponible'
            )
        else:
            pelicula['imagen'] = 'No disponible'
        
        # Sinopsis - Generalmente en página de detalle
        sinopsis_elem = (
            pelicula_element.find('p', class_='synopsis') or 
            pelicula_element.find('div', class_='sinopsis') or
            pelicula_element.find('p', class_='overview') or
            pelicula_element.find('div', class_='overview') or
            pelicula_element.find('div', class_='description') or
            pelicula_element.find('p', class_='description')
        )
        pelicula['sinopsis'] = sinopsis_elem.get_text(strip=True) if sinopsis_elem else 'Sin sinopsis'
        
        return pelicula
    
    def scrape_cine_page(self, url):
        """Scrapear una página de cine específica"""
        print(f"Scrapeando: {url}")
        
        html_content = self.get_page(url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar contenedores de películas - Optimizado para sitios piratas latino
        peliculas_selectors = [
            ('div', 'pelicula'),           # Genérico español
            ('div', 'movie'),             # Inglés
            ('div', 'film'),              # Inglés  
            ('article', 'movie'),          # TMDB y otros
            ('div', 'card'),              # Bootstrap/moderno
            ('div', 'item'),              # Genérico
            ('div', 'movie-item'),        # Específico
            ('li', 'movie'),              # Listas
            ('div', 'post'),              # WordPress
            ('div', 'ksaj'),              # RepelisPlus específico
            ('div', 'result'),            # Resultados búsqueda
            ('div', 'video'),             # Contenido video
            ('div', 'entry'),             # WordPress entry
            ('div', 'content-item'),      # Item de contenido
        ]
        
        peliculas_elements = []
        for tag, class_name in peliculas_selectors:
            elements = soup.find_all(tag, class_=class_name)
            if elements:
                peliculas_elements.extend(elements)
                break  # Tomar el primero que encuentre
        
        # Si no encontramos contenedores específicos, buscar cualquier div con imágenes de películas
        if not peliculas_elements:
            # Buscar divs con imágenes que parezcan posters
            all_images = soup.find_all('img')
            for img in all_images:
                parent = img.parent
                if parent and parent.name in ['a', 'div']:
                    src = img.get('src', '') or img.get('data-src', '')
                    if src:
                        src_lower = src.lower()
                        if ('poster' in src_lower or 'movie' in src_lower or 'peli' in src_lower):
                            peliculas_elements.append(parent)
                            if len(peliculas_elements) >= 20:  # Limitar para evitar spam
                                break
        
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

# URLs de mejores sitios piratas para películas en español latino Full HD
CINE_URLS = [
    # TMDB - Base de datos oficial (solo para referencias)
    'https://www.themoviedb.org/movie',
    
    # CUEVANA 3 - El más popular para streaming latino HD
    'https://www3.cuevana3.to/',
    'https://ww9.cuevana3.to/',
    'https://znr.cuevana.pro/',
    'https://cuevanav3.com/',
    'https://es.cuevana3i.org/',
    
    # REPELISPLUS - Excelente alternativa, full HD latino
    'https://repelisplus.lat/',
    'https://repelisplus.hair/',
    'https://repelisplus.my/',
    
    # PELISPLUS HD - Streaming en alta calidad
    'https://ww3.pelisplushd.to/',
    'https://www.pelisplushd.ms/',
    
    # PELISPEDIA - Gran catálogo en español
    'https://pelispedia.mov/',
    'https://repelispedia.lat/',
    
    # GNULA - Clásico para películas latino
    'https://gnula.nu/',
    'https://gnula.se/',
    
    # DIVXTOTAL - Descargas y streaming
    'https://divxtotal.to/',
    'https://divxtotal.es/',
    
    # INFILIX - Nueva opción popular
    'https://infilix.com/',
    'https://infilix.me/',
    
    # CINETUX - Películas en español latino
    'https://cinetux.to/',
    'https://cinetux.io/',
    
    # TORRENT sites para magnet links
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