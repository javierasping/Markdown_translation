# @name: translate.py
# @creation_date: 2023-08-24
# @license: GNU Affero General Public License, Version 3 <https://www.gnu.org/licenses/agpl-3.0.en.html>
# @author: Simon Bowie <ad7588@coventry.ac.uk>
# @purpose: Sends batches of Markdown files to a locally-running LibreTranslate API and outputs translated Markdown files
# @acknowledgements:

import json
from pathlib import Path
import re
import requests
import frontmatter  # pip install python-frontmatter

# VARIABLES
input_language = 'es'
output_language = 'en'
url = "http://localhost:5000/translate"
base_directory = Path('/home/javiercruces/Documentos/sentinel/content/posts')

# Modifica los directorios de entrada y salida según la estructura de tu directorio
input_directory = base_directory 

# SUBROUTINES

# function to extract and replace text that we do not want translated (specifically anything between ``` and ``` code blocks)
def preprocess_text(text, placeholders):
    # placeholder pattern (you can customize this)
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    for i, match in enumerate(matches):
        placeholder = f'__PLACEHOLDER_{i}__'
        placeholders[placeholder] = match
        text = text.replace(f'```{match}```', placeholder)
    return text

# function to reinsert the original segments back into the text
def postprocess_text(translated_text, placeholders):
    for placeholder, original_text in placeholders.items():
        translated_text = translated_text.replace(placeholder, f'```{original_text}```')
    return translated_text

# function to translate text using LibreTranslate API
def translate_text(text, input_language, output_language):
    # build Json payload to send to LibreTranslate API
    payload = {
        "q": text,
        "source": input_language,
        "target": output_language,
        "format": "html",
        "api_key": ""
    }
    headers = {"Content-Type": "application/json"}

    # send payload to LibreTranslate API
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    # Verificar la respuesta de la API
    if response.status_code == 200:
        return response.json()['translatedText']
    else:
        print(f"Error with translation: {response.text}")
        return text

# Function to check if a line starts with ![](
def is_image_line(line):
    return line.lstrip().startswith("![](")

# MAIN PROGRAM

print(f"Starting translation from {input_language} to {output_language}...")

# iterate over files with .md suffix in the input directory
for file_path in Path(input_directory).rglob("*.md"):
    print(f"Processing file: {file_path}")

    # read Markdown file
    text = frontmatter.load(file_path)

    placeholders = {}

    # Preprocess text content of Markdown file to replace not-to-be-translated segments of text with placeholders
    print(f"Preprocessing content of {file_path.name}")
    text.content = preprocess_text(text.content, placeholders)

    # Split content into lines and check if any line starts with ![]( to skip it
    lines = text.content.splitlines()
    processed_lines = []

    for line in lines:
        if is_image_line(line):  # If it's an image link, don't translate
            processed_lines.append(line)
        else:
            # Translate non-image lines
            processed_lines.append(translate_text(line, input_language, output_language))

    # Join the lines back together into a single string
    text.content = "\n".join(processed_lines)

    # Postprocess to reinsert the original segments
    print(f"Postprocessing content of {file_path.name}")
    text.content = postprocess_text(text.content, placeholders)

    # Create the new file path with the ".en.md" suffix in the same directory as the original
    write_file_path = file_path.with_name(file_path.stem + '.en.md')
    print(f"Writing translated file to: {write_file_path}")
    
    # write new Markdown file in the same directory as the original
    with open(write_file_path, 'w') as f:
        f.write(frontmatter.dumps(text))

print(f"Translation completed.")
