# Solución de problemas en Render

## Error "Bad Gateway"

Si estás experimentando el error "Bad Gateway" en tu aplicación desplegada en Render, sigue estos pasos para diagnosticar y resolver el problema:

### 1. Verificar los logs de Render

Lo primero que debes hacer es revisar los logs en el dashboard de Render:

1. Inicia sesión en tu cuenta de Render
2. Navega hasta tu servicio web
3. Haz clic en la pestaña "Logs"
4. Busca mensajes de error específicos

### 2. Problemas comunes y soluciones

#### Problemas con la base de datos

- **Conexión fallida**: Verifica que la variable `DATABASE_URL` esté correctamente configurada en las variables de entorno de Render.
- **Formato de URL incorrecto**: La aplicación ahora maneja automáticamente la conversión de `postgres://` a `postgresql://` para compatibilidad con Render.
- **Base de datos inaccesible**: Asegúrate de que tu base de datos esté activa y accesible desde el servicio web.

#### Problemas de inicio de la aplicación

- **Dependencias faltantes**: Verifica que todas las dependencias estén correctamente listadas en `requirements.txt`.
- **Errores de importación**: Revisa los logs para identificar posibles errores de importación de módulos.
- **Tiempo de inicio**: La aplicación puede tardar en iniciar la primera vez. Espera unos minutos y vuelve a intentarlo.

#### Problemas de recursos

- **Memoria insuficiente**: Si la aplicación consume demasiada memoria, considera actualizar a un plan con más recursos.
- **CPU limitada**: Las operaciones intensivas pueden requerir más CPU. Considera un plan superior.

### 3. Verificación manual

Puedes verificar el estado de tu aplicación y la conexión a la base de datos accediendo a estos endpoints:

- `/api/health` - Muestra el estado general de la aplicación y sus dependencias
- `/dbtest` - Prueba específicamente la conexión a la base de datos PostgreSQL

### 4. Soluciones específicas

#### Si el problema es la base de datos

1. Verifica que la base de datos esté en ejecución en Render
2. Confirma que las credenciales sean correctas
3. Asegúrate de que la URL de conexión tenga el formato correcto

#### Si el problema es de memoria o recursos

1. Actualiza tu plan en Render a uno con más recursos
2. Optimiza tu código para usar menos memoria

#### Si el problema es de dependencias

1. Verifica que todas las dependencias estén en `requirements.txt`
2. Asegúrate de que las versiones sean compatibles

### 5. Contactar soporte

Si después de intentar estas soluciones el problema persiste, contacta al soporte de Render con la siguiente información:

- ID de la solicitud (Request ID) del error
- Logs de la aplicación
- Detalles de configuración (sin incluir credenciales o secretos)

### 6. Prevención

Para evitar este problema en el futuro:

- Implementa verificaciones de salud robustas
- Maneja adecuadamente los errores de conexión a la base de datos
- Configura reintentos para operaciones que pueden fallar temporalmente
- Mantén actualizadas tus dependencias