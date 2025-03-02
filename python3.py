import requests
import os

# Configuración de la API de LibreTranslate
API_URL = "http://localhost:5000/translate"
SOURCE_LANGUAGE = "es"  # Idioma de origen (inglés)
TARGET_LANGUAGE = "en"  # Idioma de destino (español)

# Función para traducir el contenido usando la API
def translate_text(text, source_lang, target_lang):
    response = requests.post(API_URL, data={
        'q': text,
        'source': source_lang,
        'target': target_lang,
        'format': 'text'
    })
    
    if response.status_code == 200:
        return response.json()['translatedText']
    else:
        print(f"Error al traducir: {response.status_code}")
        return None

# Función para traducir archivos Markdown
def translate_markdown_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    translated_content = translate_text(markdown_content, SOURCE_LANGUAGE, TARGET_LANGUAGE)
    
    if translated_content:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        print(f"Archivo traducido guardado en: {output_file}")
    else:
        print("No se pudo traducir el archivo.")

# Función para recorrer los archivos en un directorio y traducirlos
def translate_directory(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".md"):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                print(f"Traduciendo {input_path}...")
                translate_markdown_file(input_path, output_path)

# Directorios de entrada y salida
input_directory = "input_markdown"  # Directorio con los archivos Markdown originales
output_directory = "output_markdown"  # Directorio donde guardarás los archivos traducidos

# Traducir todos los archivos en el directorio
translate_directory(input_directory, output_directory)
