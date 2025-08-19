# Autopwn Active - HackTheBox


## 📖 Descripción

1. Comprobación de conectividad con los puertos **SMB (445)** y **Kerberos (88)**.  
2. Descarga del archivo **Groups.xml** desde la carpeta `Replication` mediante **smbmap**.  
3. Extracción de credenciales en texto plano desde `gpp.xml` utilizando **gpp-decrypt**.  
4. Obtención de un **TGS** con `GetUserSPNs.py` y ejecución de un **Kerberoasting Attack**.  
5. Crackeo del hash Kerberos con **John the Ripper**.  
6. Uso de las credenciales de **Administrator** para conectarse vía **psexec.py** y obtener una shell con privilegios administrativos.

## 🚀 Uso

python3 autopwn_active.py

## ⚙️ Requisitos

- **smbmap:** sudo apt install smbmap -y

- **gpp-decrypt:** sudo apt install gpp-decrypt -y

- **John the Ripper:** sudo apt install john -y

- **Impacket (para GetUserSPNs.py y psexec.py):** sudo apt install python3-impacket -y

## 📂 Archivos generados

- **gpp.xml** → Contiene las credenciales cifradas descargadas desde el recurso compartido SMB.  
- **hash.txt** → Archivo con el hash Kerberos extraído (TGS) para crackear con John.  

## 🔧 Configuración

Modificá las variables en el script según tu entorno:

**target   =** "10.10.10.100"         # IP de la máquina objetivo

**domain   =** "active.htb"           # Dominio de Windows

**wordlist =** "/usr/share/wordlists/rockyou.txt"  # Wordlist para John
