Instalar dependendias con 'pip install requirements.txt'.
crear entorno virtual con 'python -m venv env'
Es necesario un archivo .env para guardar la clave de GitHub personal.

download-repositories.py es el script principal. Hace uso de los otros dos.

searchYAML.py busca en el repositorio descargado por donwload.repositories.py todos los archivos que sean .yaml y los guarda en una carpeta a parte.

filterManifest.py filtra todos los archivos YAML encontrados por searchYAML.py y descarta aquellos que no son manifiestos de Kubernetes.



