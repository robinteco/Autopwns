# Autopwn Remote - HackTheBox

<img width="833" height="614" alt="image" src="https://github.com/user-attachments/assets/f9176805-b892-4e94-820d-07a800e68843" />

## 📖 Descripción
Este repositorio contiene tres scripts principales:

1. **`autopwn_remote.py`**: Automatiza la enumeración NFS, extracción de la base de datos Umbraco `.sdf`, crackeo de credenciales y ejecución del exploit.
2. **`exploit.py`**: Envío del payload XSLT a Umbraco, creación de reverse shell estable y extracción de contraseñas de TeamViewer.
3. **`exploit.cs`**: Es una reverse shell en PowerShell que conecta la víctima al atacante, ejecuta comandos y devuelve la salida en tiempo real.

Funcionamiento:

1. Montaje NFS seguro y creación de directorios si no existen.
2. Extracción automatizada de credenciales de Umbraco.
3. Crackeo de hashes SHA1 con john.
4. Payload XSLT para ejecutar código remoto en Umbraco.
5. Reverse shell estable en dos puertos (4444/4445) para ejecutar comandos post-explotación.
6. Descifrado de contraseñas TeamViewer de versiones vulnerables (7–15). 

## 🚀 Uso

`sudo python3 autopwn_remote.py`

## ⚙️ Requisitos

- Paquetes Python: `pip install pwntools requests beautifulsoup4 pycryptodome`
- Herramientras externas: showmount, johntheripper, evil-winrm, 

## 🔧 Configuración

Editá las variables del script según tu entorno:

```
**target = "10.10.10.180"**       # IP de la máquina objetivo

**ip_local = "10.10.16.7"**        # IP del atacante para recibir la reverse shell

**wordlist = "/usr/share/wordlists/rockyou.txt"** # Wordlist para JOhn
```

## 💻 Contacto

**Autor:** Juan Manuel Cardoso (Teco)

**Blog:** https://teco.gitbook.io/t3co

**GitHub:** https://github.com/robinteco

**LinkedIn:** https://www.linkedin.com/in/juan-manuel-cardoso/
