# Script que cuenta las caracteristicas más comunes en archivos YAML de una carpeta y guarda los resultados en un CSV.
# las columnas del CSV son:
# - feature: Clave del archivo YAML
# - Count: Número de veces que aparece la clave
# - Percentage: Porcentaje de apariciones de la clave en relación con la clave más común

import os
import yaml
from collections import Counter
import pandas as pd
from tqdm import tqdm
import csv

mapping_file = 'resources/mapping.csv' 
folder_path = 'YAMLs'  # Ruta de la carpeta con archivos .yaml
output_csv = 'most_common_features.csv'  # Ruta donde se guardará el CSV
map1 = {} # diccionario clave (feature) -> valor (string)
map2 = {} # diccionario clave (feature) -> valor (string)

# Leer el archivo CSV y construir la tabla de mapeo
def create_mapping(mapping_file):
    mapping_table = []
    global map1
    global map2
    with open(mapping_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        for row in reader:
            if len(row) >= 3:  # Asegurarse de que hay al menos 3 columnas
                mapping_table.append((row[0], row[1], row[2]))
    # Crear los diccionarios map1 y map2
    map1 = {n2: n1 for n1, n2, _ in mapping_table}
    map2 = {n3: n1 for n1, _, n3 in mapping_table}

def extract_keys(yaml_content, kind,  parent_key=''):
    keys = []
    if isinstance(yaml_content, dict):
        for key, value in yaml_content.items():
            if isinstance(key, str):  # Asegurarse de que la clave es una cadena
                full_key = f"{parent_key}_{key}" if parent_key else key
                if parent_key.startswith('spec'): 
                  full_key = f"{kind}{parent_key}_{key}"
                if full_key in map2:
                  feature = map2[full_key]
                  keys.append(feature)
                  keys.extend(extract_keys(value, kind, full_key))
                elif full_key in map1:
                    feature = map1[full_key]
                    keys.append(feature)
                    keys.extend(extract_keys(value, kind, full_key))
    elif isinstance(yaml_content, list):
        for item in yaml_content:
            keys.extend(extract_keys(item, kind, parent_key))
    return keys

def count_keys_in_folder(folder_path):
    key_counter = Counter()
    for filename in tqdm(os.listdir(folder_path)):
        if filename.endswith('.yaml'):
            file_path = os.path.join(folder_path, filename)
            try:
              with open(file_path, 'r', encoding='utf-8') as file:
                  documents = yaml.safe_load_all(file)
                  for doc in documents:
                      if doc is not None:
                          kind = doc.get('kind', '').lower()
                          keys = extract_keys(doc, kind)
                          key_counter.update(keys)
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: No se pudo leer {filename} con codificación UTF-8. Intentando con la codificación por defecto.")
                try:
                    with open(file_path, 'r') as file:
                        documents = yaml.safe_load_all(file)
                        for doc in documents:
                            if doc is not None:
                                kind = doc.get('kind', '').lower()
                                keys = extract_keys(doc, kind)
                                key_counter.update(keys)
                except (yaml.YAMLError, UnicodeDecodeError) as e:
                    continue
            except yaml.YAMLError as e:
                continue
            except AttributeError as e:
                print(f"AttributeError: No se pudo leer {filename}.")
                continue
    return key_counter


def main(folder_path, output_csv):
    create_mapping(mapping_file)
    key_counter = count_keys_in_folder(folder_path)
    key_counts = key_counter.most_common()
    
    df = pd.DataFrame(key_counts, columns=['Feature', 'Count'])

    if not df.empty:
        max_count = df['Count'].max()
        df['Percentage'] = (df['Count'] / max_count) * 100
        df['Percentage'] = df['Percentage'].round(4)  # Redondear a 4 decimales

    #df = df[df['Percentage'] >= 1.0] # Filtrar claves con menos del 1% de apariciones
    
    df.to_csv(output_csv, index=False)
    print(f"Resultados guardados en {output_csv}")

if __name__ == "__main__":
    main(folder_path, output_csv)