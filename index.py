import frontmatter

# Función para verificar si el archivo es un _index.md
def is_index_file(file_name):
    return file_name.startswith("_index.md")

# Función para procesar archivos _index.md
def process_index_file(file_path, input_language, output_language, translate_text):
    # Cargar el contenido del archivo Markdown
    text = frontmatter.load(file_path)
    
    # Extraer el contenido YAML
    yaml_content = text.metadata

    # Traducir el título si existe
    if 'title' in yaml_content:
        yaml_content['title'] = translate_text(yaml_content['title'], input_language, output_language)

    # Verificar la existencia de 'menu' y 'sidebar' antes de acceder a ellos
    if isinstance(yaml_content.get('menu'), dict):
        menu_content = yaml_content['menu']
        
        if isinstance(menu_content.get('sidebar'), dict):
            sidebar = menu_content['sidebar']
            
            # Traducir el campo 'name' si existe
            if 'name' in sidebar:
                sidebar['name'] = translate_text(sidebar['name'], input_language, output_language)

    # Asegurar que se mantenga la estructura original del YAML
    translated_yaml_content = {
        'title': yaml_content.get('title', '')  # Mantiene 'title', aunque no exista en algunos casos
    }
    
    if 'menu' in yaml_content:  # Solo agrega 'menu' si existe en el original
        translated_yaml_content['menu'] = yaml_content['menu']

    # Asignamos el contenido traducido de vuelta al texto
    text.metadata = translated_yaml_content

    # Escribir el archivo traducido
    write_file_path = file_path.with_name(file_path.stem + f'.{output_language}.md')
    with open(write_file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(text))
    
    print(f"Archivo _index.md traducido guardado en: {write_file_path}")