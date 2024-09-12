import yaml
import csv
from tqdm import tqdm
import os

output_csv = "Configuraciones.csv"
folder_path = "MisYAMLs"

# Función recursiva para extraer todas las claves, incluyendo las anidadas, de un archivo YAML
def extract_keys(data, parent_key=''):
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}_{key}" if parent_key else key
            keys.append(full_key)
            keys.extend(extract_keys(value, full_key))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            full_key = f"{parent_key}[{index}]"
            keys.extend(extract_keys(item, full_key))
    return keys

def obtener_claves_yaml(file_path):
    keys = []
    kinds = []
    with open(file_path, 'r') as file:
        # Cargar todos los documentos YAML (incluidos los separadores '---')
        documents = yaml.safe_load_all(file)
        for doc in documents:
            if doc is None:
                continue
            kind_value = doc.get('kind', '') # Obtener el valor de 'kind' para saber cómo prefijar las claves
            keys_doc = extract_keys(doc) # Obtener todas las claves del documento YAML
            keys.append(keys_doc)
            kinds.append(kind_value)
    return keys, kinds

# Guardar las claves en un archivo CSV
def guardar_claves_csv(objectType, keys, filename, error, variability, csv_writer):
    for key_list, objectType in zip(keys, objectType):
        csv_writer.writerow([filename, objectType, "", len(key_list), variability, error, key_list])

if __name__ == '__main__':
    with open(output_csv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['File', 'ObjectType', 'Valid', 'numFeatures', 'ContainVariability', 'Error', 'Config'])  # Escribir el encabezado
        for filename in tqdm(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, filename)
            try:
                keys, objectType = obtener_claves_yaml(file_path)
                guardar_claves_csv(objectType, keys, filename,'', False, csv_writer)
            except yaml.YAMLError as e:
              guardar_claves_csv(['none'], [''], filename, '', True ,csv_writer)
              continue
            except Exception as e:
                print(f"No se pudo procesar {filename}: {e}")
                guardar_claves_csv(['none'], [''], filename, '', True ,csv_writer)
                continue
    print(f"Las claves se han guardado en {output_csv}.")
