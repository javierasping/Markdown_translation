import json
from pathlib import Path
import re
import requests
import frontmatter  # pip install python-frontmatter

# VARIABLES
input_language = 'es'
output_language = 'en'
url = "http://localhost:5000/translate"
input_directory = Path('/home/javiercruces/Documentos/sentinel/content/posts')

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

        # Preserve the first 7 lines
        preserved_lines = lines[:7]
        lines = lines[7:]

        processed_lines = []

        for line in lines:
            if is_image_line(line):  # If it's an image link, don't translate
                processed_lines.append(line)
            else:
                # Translate non-image lines
                processed_lines.append(translate_text(line, input_language, output_language))

        # Postprocess to reinsert the original segments
        print(f"Postprocessing content of {file_path.name}")
        translated_content = postprocess_text("\n".join(processed_lines), placeholders)

        # Ensure proper formatting of the header
        fixed_header = []
        for line in preserved_lines:
            line = line.strip()
            if line.startswith("date:"):
                line = line.replace(" ", "").replace("T", "T").replace("+", "+")
                line = line.replace("date:", "date: ")  # Ensure a space after "date:"
            elif line.startswith("hero:"):
                line = line.replace(" / ", "/")
            elif line.startswith("#"):  # Process lines starting with "#"
                line = line.lstrip()  # Remove leading spaces
                # Remove any extra space between multiple '#' symbols
                line = line.replace("# #", "##")  # For title level 2 (e.g., ##)
                line = line.replace("# ##", "###")  # For title level 3 (e.g., ###)
                line = line.replace("# ###", "####")  # For title level 4 (e.g., ####)
                line = line.replace("# ####", "#####")  # For title level 5 (e.g., #####)
                line = line.replace("# #####", "######")  # For title level 6 (e.g., ######)
            else:
                line = translate_text(line, input_language, output_language)  # Ensure header fields are translated
            fixed_header.append(line)

        # Combine header and translated content
        text.content = "\n".join(fixed_header) + "\n" + translated_content

        # Create the new file path with the ".en.md" suffix in the same directory as the original
        write_file_path = file_path.with_name(file_path.stem + '.en.md')
        print(f"Writing translated file to: {write_file_path}")

        # Write new Markdown file in the same directory as the original
        with open(write_file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(text).lstrip("\ufeff"))  # Remove unwanted BOM characters

        # Now correct the titles in the file by removing the space after the '#'
        with open(write_file_path, 'r+', encoding='utf-8') as f:
            content = f.readlines()

            # Correct the titles by removing spaces between '#' and the title
            corrected_content = []
            for line in content:
                if line.lstrip().startswith("#"):  # Check if line is a header
                    # Remove any space between '#' symbols and the title
                    line = line.replace(" #", "#")  # Remove space between '#' symbols
                corrected_content.append(line)

            # Rewind and write the corrected content
            f.seek(0)
            f.truncate()  # Clear the file content
            f.writelines(corrected_content)  # Write the corrected lines back

            # Now, remove the first 5 lines and insert the '---'
            corrected_content = corrected_content[5:]  # Remove the first 5 lines
            corrected_content.insert(0, "---\n")  # Add the line with ---
            f.seek(0)  # Go back to the beginning of the file
            f.truncate()  # Clear the file content
            f.writelines(corrected_content)  # Write the remaining lines back

    print(f"Translation completed.")