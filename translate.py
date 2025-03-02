import json
import requests
from pathlib import Path
from index import process_index_file
from post import process_non_index_file

# VARIABLES
input_language = 'es'
output_language = 'en'
url = "http://localhost:5000/translate"
input_directory = Path('/home/javiercruces/Documentos/test')

# Función para traducir texto utilizando la API de LibreTranslate
def translate_text(text, input_language, output_language):
    if not text.strip():
        return text
    
    payload = {
        "q": text,
        "source": input_language,
        "target": output_language,
        "format": "html",
        "api_key": ""
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        return response.json()['translatedText']
    else:
        print(f"Error con la traducción: {response.text}")
        return text

# Función para listar los archivos .md en un directorio y subdirectorios,
# y omitir aquellos que ya están traducidos
def list_md_files(directory, output_language):
    path = Path(directory)
    
    if not path.is_dir():
        raise ValueError(f"La ruta proporcionada no es un directorio válido: {directory}")
    
    # Usamos rglob para obtener todos los archivos .md
    md_files = list(path.rglob("*.md"))
    
    # Filtramos para omitir archivos que ya tienen el sufijo de idioma de salida (por ejemplo, .en.md)
    md_files = [file for file in md_files if not file.name.endswith(f'.{output_language}.md')]
    
    # Verificamos si el archivo traducido ya existe, si es así lo eliminamos de la lista
    md_files = [file for file in md_files if not file.with_suffix(f'.{output_language}.md').exists()]
    
    return md_files

# Función para contar archivos de cada idioma
def count_files_by_language(directory, languages):
    file_count = {lang: {"total": 0, "translated": 0, "pending": 0} for lang in languages}
    
    for file in Path(directory).rglob("*.md"):
        for lang in languages:
            # Para los archivos que tienen el sufijo del idioma (por ejemplo, .en.md)
            if file.name.endswith(f".{lang}.md"):  
                file_count[lang]["total"] += 1
                if file.with_suffix(f".{lang}.md").exists():
                    file_count[lang]["translated"] += 1
                else:
                    file_count[lang]["pending"] += 1
            # Si el archivo no tiene sufijo de idioma, contamos como pendiente en el idioma original
            elif lang == 'es' and not any(file.name.endswith(f".{l}.md") for l in languages):  # Archivos sin sufijo de idioma
                file_count[lang]["total"] += 1
                file_count[lang]["pending"] += 1
    
    return file_count

# Lista de archivos .md, excluyendo los que ya están traducidos
md_files = list_md_files(input_directory, output_language)

# print(f"Lista bruta: {list(Path(input_directory).rglob('*.md'))}")
# print(f"Lista neta: {md_files}")

# Estadísticas de archivos
languages = ['es', 'en']  # Idiomas que manejas
file_count = count_files_by_language(input_directory, languages)

# Mostrar estadísticas de archivos
print(f"Estadísticas de archivos:")
for lang, counts in file_count.items():
    print(f"Idioma: {lang}")
    print(f"  Total archivos: {counts['total']}")
    print(f"  Archivos traducidos: {counts['translated']}")
    print(f"  Archivos pendientes de traducir: {counts['pending']}")
    
# Ejecutar el script
print(f"Comenzando traducción de {input_language} a {output_language}...")

# Iterar sobre los archivos .md en el directorio de entrada
for file_path in md_files:

    # Verificar si el archivo es _index.md y procesarlo con el módulo index.py
    if file_path.name == "_index.md":
        print(f"Procesando archivo _index.md: {file_path.name}")
        process_index_file(file_path, input_language, output_language, translate_text)
    else:
        # Procesar cualquier otro archivo con el módulo post.py
        print(f"Procesando archivo no _index.md: {file_path.name}")
        process_non_index_file(file_path, input_language, output_language, translate_text)

print(f"Traducción completada.")