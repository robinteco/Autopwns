# Autopwn Forest - HackTheBox

Script en Python para automatizar la explotación de la máquina Forest de HackTheBox.

## Descripción

Este script automatiza el proceso de:

- Comprobar la conectividad con los puertos **RPC (135)** y **Kerberos (88)**.
- Enumerar usuarios del dominio mediante **rpcclient**.
- Identificar usuarios AS-REP roastables usando **Kerbrute**.
- Crackear hashes obtenidos con **John the Ripper**.
- Servir scripts y archivos necesarios mediante un servidor HTTP simple.
- Ejecutar un script PowerShell (`privesc.ps1`) para crear un usuario con privilegios DCSync.
- Extraer hashes NTLM del Domain Controller.
- Conectarse como **Administrator** usando passthehash con **Evil-WinRM**.

## Requisitos

Herramientas externas necesarias en el PATH:

- rpcclient (parte de samba-client)
- kerbrute
- john
- crackmapexec
- secretsdump.py (de Impacket)
- evil-winrm

Archivos necesarios en la misma carpeta:

- privesc.ps1 (script para crear usuario y DCSync)

## Configuración

Modificá estas variables en el script según tu entorno:

target = "10.10.10.161"       # IP de la máquina objetivo

domain = "htb.local"          # Dominio de Windows

ip_local = "10.10.16.7"       # Tu IP para recibir archivos

wordlist = "/usr/share/wordlists/rockyou.txt"  # Wordlist para John

## Uso

Ejecutar el script directamente: python3 autopwn_forest.py

El script realiza la enumeración, identifica usuarios vulnerables, crackea hashes, sirve archivos por HTTP, crea un usuario con DCSync y finalmente obtiene acceso como Administrator.

Advertencias y recomendaciones
Este script es solo para entornos legales, como HackTheBox.
No elimina archivos automáticamente para evitar errores en Windows por archivos en uso.
Se recomienda leer la salida del script cuidadosamente, ya que puede requerir intervención manual para ciertos pasos (por ejemplo, subida de scripts o revisión de hashes).

Contacto
Si tenés dudas o sugerencias, podés contactarme en: cardosojuan@gmail.com
