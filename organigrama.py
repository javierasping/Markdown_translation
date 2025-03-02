import frontmatter
import yaml
from pathlib import Path

# Función para procesar el archivo _index.md de cada carpeta
def process_index_file(file_path):
    text = frontmatter.load(file_path)
    yaml_content = text.metadata
    
    # Recogemos el 'menu' si está presente
    if 'menu' in yaml_content and 'sidebar' in yaml_content['menu']:
        return yaml_content['menu']['sidebar']
    return None

# Función para procesar los archivos .md de cada post
def process_post_file(file_path):
    text = frontmatter.load(file_path)
    yaml_content = text.metadata
    
    if 'title' in yaml_content and 'identifier' in yaml_content:
        return {
            'title': yaml_content['title'],
            'identifier': yaml_content['identifier']
        }
    return None

# Función para construir el organigrama jerárquico basado en los archivos en el directorio
def build_org_chart(directory):
    org_chart = {}
    
    # Procesamos las carpetas principales en content/posts/
    for main_dir in Path(directory).iterdir():
        if main_dir.is_dir():
            category_name = main_dir.name
            category_data = {
                'title': category_name.replace('_', ' ').title(),  # Formato de nombre
                'identifier': category_name,
                'children': []
            }

            # Buscar el archivo _index.md en la categoría
            index_file = main_dir / "_index.md"
            if index_file.exists():
                index_data = process_index_file(index_file)
                if index_data:
                    category_data['title'] = index_data.get('name', category_data['title'])

            # Procesar los subdirectorios (posts) dentro de esta categoría
            for sub_dir in main_dir.iterdir():
                if sub_dir.is_dir():
                    post_data = process_post_file(sub_dir / "_index.md")
                    if post_data:
                        category_data['children'].append(post_data)
            
            org_chart[category_name] = category_data
    
    return org_chart

# Función para guardar el organigrama en formato YAML
def save_org_chart(org_chart, output_file):
    with open(output_file, 'w') as yaml_file:
        yaml.dump(org_chart, yaml_file, default_flow_style=False, allow_unicode=True)

# Directorios y archivo de salida
input_directory = "/home/javiercruces/Documentos/sentinel/content/posts"  # Cambia esta ruta a la ruta correcta
output_file = "organigrama.yaml"

# Generar el organigrama
org_chart = build_org_chart(input_directory)

# Guardar el resultado en un archivo YAML
save_org_chart(org_chart, output_file)

print(f"El organigrama ha sido guardado en {output_file}.")