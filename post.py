import re

def process_non_index_file(file_path, input_language, output_language, translate_text):
    # Leer el archivo y procesar línea por línea
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Lista para almacenar el contenido traducido
    translated_lines = []
    
    # Líneas que deben ser respetadas (1, 3, 5, 6, 7) – indexadas desde 1
    lines_to_skip = {1, 3, 5, 6, 7}  # Usamos un conjunto para mejorar la eficiencia de la búsqueda
    
    # Función para restaurar el formato del título (sin espacios entre # y el título)
    def restore_title_format(line):
        # Buscar líneas que empiecen con 1 a 5 #
        match = re.match(r"^(#{1,5})\s*(.*)$", line)  # Buscar títulos de 1 a 5 #
        if match:
            hashes = match.group(1)  # El símbolo # o los símbolos #
            title = match.group(2).strip()  # El texto del título
            return f"{hashes}{title}\n"  # Restauramos el formato sin espacios entre los # y el título
        return line

    # Función para reemplazar el símbolo ♪ ♪ por el número adecuado de #
    def replace_music_notes_with_hashes(line):
        # Buscamos el patrón ♪ ♪ (se puede repetir uno o más veces)
        pattern = r"(♪\s*){2,}"  # Buscamos 2 o más símbolos ♪
        match = re.search(pattern, line)
        
        if match:
            num_of_notes = len(match.group(0).strip().split())  # Contamos cuántos ♪ hay
            num_of_hashes = num_of_notes + 1  # Añadimos 1 al número de ♪ para obtener los # correspondientes
            line = line.replace(match.group(0), "#" * num_of_hashes + " ")  # Reemplazamos los ♪ por # y añadimos un espacio
        
        return line

    # Procesar cada línea y traducir
    for idx, line in enumerate(lines, start=1):  # Usamos enumerate para contar las líneas
        stripped_line = line.strip()  # Eliminar saltos de línea y espacios innecesarios
        
        # Si la línea comienza con ![](
        if line.lstrip().startswith("![]("):
            translated_lines.append(line)  # Añadirla tal cual está, no traducirla
        elif idx in lines_to_skip:  # Si la línea es una de las que debemos respetar
            translated_lines.append(line)  # Añadirla tal cual está
        elif stripped_line:  # Si la línea no está vacía y no es una de las anteriores
            translated_line = translate_text(line, input_language, output_language)
            translated_lines.append(translated_line)  # Añadir la línea traducida tal cual
        else:
            translated_lines.append(line)  # Respetar la línea vacía y añadirla tal cual
    
    # Restaurar el formato de los títulos en el archivo traducido
    translated_lines = [restore_title_format(line) for line in translated_lines]
    
    # Reemplazar el símbolo ♪ ♪ por el número adecuado de #
    translated_lines = [replace_music_notes_with_hashes(line) for line in translated_lines]
    
    # Escribir el contenido traducido en un nuevo archivo
    translated_file_path = file_path.with_suffix(f'.{output_language}.md')
    
    with open(translated_file_path, 'w', encoding='utf-8') as translated_file:
        translated_file.write("".join(translated_lines))  # Usamos "".join() para mantener los saltos de línea originales
    
    print(f"Archivo traducido guardado como: {translated_file_path}")
