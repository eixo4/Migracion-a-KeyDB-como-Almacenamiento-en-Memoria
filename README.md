# ⚡ Turbo-Librarian

Gestor de biblioteca de alto rendimiento utilizando **KeyDB** (compatible con Redis) como almacenamiento en memoria Key-Value.

## 📝 Requisitos

* Python 3.8+
* Servidor KeyDB (o Redis)

## 🛠️ Instalación y Configuración

### 1. Levantar KeyDB (Docker - Recomendado)
La forma más fácil de tener KeyDB corriendo es con Docker. Ejecuta este comando en tu terminal:

```bash
docker run -d -p 6379:6379 --name mi-keydb eqalpha/keydb
````

*Si no tienes Docker:* Puedes instalar Redis Server (que es compatible) en Windows o Linux. KeyDB actúa como un "drop-in replacement" de Redis.

### 2\. Instalar Entorno Python

```bash
pip install -r requirements.txt
```

### 3\. Configurar `.env`

Crea un archivo llamado `.env` en la raíz y define:

```ini
KEYDB_HOST=localhost
KEYDB_PORT=6379
```

## ▶️ Ejecución

```bash
python main.py
```

### ¿Por qué `redis-py` si usamos KeyDB?
KeyDB mantiene compatibilidad total con el protocolo de Redis. Por lo tanto, no necesitas una librería especial de Python para KeyDB; la librería estándar de Redis (`redis-py`) funciona perfectamente y es el estándar de la industria.
