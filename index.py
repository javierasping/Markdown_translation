import frontmatter

# Función para verificar si el archivo es un _index.md
def is_index_file(file_name):
    return file_name.startswith("_index.md")

# Función para procesar archivos _index.md
def process_index_file(file_path, input_language, output_language, translate_text):
    # Cargar el contenido del archivo Markdown
    text = frontmatter.load(file_path)
    
    # Extraer y traducir el contenido YAML
    yaml_content = text.metadata
    
    # Traducir el título y el nombre del menú
    if 'title' in yaml_content:
        yaml_content['title'] = translate_text(yaml_content['title'], input_language, output_language)
    
    if 'menu' in yaml_content and 'sidebar' in yaml_content['menu']:
        sidebar = yaml_content['menu']['sidebar']
        if 'name' in sidebar:
            sidebar['name'] = translate_text(sidebar['name'], input_language, output_language)

    # Cambiar el orden del YAML para el caso específico de español a inglés
    if input_language == 'es' and output_language == 'en':
        # Orden correcto para el archivo en inglés
        translated_yaml_content = {
            'menu': yaml_content['menu'],
            'title': yaml_content['title']
        }
    else:
        # Para otros idiomas, no modificamos el orden
        translated_yaml_content = yaml_content

    # Asignamos el contenido traducido de vuelta al texto
    text.metadata = translated_yaml_content
    
    # Escribir el archivo traducido
    write_file_path = file_path.with_name(file_path.stem + '.en.md')
    with open(write_file_path, 'w') as f:
        f.write(frontmatter.dumps(text))
    print(f"Escribiendo archivo _index.md traducido en: {write_file_path}")