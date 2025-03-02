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

# Function to check if the file is an _index.md file
def is_index_file(file_name):
    return file_name.startswith("_index.md")

# MAIN PROGRAM

print(f"Starting translation from {input_language} to {output_language}...")

# iterate over files with .md suffix in the input directory
for file_path in Path(input_directory).rglob("*.md"):
    print(f"Processing file: {file_path}")

    # read Markdown file
    text = frontmatter.load(file_path)

    # If the file is _index.md, only translate the YAML fields title and name
    if is_index_file(file_path.name):
        print(f"Processing _index.md file: {file_path.name}")
        
        # Extract YAML content and translate title and name fields
        yaml_content = text.metadata
        if 'title' in yaml_content:
            yaml_content['title'] = translate_text(yaml_content['title'], input_language, output_language)
        if 'menu' in yaml_content and 'sidebar' in yaml_content['menu'] and 'name' in yaml_content['menu']['sidebar']:
            yaml_content['menu']['sidebar']['name'] = translate_text(yaml_content['menu']['sidebar']['name'], input_language, output_language)
        
        # Save the modified YAML back to the text metadata
        text.metadata = yaml_content
        
        # Write the modified file back (only metadata changes)
        write_file_path = file_path.with_name(file_path.stem + '.en.md')
        print(f"Writing translated _index.md file to: {write_file_path}")
        with open(write_file_path, 'w') as f:
            f.write(frontmatter.dumps(text))
    
    else:
        # For non _index.md files, process the full content as usual
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