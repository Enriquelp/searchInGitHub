# Script de búsqueda en GitHub.

# Instalación y ejecución

```python
python -m venv env # Crear entorno virtual
pip install requirements.txt # Instalar dependencias
python download-repositories.py # Ejecutar el script
```

Es necesario crear un archivo .env para guardar el token privado de GitHub

```
github_token = 'XXXXX'
```

# Configuración Inicial

- Se definen intervalos de tiempo para todo el año 2024, dividiéndolo en periodos de 10-11 días.
- Se establecen las configuraciones necesarias para realizar búsquedas en GitHub, como el token de autenticación y el nombre de usuario.
- Se definen varias variables para la gestión de repositorios y archivos YAML, así como los nombres de las columnas para un archivo CSV que almacenará los resultados.

# Funciones

- **remove_readonly(func, path, _):** Elimina los permisos de "solo lectura" de un archivo o directorio para permitir su eliminación.
- **buscar_repositorios(query, github_user, github_token, page, month):** Realiza una búsqueda en GitHub de repositorios que coincidan con la consulta y el intervalo de tiempo especificado.
- **archivo_en_uso(ruta):** Comprueba si un archivo o directorio está en uso por otro proceso.
- **eliminar_repo(ruta_repositorio):** Elimina un repositorio clonado.
- **clonar_repositorio(repo, directorio_destino):** Clona un repositorio de GitHub en el directorio especificado.
- **quitar_solo_lectura(directorio):** Elimina los permisos de solo lectura de un directorio y sus archivos.

# Proceso Principal

1. Creación del archivo CSV: Se abre un archivo CSV para escribir los resultados.
2. Iteración sobre los intervalos de tiempo: Para cada intervalo de tiempo definido:
3. Se busca en GitHub repositorios que coincidan con la consulta Kubernetes_manifest.
4. Para cada repositorio encontrado:
- Se clona el repositorio.
- Se buscan archivos YAML en el repositorio clonado utilizando el módulo ***searchYAML***.
- Se elimina el repositorio clonado.
- Se registran los resultados en el archivo CSV.
1. Se repiten los pasos 3 y 4 hasta que se han recorrido todos los intervalos de tiempo.
2. Finalmente, se filtran los archivos YAML para descartar aquellos que no sean manifiestos de Kubernetes utilizando el módulo ***filterManifest***.

# Módulos

- **searchYAMLs:** Está diseñado para buscar archivos *yaml* en una carpeta específica y copiar todos esos archivos a otra carpeta. Recibe como entrada la ruta donde se encuentra el repositorio a examinar y la ruta a la que se van a copiar los ficheros *yaml* Devuelve el número de archivos encontrados.
- **filterManifest:** está diseñado para verificar si los archivos YAML en una carpeta específica son manifiestos de Kubernetes. Esto se determina buscando las palabras clave *apiVersion* y *kind* en el contenido de cada archivo. Los archivos que no son manifiestos de Kubernetes se mueven a otra carpeta. Recibe como entrada la ruta donde se encuentra los archivos *yaml* examinar y la ruta a la que se van a copiar los ficheros *yaml* que no sean manifiestos de Kubernetes. Devuelve el número de archivos *yaml* que no son manifiestos.

![Diagrama.png](Diagrama.png)
