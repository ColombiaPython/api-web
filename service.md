# Publicar FastAPI con systemd, Nginx y HTTPS

Este manual publica la API en `pythonco.orionis-framework.com`. La aplicación
escucha únicamente en `127.0.0.1:8002`; Nginx recibe el tráfico público en los
puertos 80 y 443 y lo reenvía a FastAPI.

## 1. Requisitos previos

Ejecuta los comandos como `root` o con `sudo`. Antes de continuar, confirma
que:

- El proyecto está desplegado en `/opt/python_co`.
- Existe el entorno virtual `/opt/python_co/.venv`.
- Existe `/opt/python_co/.env` y contiene las variables necesarias.
- El dominio `pythonco.orionis-framework.com` apunta a la IP pública del servidor.
- El Security Group de AWS permite TCP 80 y TCP 443 desde Internet.

Instala Nginx si aún no está instalado:

```bash
apt update
apt install nginx -y
```

## 2. Crear el servicio de systemd

Crea el archivo `/etc/systemd/system/python-co.service`:

```bash
nano /etc/systemd/system/python-co.service
```

Contenido:

```ini
[Unit]
Description=FastAPI PythonCo
After=network.target

[Service]
User=root
WorkingDirectory=/opt/python_co
EnvironmentFile=/opt/python_co/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/python_co/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`User=root` mantiene el comportamiento del despliegue actual. Para producción
se recomienda crear un usuario dedicado y usarlo en lugar de `root`.

Guarda el archivo con `Ctrl + O`, confirma con `Enter` y sal con `Ctrl + X`.

## 3. Activar e iniciar FastAPI

Recarga las unidades de systemd y activa el servicio para que arranque con el
servidor. `--now` también lo inicia inmediatamente:

```bash
systemctl daemon-reload
systemctl enable --now python-co
```

Comprueba el estado:

```bash
systemctl status python-co --no-pager
```

Debe aparecer `Active: active (running)`. Si el servicio falla, consulta los
logs:

```bash
journalctl -u python-co -n 100 --no-pager
journalctl -u python-co -f
```

El segundo comando muestra los logs en tiempo real; sal con `Ctrl + C`.

Antes de configurar Nginx, verifica que FastAPI responde localmente:

```bash
curl http://127.0.0.1:8002
```

## 4. Configurar Nginx

Crea la configuración del sitio:

```bash
nano /etc/nginx/sites-available/python-co
```

Pega este contenido:

```nginx
server {
    listen 80;
    server_name pythonco.orionis-framework.com;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activa el sitio. El enlace simbólico con `-sfn` permite repetir el comando sin
obtener un error si ya existe:

```bash
ln -sfn /etc/nginx/sites-available/python-co /etc/nginx/sites-enabled/python-co
```

Comprueba la configuración y recarga Nginx:

```bash
nginx -t
systemctl reload nginx
```

Prueba el dominio por HTTP:

```bash
curl -i http://pythonco.orionis-framework.com
```

No continúes con SSL hasta que DNS, Nginx y la respuesta HTTP funcionen.

## 5. Activar HTTPS con Let's Encrypt

Instala Certbot y su complemento para Nginx:

```bash
apt update
apt install certbot python3-certbot-nginx -y
```

Solicita el certificado y permite que Certbot configure Nginx:

```bash
certbot --nginx -d pythonco.orionis-framework.com
```

Durante el asistente, selecciona la redirección de HTTP a HTTPS cuando se
ofrezca. Después verifica la configuración y la API:

```bash
nginx -t
curl -i https://pythonco.orionis-framework.com
```

Certbot configura la renovación automática. Puedes comprobarla sin renovar el
certificado con:

```bash
certbot renew --dry-run
```

## 6. Puertos del servidor

En el Security Group de AWS permite únicamente:

```text
TCP 80   0.0.0.0/0
TCP 443  0.0.0.0/0
```

No abras el puerto `8002` públicamente. FastAPI está enlazado a
`127.0.0.1:8002`, por lo que solo Nginx puede acceder directamente al servicio.
