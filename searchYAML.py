# Este script busca los archivos YAML de una carpeta y guarda todos ellos en 
# otra carpeta

import os
import shutil

def buscar_archivos_yaml(directorio_raiz):
    archivos_yaml = []
    for root, dirs, files in os.walk(directorio_raiz):
        for file in files:
            if file.endswith('.yaml'):
                archivos_yaml.append(os.path.join(root, file))
    return archivos_yaml

def main(root, dest):
    print(f'Buscando archivos yaml...')
    directorio_raiz = root  
    if not os.path.exists(dest):
        os.makedirs(dest)
    archivos_yaml = buscar_archivos_yaml(directorio_raiz)

    # Imprimir los archivos .yaml encontrados
    for archivo in archivos_yaml:
        shutil.copy2(archivo, dest)
    print(f"se han copiado {len(archivos_yaml)} archivos")
    

