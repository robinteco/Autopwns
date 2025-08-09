# Autopwn Devel - HackTheBox

Script en Python para automatizar la explotación de la máquina **Devel** de HackTheBox usando el exploit MS11-046.


## Descripción

Este script automatiza el proceso de:

- Comprobar conexión FTP con la máquina objetivo.  
- Subir archivos maliciosos necesarios (netcat, web shell, exploit).  
- Ejecutar el exploit MS11-046 para escalar privilegios a SYSTEM.  
- Obtener una shell interactiva con permisos SYSTEM.


## Requisitos

- Python 3  
- Kali Linux o cualquier entorno con Python y librerías necesarias  
- Paquetes Python:  
- pwntools  
- requests

Podés instalar las librerías con: `pip install pwntools requests`


## Archivos necesarios en la misma carpeta

**nc.exe** (Netcat para Windows)

**shell.aspx** (Web shell ASPX para ejecución remota)

**ms11-046.exe** (Exploit compilado para Windows)


## Uso

python3 autopwn_devel.py


## Configuración

En el script, modificá estas variables si es necesario:

```bash
rhost = '10.10.10.5'    # IP de la máquina víctima  
lhost = '10.10.16.7'    # IP del atacante (tu máquina)  
lport = 443             # Puerto local para recibir la shell  
```

## Advertencias y recomendaciones

Usar este script únicamente en entornos legales o máquinas que tengas permiso para atacar (por ejemplo, HackTheBox).
No compartir ni usar para actividades ilegales.
El script no elimina los archivos subidos automáticamente para evitar errores en Windows por archivos en uso.


## Contacto

Si tenés dudas o sugerencias, podés contactarme en: cardosojuan@gmail.com
