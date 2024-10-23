# Este script extrae las claves de los archivos YAML y las guarda en un archivo CSV. el archivo csv cuenta con las siguientes columnas:
# File: Nombre del archivo YAML
# ObjectType: Tipo de objeto YAML (solo si es un manifiesto de Kubernetes)
# Valid: Indica si el archivo YAML es válido o no
# numFeatures: Número de características en el archivo YAML
# ContainVariability: Indica si el archivo YAML contiene variabilidad o no
# Error: Indica si hubo un error al Comprobar que fuera una configuración válida
# Config: Claves del archivo YAML
# featuresNotFound: Claves encontradas en el archivo YAML que no se encuentran en el modelo de características
# Tambien genera un archivo CSV con el numero de configuraciones por manifiesto (incluyendo aquellas donde no se encontraron configuraciones)
# y un archivo con los archivos no procesados.

import yaml
import csv
from tqdm import tqdm
import os
import valid_config
import socket

output_csv = "Configuraciones.csv" # Ruta del archivo CSV de salida
output_numConfPerManifest_csv = "numConfPerManifest.csv" # Ruta del archivo CSV con el numero de configuraciones por manifiesto
output_not_processed = "filesNotProcessed.txt" # Ruta del archivo con los archivos no procesados
folder_path = "YAMLs" # Ruta de la carpeta con los archivos YAML
mapping_file = "resources\mapping.csv" # Ruta del archivo de mapeo
model_path = "resources\kubernetes.uvl" # Ruta del modelo de características
fm_model, sat_model = valid_config.inizialize_model(model_path) # Inicializar los modelos (Mas eficiente cargarlos solo una vez)
values_of_keys = [] # Lista para almacenar los valores de las claves

def is_ip(value):
    try:
        # Intentar validar como IPv4
        socket.inet_pton(socket.AF_INET, value)
        return True
    except socket.error:
        pass  # No es una IPv4 válida
    try:
        # Intentar validar como IPv6
        socket.inet_pton(socket.AF_INET6, value)
        return True
    except socket.error:
        pass  # No es una IPv6 válida
    return False

# Función recursiva para extraer todas las claves, incluyendo las anidadas, de la declaracion de un objeto de Kubernetes.
def extract_keys(data, parent_key='', kind=None):
    global values_of_keys
    keys = []
    values = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}_{key}" if parent_key else key
            # Si la clave comienza con 'spec', se añade como prefijo el valor de 'kind' generando "deploymentspec" o "servicespec" por ejemplo
            if key == 'spec' and parent_key == '':
                full_key = f"{kind}{key}"
            if parent_key.startswith('spec'): 
                full_key = f"{kind}{parent_key}_{key}"
            if isinstance(value, str):
                if is_ip(value): # Si el valor es una IP, se añade como "key_IP_value"
                    full_value = f"{full_key}_IP"
                else:
                    full_value = f"{full_key}_{value}"
                values_of_keys.append(full_value)
            keys.append(full_key)    
            keys.extend(extract_keys(value, full_key, kind))
    # Si es una lista, se procesa cada elemento de la lista
    elif isinstance(data, list): 
        full_key = f"{parent_key}"
        for index, item in enumerate(data):
            if isinstance(item, str) and is_ip(item):
                values_of_keys.append(full_key + "_IP") 
            else:
                keys.extend(extract_keys(item, full_key, kind))      
    return list(set(keys)) # Eliminar duplicados

#funcion para traducir las claves de los archivos YAML en caracteristiacs del modelo.
def translate_keys(keys, map1, map2):
    # Lista para almacenar las claves mapeadas
    mapped_keys = []
    keys_not_found = []

    
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
           keys_not_found.append(key)
    return mapped_keys, keys_not_found

# Obtener el grupo y la versión del objeto de Kubernetes
def get_group_and_version(doc):
    var = doc.get('apiVersion', '').split('/')
    kind = doc.get('kind', '')
    if len(var) == 2:
        group, version = var
    else:
        group = 'core'
        version = var[0]
    return group, version, kind


# Extrae todas las caracteristicas de los objetos definidos en el archivo YAML (puede definirse mas de un objeto en un archivo YAML)
def read_keys_yaml(file_path, map1, map2):
    keys = []
    kinds = []
    not_found = []
    configs = 0
    global values_of_keys
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        # Cargar todos los documentos YAML (incluidos los separadores '---')
        documents = yaml.safe_load_all(file)
        for doc in documents:
            if doc is None:
                continue
            values_of_keys = []
            configs += 1 # Contar el numero de configuraciones en el archivo YAML
            # Obtener el valor de 'group', 'version' y 'kind' (para saber cómo prefijar las claves) para incluir esas claves
            group_value, version_value, kind_value = get_group_and_version(doc)
            # Obtener todas las claves del documento YAML
            keys_doc = extract_keys(doc, kind = kind_value.lower()) 
            values_doc, values_not_found = translate_keys(values_of_keys, map1, map2)
            keys_doc.append(kind_value)
            keys_doc.append(group_value)
            keys_doc.append(version_value)
            # Traducir las claves
            keys_doc, keys_not_found = translate_keys(keys_doc, map1, map2) 
            # Se añaden las caracteristicas encontradas como valor de alguna clave a la lista de claves del manifiesto
            for value in values_doc:
                if value not in keys_doc:
                    keys_doc.append(value)
            keys.append(keys_doc)
            kinds.append(kind_value)
            not_found.append(keys_not_found)
    return keys, kinds, not_found, configs

# Guardar las claves en un archivo CSV
def save_keys_csv(objectType, keys, filename, variability, not_found, csv_writer):
    for key_list, objectType, not_found in zip(keys, objectType, not_found):
        isValid, error, complete_config = valid_config.main(key_list, fm_model, sat_model) #complete_config es la configuracion completa segun el modelo
        csv_writer.writerow([filename, objectType, isValid, len(complete_config), variability, error, complete_config, not_found])

# Leer el archivo CSV y construir la tabla de mapeo
def create_mapping(mapping_file):
    mapping_table = []
    with open(mapping_file, mode='r', newline='', encoding='utf-8') as file:
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
    numFilesNotProcessed = 0
    filesNotProcessed = []
    numConfPerManifest = {}
    # Crear el archivo CSV y escribir el encabezado
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['File', 'ObjectType', 'Valid', 'numFeatures', 'ContainVariability', 'Error', 'Config', 'featuresNotFound'])
        
        # Procesar cada archivo YAML en la carpeta
        for filename in tqdm(os.listdir(folder_path)): # tqdm para mostrar una barra de progreso
            configs = 0
            # Obtener la ruta completa del archivo
            file_path = os.path.join(folder_path, filename)
            # Crear los diccionarios map1 y map2 para traducir las claves del yaml a caracteristicas del FM (mas eficiente)
            map1, map2 = create_mapping(mapping_file) 
            try:
                # Obtener las caracteristicas del archivo yaml
                values_of_keys = []
                keys, objectType, not_found, configs = read_keys_yaml(file_path, map1, map2) 
                # Guardar el numero de configuraciones por manifiesto
                numConfPerManifest[filename] = configs
                # Guardar las caracteristicas en el archivo csv
                save_keys_csv(objectType, keys, filename, False, not_found, csv_writer) 
            # Manejar errores
            except yaml.YAMLError as e:
                # Si hay un error al sacar las caracteristicas del archivo YAML
                numFilesNotProcessed += 1
                filesNotProcessed.append((filename, str(e)))
                numConfPerManifest[filename] = configs
                save_keys_csv(['none'], [''], filename, True , [''], csv_writer)
                continue
            except Exception as e:
                numFilesNotProcessed += 1
                filesNotProcessed.append((filename, str(e)))
                numConfPerManifest[filename] = configs
                save_keys_csv(['none'], [''], filename, False , [''], csv_writer)
                continue
    # Guardar los archivos no procesados
    with open(output_not_processed, mode='w', newline='', encoding='utf-8') as file:
        file.write(f'No se han podido procesar {numFilesNotProcessed} archivos. \n\n')
        for (filename, err) in filesNotProcessed:
            file.write(f'archivo: {filename} ')
            file.write(f'error: {err}')
            file.write(f'\n <------------------------------------> \n')
    # Guardar el numero de configuraciones por manifiesto
    with open(output_numConfPerManifest_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['File', 'numConfigurations'])
        for key, value in numConfPerManifest.items():
            csv_writer.writerow([key, value])

    # Mostrar mensaje de finalización
    print(f"Las claves se han guardado en {output_csv}.")
    print(f"No se han podido procesar {numFilesNotProcessed} archivos. La lista se encuentra en {output_not_processed}.")
