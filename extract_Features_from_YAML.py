import yaml
import csv
from tqdm import tqdm
import os

output_csv = "Configuraciones.csv"
folder_path = "MisYaml"

# Función recursiva para extraer todas las claves, incluyendo las anidadas, de un archivo YAML
def extract_keys(data, parent_key='', kind=None):
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            # Si estamos dentro de spec, añadimos el prefijo "deployment" a la clave
            if parent_key.startswith('spec') and kind == 'Deployment':
                full_key = f"deployment{parent_key}.{key}"
            keys.append(full_key)
            keys.extend(extract_keys(value, full_key, kind))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            full_key = f"{parent_key}[{index}]"
            keys.extend(extract_keys(item, full_key, kind))
    return keys

def obtener_claves_yaml(file_path):
  with open(file_path, 'r') as file:
    data = yaml.safe_load(file) #carga los datos del archivo yaml  
    kind_value = data.get('kind', '') # Obtener el valor de 'kind' para saber cómo prefijar las claves
    keys = extract_keys(data, kind=kind_value) # Obtener todas las claves del archivo yaml
    return keys

# Guardar las claves en un archivo CSV
def guardar_claves_csv(keys,filename, csv_writer):
  csv_writer.writerow([keys, " " ,filename, len(keys)])

if __name__ == '__main__':
  with open('Configuraciones.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Config', 'Valid', 'File', 'Features'])  # Escribir el encabezado
    for filename in tqdm(os.listdir(folder_path)):
      file_path = os.path.join(folder_path, filename)
      print(file_path)
      keys = obtener_claves_yaml(file_path)
      guardar_claves_csv(keys, filename, csv_writer)
  print("Las claves se han guardado en 'claves.csv'.")
