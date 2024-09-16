# Este script busca los archivos YAML de una carpeta y guarda todos ellos en otra carpeta

import os
import shutil

def buscar_archivos_yaml(directorio_raiz):
    archivos_yaml = []
    for root, dirs, files in os.walk(directorio_raiz):
        for file in files:
            if file.endswith('.yaml'):
                archivos_yaml.append(os.path.join(root, file))
    return archivos_yaml

def generar_nombre_unico(dest, nombre_archivo):
    nombre, extension = os.path.splitext(nombre_archivo)
    contador = 1
    nuevo_nombre = nombre_archivo
    while os.path.exists(os.path.join(dest, nuevo_nombre)):
        nuevo_nombre = f"{nombre}{contador}{extension}"
        contador += 1
    return nuevo_nombre

def main(root, dest):
    print(f'Buscando archivos yaml...')
    directorio_raiz = root  
    if not os.path.exists(dest):
        os.makedirs(dest)
    archivos_yaml = buscar_archivos_yaml(directorio_raiz)

    # copiar los archivos .yaml encontrados
    for archivo in archivos_yaml:
        nombre_archivo = os.path.basename(archivo)
        nombre_unico = generar_nombre_unico(dest, nombre_archivo)
        shutil.copy2(archivo, os.path.join(dest, nombre_unico))
    print(f"se han copiado {len(archivos_yaml)} archivos")
    return len(archivos_yaml)

# Llamada de prueba a la función main
# main('/ruta/de/origen', '/ruta/de/destino')


