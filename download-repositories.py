import requests
import git
import os
import shutil
import psutil
import stat
import searchYAML
import filterManifest

year2024 = [
    "created:2024-01-01..2024-01-31",
    "created:2024-02-01..2024-02-29",
    "created:2024-03-01..2024-03-31",
    "created:2024-04-01..2024-04-30",
    "created:2024-05-01..2024-05-31",
    "created:2024-06-01..2024-06-30",
    "created:2024-07-01..2024-07-31",
    "created:2024-08-01..2024-08-31",
    "created:2024-09-01..2024-09-30",
    "created:2024-10-01..2024-10-31",
    "created:2024-11-01..2024-11-30",
    "created:2024-12-01..2024-12-31"
]

# Mi token de GitHub
github_token = os.getenv("github_token")

# Configuración
github_user = 'Enriquelp'
query = 'Kubernetes_manifest'
clonar_en_directorio = 'Repositories/'
destYAML = "YAMLs"

# elimina un directorio oculto
def remove_readonly(func, path, _):
    archivo_en_uso(ruta_repositorio)
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Función para buscar repositorios en GitHub
def buscar_repositorios(query, github_user, github_token, page, month):
    url = f'https://api.github.com/search/repositories?q={query}+{month}&page={page}&per_page=100&sort=stars&order=desc'
    print(f"Descargando repositorios desde la url -> {url}")
    response = requests.get(url, auth=(github_user, github_token))
    if response.status_code == 200:
        return response.json()['items'], response.json()['total_count']
    else:
        response.raise_for_status()

# Comprueba si un archivo o directorio está en uso por otro proceso
def archivo_en_uso(ruta):
    ruta_real = os.path.realpath(ruta)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for item in proc.open_files():
                if item.path == ruta_real:
                    return True, proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None

# Eliminar la carpeta del repositorio que ya no se necesita
def eliminar_repo(ruta_repositorio):
    archivo_en_uso(ruta_repositorio)
    try:
        shutil.rmtree(ruta_repositorio, onerror=remove_readonly)
        print(f"El repositorio ha sido eliminado exitosamente.")
    except Exception as e:
        print(f"Error al eliminar el repositorio {ruta_repositorio}: {e}")

# Función para clonar un repositorio
def clonar_repositorio(repo, directorio_destino):
    print(f"Clonando {repo['clone_url']}...")
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    try:
        repo = git.Repo.clone_from(repo['clone_url'], directorio_destino)
        print(f"Repositorio {directorio_destino} clonado con exito.")
    except:
        print('Hubo un problema con la clonacion.')
    # Eliminamos los permisos de "read-only"
    quitar_solo_lectura(directorio_destino)
    return repo

# Funcion para eliminar los permisos de lectura de un directorio
def quitar_solo_lectura(directorio):
    print(f'Eliminando permisos de solo lectura...')
    for root, dirs, files in os.walk(directorio):
        for nombre in files:
            ruta_archivo = os.path.join(root, nombre)
            # Quitar el atributo de solo lectura del archivo
            os.chmod(ruta_archivo, stat.S_IWRITE)

        for nombre in dirs:
            ruta_directorio = os.path.join(root, nombre)
            # Quitar el atributo de solo lectura del directorio
            os.chmod(ruta_directorio, stat.S_IWRITE)

for month in year2024:
    page = 1
    repositoriosURL, numMaxRepo = buscar_repositorios(query, github_user, github_token, 1, month)
    numRepo = 1

    while numRepo <= numMaxRepo and numRepo <= 1000 and page < 100:
        for repoURL in repositoriosURL:
            print(f"<---- Repositorio {numRepo} de {numMaxRepo} ---->")
            ruta_repositorio = clonar_en_directorio+repoURL['full_name']
            repo = clonar_repositorio(repoURL, ruta_repositorio)

            # Guardamos todos los archivos YAML de ese repositorio
            searchYAML.main(ruta_repositorio, destYAML)

            # Eliminamos el repositorio
            eliminar_repo(clonar_en_directorio)
            numRepo += 1

        page +=1
        repositoriosURL, numMaxRepo = buscar_repositorios(query, github_user, github_token, page, month)
        

filterManifest.main(destYAML)