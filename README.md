# Fondos ONG

Aplicación web hecha con Django para manejar información de fondos, proyectos, presupuestos, donaciones y órdenes de compra para una ONG.

La idea de este README es dejar los pasos básicos para que otro desarrollador pueda levantar el proyecto localmente sin perderse mucho.

## Requisitos

Necesitas tener instalado:

- Python 3.13 o superior
- Git
- Opcional: `uv`, si quieres usar el flujo más rápido para crear el entorno e instalar dependencias

Para revisar tu versión de Python:

```bash
python3 --version
```

También puedes descargarlo desde la página oficial:

https://www.python.org/downloads/

## Clonar el proyecto

```bash
git clone git@github-alejandro:munoz-alejandro/presupuestos_ong.git
cd presupuestos_ong
```

Si estás usando HTTPS en lugar de SSH, el clone sería algo como:

```bash
git clone https://github.com/munoz-alejandro/presupuestos_ong.git
cd presupuestos_ong
```

## Opción 1: levantar el entorno con uv

Si no tienes `uv`, lo puedes instalar así:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Luego, dentro de la carpeta del proyecto:

```bash
uv sync
```

Eso crea el entorno virtual e instala las dependencias usando `pyproject.toml` y `uv.lock`.

Para correr comandos de Django usando `uv`, puedes usar:

```bash
uv run python manage.py <comando>
```

Por ejemplo:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

## Opción 2: levantar el entorno con venv y pip

Si prefieres usar el flujo normal de Python, crea el entorno virtual así:

```bash
python3 -m venv .venv
```

Actívalo:

```bash
source .venv/bin/activate
```

Actualiza `pip`:

```bash
python -m pip install --upgrade pip
```

Instala las dependencias desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

Si todo salió bien, ya deberías poder usar Django desde ese entorno virtual.

## Ejecutar migraciones

Antes de correr la app por primera vez, hay que crear o actualizar la base de datos local, para hacer esto mas liviano, estamos usando sqlite:

```bash
python manage.py migrate
```

Si estás usando `uv`, el mismo comando sería:

```bash
uv run python manage.py migrate
```

Esto crea el archivo local `db.sqlite3` con las tablas necesarias. Ese archivo no se sube al repositorio porque es una base de datos local de desarrollo.

## Revisar la base de datos SQLite

Para inspeccionar la base de datos o correr consultas, recomiendo usar esta extensión de VS Code:

```text
SQLite
Autor: alexcvzz
```

La extensión sirve para explorar y consultar bases de datos SQLite directamente desde VS Code.

En este proyecto hay un archivo `consultas.sql`. Para ejecutarlas:

1. Abre `consultas.sql` en VS Code.
2. Presiona `Ctrl + Shift + P`.
3. Busca y ejecuta el comando para correr la consulta de SQLite.

También puedes abrir el archivo `db.sqlite3` desde la extensión para ver las tablas y datos de forma visual.

## Correr la aplicación

Con el entorno virtual activado:

```bash
python manage.py runserver
```

O usando `uv`:

```bash
uv run python manage.py runserver
```

Después abre esta URL en el navegador:

```text
http://127.0.0.1:8000/
```

## Resumen rápido

Con `uv`:

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Con `venv` y `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
