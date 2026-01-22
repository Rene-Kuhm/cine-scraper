# Cine Scraper

Proyecto para scrapear información de películas de sitios web de cines.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

1. Edita el archivo `cine_scraper.py` y agrega las URLs de los sitios de cine que quieres scrapear en la lista `CINE_URLS`
2. Ejecuta el scraper:
```bash
python cine_scraper.py
```

## Configuración

Deberás ajustar los selectores CSS en los métodos:
- `extract_pelicula_info()` - para adaptar al HTML específico de cada sitio
- `scrape_cine_page()` - para encontrar los contenedores de películas correctos

## Output

Los resultados se guardarán en `peliculas.csv`

## Sitios soportados (ejemplos)
- Cinepolis
- Cinemex  
- Cinemark
- (Adaptable a cualquier sitio de cine)