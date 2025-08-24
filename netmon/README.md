# Autopwn Netmon - HackTheBox

## 📖 Descripción
Explotación automática de la máquina Netmon de HackTheBox aprovechando el acceso anónimo a FTP y la vulnerabilidad en **PRTG Network Monitor**.  

1. Comprobación de conectividad con el puerto FTP (21).  
2. Conexión como usuario **Anonymous** y descarga del archivo `PRTG Configuration.old.bak`.  
3. Extracción de credenciales en texto plano desde el archivo de configuración.  
4. Corrección automática de la contraseña incrementando el año.  
5. Autenticación en la interfaz web de **PRTG Network Monitor** con las credenciales válidas.  
6. Creación de una notificación maliciosa con comando para añadir un nuevo usuario administrador en Windows.  
7. Ejecución de la notificación para ganar privilegios en el sistema.  
8. Obtención de una PowerShell interactiva con **evil-winrm** como usuario administrador.  

## 🚀 Uso
python3 autopwn_netmon.py

## ⚙️ Requisitos
**pwntools:** pip3 install pwntools

**requests:** pip3 install requests

**evil-winrm:** sudo gem install evil-winrm

## 🔧 Configuración

Editá las variables del script según tu entorno:

**target = "10.10.10.152"**       # IP de la máquina objetivo

**user_privesc = "teco2"**        # Usuario a crear en Windows

**password_privesc = "t3cO123!"** # Contraseña del usuario
