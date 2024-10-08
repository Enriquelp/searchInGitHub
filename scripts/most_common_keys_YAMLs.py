# Script que cuenta las claves más comunes en archivos YAML de una carpeta y guarda los resultados en un CSV.
# las columnas del CSV son:
# - Key: Clave del archivo YAML
# - Count: Número de veces que aparece la clave
# - Percentage: Porcentaje de apariciones de la clave en relación con la clave más común

import os
import yaml
from collections import Counter
import pandas as pd
from tqdm import tqdm

def extract_keys(yaml_content, prefix=''):
    keys = []
    if isinstance(yaml_content, dict):
        for key, value in yaml_content.items():
            if isinstance(key, str):  # Asegurarse de que la clave es una cadena
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                keys.extend(extract_keys(value, full_key))
    elif isinstance(yaml_content, list):
        for item in yaml_content:
            keys.extend(extract_keys(item, prefix))
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
                            keys = extract_keys(doc)
                            key_counter.update(keys)
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: No se pudo leer {filename} con codificación UTF-8. Intentando con la codificación por defecto.")
                try:
                    with open(file_path, 'r') as file:
                        documents = yaml.safe_load_all(file)
                        for doc in documents:
                            if doc is not None:
                                keys = extract_keys(doc)
                                key_counter.update(keys)
                except (yaml.YAMLError, UnicodeDecodeError) as e:
                    continue
            except yaml.YAMLError as e:
                continue
    
    return key_counter

def main(folder_path, output_csv):
    key_counter = count_keys_in_folder(folder_path)
    key_counts = key_counter.most_common()
    
    df = pd.DataFrame(key_counts, columns=['Key', 'Count'])

    if not df.empty:
        max_count = df['Count'].max()
        df['Percentage'] = (df['Count'] / max_count) * 100
        df['Percentage'] = df['Percentage'].round(4)  # Redondear a 4 decimales

    # df = df[df['Percentage'] >= 1.0]
    
    df.to_csv(output_csv, index=False)
    print(f"Resultados guardados en {output_csv}")

if __name__ == "__main__":
    folder_path = 'YAMLs'  # Ruta de la carpeta con archivos .yaml
    output_csv = 'most_common_keys.csv'  # Ruta donde guardar el CSV
    main(folder_path, output_csv)
