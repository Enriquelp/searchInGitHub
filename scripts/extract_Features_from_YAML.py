# Este script extrae las claves de los archivos YAML y las guarda en un archivo CSV. el archivo csv cuenta con las siguientes columnas:
# File: Nombre del archivo YAML
# ObjectType: Tipo de objeto YAML (solo si es un manifiesto de Kubernetes)
# Valid: Indica si el archivo YAML es válido o no
# numFeatures: Número de características en el archivo YAML
# ContainVariability: Indica si el archivo YAML contiene variabilidad o no
# Error: Indica si hubo un error al Comprobar que fuera una configuración válida
# Config: Claves del archivo YAML

import yaml
import csv
from tqdm import tqdm
import os
import valid_config

output_csv = "Configuraciones.csv" # Ruta del archivo CSV de salida
folder_path = "MisYAMLs" # Ruta de la carpeta con los archivos YAML
mapping_file = "resources\mapping.csv" # Ruta del archivo de mapeo
model_path = "resources\kubernetes.uvl" # Ruta del modelo de características
fm_model, sat_model = valid_config.inizialize_model(model_path) # Inicializar los modelos (Mas eficiente cargarlos solo una vez)

# Función recursiva para extraer todas las claves, incluyendo las anidadas, de la declaracion de un objeto de Kubernetes.
def extract_keys(data, parent_key='', kind=None):
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}_{key}" if parent_key else key
            # Si la clave comienza con 'spec', se añade como prefijo el valor de 'kind'
            if parent_key.startswith('spec'): 
                full_key = f"{kind}{parent_key}_{key}"
            keys.append(full_key)
            keys.extend(extract_keys(value, full_key, kind))
    # Si es una lista, se procesa cada elemento de la lista
    elif isinstance(data, list): 
        for index, item in enumerate(data):
            full_key = f"{parent_key}"
            keys.extend(extract_keys(item, full_key, kind))
    return list(set(keys)) # Eliminar duplicados

#funcion para traducir las claves de los archivos YAML en caracteristiacs del modelo.
def translate_keys(keys, map1, map2):
    # Lista para almacenar las claves mapeadas
    mapped_keys = []
    
    # Procesar cada clave
    for key in keys:
        if key in map2:
            # Si está en la 3ra columna, sustituir por el valor de la 1ra columna
            mapped_keys.append(map2[key])
        elif key in map1:
            # Si está en la 2da columna, sustituir por el valor de la 1ra columna
            mapped_keys.append(map1[key])
        else:
            # Si no se encuentra en ninguna columna, dejar la clave tal cual
           continue
    return mapped_keys

# Extrae todas las caracteristicas de los objetos definidos en el archivo YAML (puede definirse mas de un objeto en un archivo YAML)
def obtener_claves_yaml(file_path, map1, map2):
    keys = []
    kinds = []
    with open(file_path, 'r') as file:
        # Cargar todos los documentos YAML (incluidos los separadores '---')
        documents = yaml.safe_load_all(file)
        for doc in documents:
            if doc is None:
                continue
            kind_value = doc.get('kind', '').lower() # Obtener el valor de 'kind' para saber cómo prefijar las claves
            keys_doc = extract_keys(doc, kind = kind_value) # Obtener todas las claves del documento YAML
            keys_doc = translate_keys(keys_doc, map1, map2) # Traducir las claves
            keys.append(keys_doc)
            kinds.append(kind_value)
    return keys, kinds

# Guardar las claves en un archivo CSV
def guardar_claves_csv(objectType, keys, filename, variability, csv_writer):
    for key_list, objectType in zip(keys, objectType):
        isValid, error = valid_config.main(key_list, fm_model, sat_model)
        csv_writer.writerow([filename, objectType, isValid, len(key_list), variability, error, key_list])

# Leer el archivo CSV y construir la tabla de mapeo
def createmapping(mapping_file):
    mapping_table = []
    with open(mapping_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        for row in reader:
            if len(row) >= 3:  # Asegurarse de que hay al menos 3 columnas
                mapping_table.append((row[0], row[1], row[2]))
    # Crear los diccionarios map1 y map2
    map1 = {n2: n1 for n1, n2, _ in mapping_table}
    map2 = {n3: n1 for n1, _, n3 in mapping_table}
    return map1, map2

if __name__ == '__main__':
    # Crear el archivo CSV y escribir el encabezado
    with open(output_csv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['File', 'ObjectType', 'Valid', 'numFeatures', 'ContainVariability', 'Error', 'Config'])
        
        # Procesar cada archivo YAML en la carpeta
        for filename in tqdm(os.listdir(folder_path)): # tqdm para mostrar una barra de progreso
            # Obtener la ruta completa del archivo
            file_path = os.path.join(folder_path, filename)
            # Crear los diccionarios map1 y map2 para traducir las claves del yaml a caracteristicas del FM (mas eficiente)
            map1, map2 = createmapping(mapping_file) 
            try:
                # Obtener las caracteristicas del archivo yaml
                keys, objectType = obtener_claves_yaml(file_path, map1, map2) 
                # Guardar las caracteristicas en el archivo csv
                guardar_claves_csv(objectType, keys, filename, False, csv_writer) 
            # Manejar errores
            except yaml.YAMLError as e:
                # Si hay un error al sacar las caracteristicas del archivo YAML
                guardar_claves_csv(['none'], [''], filename, True ,csv_writer)
                continue
            except Exception as e:
                print(f"No se pudo procesar {filename}: {e}")
                guardar_claves_csv(['none'], [''], filename, True ,csv_writer)
                continue
    print(f"Las claves se han guardado en {output_csv}.")
