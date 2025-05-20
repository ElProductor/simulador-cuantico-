# Simulador Cuántico Web

Aplicación web para simulación de circuitos cuánticos desarrollada con Flask.

## Requisitos

- Python 3.10.13
- PostgreSQL (opcional, para funcionalidades avanzadas)
- Dependencias listadas en `requirements.txt`

## Instalación local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar la aplicación: `python webapp.py`

## Despliegue en Render

Esta aplicación está configurada para ser desplegada en [Render](https://render.com). Sigue estos pasos para un despliegue exitoso:

### 1. Configuración en Render

1. Crea una cuenta en [Render](https://render.com) si aún no tienes una
2. Conecta tu repositorio de GitHub a Render
3. Crea un nuevo servicio web:
   - Selecciona tu repositorio
   - Nombre: `simulador-cuantico` (o el que prefieras)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn webapp:app`

### 2. Configuración de la base de datos (opcional)

Si necesitas funcionalidades que requieren base de datos:

1. Crea una nueva base de datos PostgreSQL en Render
2. En la configuración de tu servicio web, añade la variable de entorno `DATABASE_URL` con el valor de la cadena de conexión proporcionada por Render

### 3. Variables de entorno

Configura las siguientes variables de entorno en tu servicio web de Render:

- `PYTHON_VERSION`: 3.10.13
- `DATABASE_URL`: URL de conexión a tu base de datos PostgreSQL (si aplica)
- `FLASK_ENV`: production

## Solución de problemas

### Error "Bad Gateway"

Si encuentras un error "Bad Gateway" al acceder a tu aplicación desplegada, prueba las siguientes soluciones:

1. **Verifica los logs de Render**: Revisa los logs en el dashboard de Render para identificar errores específicos.

2. **Problemas con la base de datos**:
   - Asegúrate de que la variable `DATABASE_URL` esté correctamente configurada
   - Verifica que la base de datos esté activa y accesible
   - La aplicación ahora maneja automáticamente la conversión de `postgres://` a `postgresql://` para compatibilidad con Render

3. **Problemas de memoria o CPU**:
   - Considera actualizar a un plan con más recursos si la aplicación consume demasiada memoria o CPU

4. **Tiempo de inicio**:
   - La aplicación puede tardar en iniciar la primera vez. Espera unos minutos y vuelve a intentarlo.

5. **Dependencias**:
   - Asegúrate de que todas las dependencias estén correctamente listadas en `requirements.txt`

## Archivos de configuración

- `render.yaml`: Configuración para despliegue automático en Render
- `Procfile`: Especifica el comando para iniciar la aplicación
- `runtime.txt`: Especifica la versión de Python
- `requirements.txt`: Lista de dependencias

## Contacto

Si encuentras problemas adicionales, por favor crea un issue en el repositorio de GitHub.