# 🔐 Configuración de GitHub Secrets y Variables

Esta guía te ayudará a configurar todos los secrets y variables necesarios para el deployment automático.

## 📍 Ubicación en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (Configuración)
3. En el menú lateral izquierdo, ve a **Secrets and variables** → **Actions**

## 🔑 Secrets a Configurar

### 1. DB_PASSWORD
```
Valor: Tu contraseña de PostgreSQL
Ejemplo: MiP@ssw0rdSegur0!
```

### 2. EC2_HOST
```
Valor: IP pública o dominio de tu servidor EC2
Ejemplo: 54.123.45.67
Ejemplo: api.tudominio.com
```

### 3. EC2_SSH_KEY
```
Valor: Tu clave privada SSH completa (incluyendo BEGIN y END)
Formato:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
... (todo el contenido de tu clave) ...
-----END RSA PRIVATE KEY-----

⚠️ IMPORTANTE: Incluir TODO el contenido de la clave, con los headers
⚠️ No uses contraseña en la clave SSH (debe ser passwordless)
```

**Cómo obtener tu clave SSH:**
```bash
# Si ya tienes una clave
cat ~/.ssh/id_rsa

# Si necesitas crear una nueva (sin contraseña)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/siscom_deploy -N ""

# Copiar la clave pública al EC2
ssh-copy-id -i ~/.ssh/siscom_deploy.pub usuario@tu-ec2-host
```

### 4. EC2_SSH_PORT
```
Valor: Puerto SSH de tu EC2
Ejemplo: 22
(Si usas un puerto personalizado, usa ese número)
```

### 5. EC2_USERNAME
```
Valor: Usuario SSH para conectarse al EC2
Ejemplo para Ubuntu: ubuntu
Ejemplo para Amazon Linux: ec2-user
Ejemplo para Debian: admin
```

### 6. JWT_SECRET_KEY
```
Valor: Una clave secreta larga y aleatoria para JWT
Ejemplo: 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

⚠️ DEBE ser diferente en cada ambiente
⚠️ Mantener segura, nunca compartir
```

**Generar una clave segura:**
```bash
# Usando OpenSSL
openssl rand -hex 32

# Usando Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 7. DOCKER_USERNAME (Opcional)
```
Valor: Tu usuario de Docker Hub
Solo necesario si quieres guardar las imágenes en Docker Hub
Puedes comentar estas líneas en el workflow si no lo usas
```

### 8. DOCKER_PASSWORD (Opcional)
```
Valor: Token de acceso de Docker Hub
⚠️ NO uses tu contraseña, usa un Access Token
Crear en: https://hub.docker.com/settings/security
```

## 📊 Variables a Configurar

En la misma página, ve a la pestaña **Variables** (al lado de Secrets):

### 1. DB_CONNECTION_TIMEOUT_SECS
```
Valor: 30
Descripción: Timeout en segundos para conexión a la DB
```

### 2. DB_DATABASE
```
Valor: siscom
Descripción: Nombre de la base de datos
```

### 3. DB_HOST
```
Valor: tu-db-host.rds.amazonaws.com
Descripción: Host de tu base de datos PostgreSQL
Ejemplo: localhost (si la DB está en el mismo EC2)
Ejemplo: postgres.internal (si usas DNS interno)
```

### 4. DB_IDLE_TIMEOUT_SECS
```
Valor: 300
Descripción: Timeout de idle para conexiones en el pool
```

### 5. DB_MAX_CONNECTIONS
```
Valor: 20
Descripción: Número máximo de conexiones en el pool
```

### 6. DB_MIN_CONNECTIONS
```
Valor: 10
Descripción: Número mínimo de conexiones en el pool
```

### 7. DB_PORT
```
Valor: 5432
Descripción: Puerto de PostgreSQL
```

### 8. DB_USERNAME
```
Valor: postgres
Descripción: Usuario de la base de datos
```

## ✅ Verificación

### Checklist de Secrets:
- [ ] DB_PASSWORD
- [ ] EC2_HOST
- [ ] EC2_SSH_KEY (incluye BEGIN/END)
- [ ] EC2_SSH_PORT
- [ ] EC2_USERNAME
- [ ] JWT_SECRET_KEY

### Checklist de Variables:
- [ ] DB_CONNECTION_TIMEOUT_SECS
- [ ] DB_DATABASE
- [ ] DB_HOST
- [ ] DB_IDLE_TIMEOUT_SECS
- [ ] DB_MAX_CONNECTIONS
- [ ] DB_MIN_CONNECTIONS
- [ ] DB_PORT
- [ ] DB_USERNAME

## 🧪 Probar la Configuración

### 1. Verificar SSH desde tu máquina local:
```bash
ssh -i ~/.ssh/tu_clave -p PUERTO usuario@HOST
```

### 2. Verificar que Docker esté instalado en el EC2:
```bash
ssh -i ~/.ssh/tu_clave -p PUERTO usuario@HOST "docker --version && docker compose version"
```

### 3. Verificar conectividad a la DB desde el EC2:
```bash
ssh -i ~/.ssh/tu_clave -p PUERTO usuario@HOST "nc -zv DB_HOST DB_PORT"
```

## 🚀 Primer Deploy

1. Haz un commit y push a la rama `main`:
```bash
git add .
git commit -m "Initial setup with CI/CD"
git push origin main
```

2. Ve a **Actions** en GitHub para ver el workflow ejecutándose

3. Si falla, revisa los logs para identificar qué secret o variable está mal configurado

## 🔧 Preparación del EC2

Antes del primer deploy, asegúrate de que tu EC2 tenga:

### 1. Docker instalado:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Reiniciar sesión SSH después de agregar al grupo docker
```

### 2. Docker Compose instalado:
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin -y
```

### 3. Crear directorio para el proyecto:
```bash
mkdir -p ~/siscom-api
```

### 4. Security Group configurado:
- Puerto 22 (SSH) abierto para tu IP
- Puerto 8000 (API) abierto según necesites
- Puerto 5432 (si la DB está en el mismo EC2)

### 5. Conectividad a la base de datos:
- Si usas RDS, asegúrate de que el Security Group del RDS permita conexiones desde el EC2
- Si usas DB en el mismo EC2, crea un contenedor de PostgreSQL

## 📝 Ejemplo de Security Group (EC2)

**Inbound Rules:**
```
Type        | Port | Source           | Description
SSH         | 22   | Tu IP           | SSH Access
Custom TCP  | 8000 | 0.0.0.0/0       | API Access
PostgreSQL  | 5432 | Security Group  | DB Access (si aplica)
```

## 🐛 Troubleshooting

### Error: "Permission denied (publickey)"
- Verifica que la clave SSH sea correcta
- Verifica que la clave pública esté en el EC2: `~/.ssh/authorized_keys`
- Verifica el usuario (ubuntu, ec2-user, etc.)

### Error: "Host key verification failed"
- Primer deploy: Conecta manualmente una vez por SSH
- O agrega `StrictHostKeyChecking=no` (menos seguro)

### Error: "docker: command not found"
- Docker no está instalado en el EC2
- Sigue los pasos de preparación del EC2

### Error: "Cannot connect to database"
- Verifica el DB_HOST y DB_PORT
- Verifica Security Groups
- Verifica que la DB esté corriendo

## 🎯 Ambientes Múltiples

Para tener ambientes de staging y producción:

1. Crea diferentes secrets por ambiente:
   - Prefija con el ambiente: `PROD_DB_PASSWORD`, `STAGING_DB_PASSWORD`
   
2. Modifica el workflow para usar diferentes secrets según la rama:
```yaml
env:
  DB_PASSWORD: ${{ github.ref == 'refs/heads/main' && secrets.PROD_DB_PASSWORD || secrets.STAGING_DB_PASSWORD }}
```

3. Usa diferentes hosts de EC2 para cada ambiente

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del workflow en GitHub Actions
2. Conéctate al EC2 y revisa: `docker logs siscom-api`
3. Verifica que todos los secrets y variables estén configurados
4. Verifica la conectividad de red entre EC2 y la DB

