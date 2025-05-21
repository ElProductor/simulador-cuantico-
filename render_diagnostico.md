# Diagnóstico y Solución de Problemas en Render

Este documento proporciona instrucciones detalladas para diagnosticar y solucionar problemas específicos al desplegar el Simulador Cuántico en Render. Sigue esta guía paso a paso para resolver los problemas más comunes y optimizar tu experiencia con la plataforma.

## Endpoints de Diagnóstico

La aplicación incluye endpoints específicos para diagnóstico que te ayudarán a identificar y resolver problemas rápidamente:

### `/api/health`

Proporciona información completa sobre el estado de la aplicación:

```json
{
  "status": "ok",
  "timestamp": "2023-09-15T12:34:56.789012",
  "environment": "production",
  "render_instance": true,
  "python_version": "3.10.13",
  "database_configured": true,
  "temp_dir_writable": true,
  "database_connection": "ok"
}
```

Si hay problemas, el campo `status` mostrará "error" y se incluirán detalles adicionales.

### `/dbtest`

Prueba específicamente la conexión a la base de datos:

```json
{
  "status": "ok",
  "message": "Conexión a la base de datos exitosa",
  "database_url_type": "postgresql"
}
```

## Solución de Problemas Comunes

### 1. Error "Bad Gateway"

Si encuentras este error al acceder a tu aplicación, sigue estos pasos en orden:

1. **Verifica los logs en Render**:
   - Accede al dashboard de Render > Tu servicio > Logs
   - Busca mensajes de error específicos como "ImportError", "ModuleNotFoundError" o "SyntaxError"
   - Presta atención a errores relacionados con dependencias o configuración

2. **Verifica el estado de la aplicación**:
   - Accede a `https://tu-app.onrender.com/api/health`
   - Revisa el estado general y los detalles proporcionados
   - Verifica que todos los componentes muestren "ok" en su estado

3. **Problemas de inicio**:
   - La aplicación puede tardar hasta 2-3 minutos en iniciar completamente
   - Verifica si hay errores de importación o dependencias faltantes en los logs
   - Si la aplicación se reinicia constantemente, revisa los límites de memoria

### 2. Problemas con la Base de Datos

1. **Verifica la conexión**:
   - Accede a `https://tu-app.onrender.com/dbtest`
   - Si muestra error, verifica que la base de datos esté activa en Render

2. **Formato de URL incorrecto**:
   - La aplicación ahora corrige automáticamente URLs que comienzan con `postgres://` a `postgresql://`
   - Si sigues teniendo problemas, verifica manualmente el formato en las variables de entorno de Render

3. **Reinicio de la base de datos**:
   - En algunos casos, puede ser necesario reiniciar la base de datos desde el dashboard de Render

### 3. Problemas de Memoria o Recursos

1. **Errores de memoria**:
   - Si ves errores como "MemoryError" o la aplicación se cierra inesperadamente
   - Considera actualizar a un plan con más recursos

2. **Operaciones intensivas**:
   - Las simulaciones cuánticas complejas pueden requerir más recursos
   - Limita la complejidad de los circuitos en entornos con recursos limitados

### 4. Problemas con Archivos Temporales

1. **Errores al generar gráficos**:
   - La aplicación ahora utiliza `tempfile.gettempdir()` para determinar el directorio temporal adecuado
   - Verifica que el directorio temporal sea escribible en `/api/health`

## Variables de Entorno Importantes

- `PYTHON_VERSION`: 3.10.13 (requerido para compatibilidad con todas las dependencias)
- `FLASK_ENV`: production (recomendado en Render para optimizar rendimiento)
- `LOG_LEVEL`: INFO (o DEBUG para más detalles durante la resolución de problemas)
- `DATABASE_URL`: Configurada automáticamente si usas una base de datos en Render
- `RENDER`: true (ayuda a la aplicación a detectar que está en Render y ajustar configuraciones)

## Navegación y Experiencia de Usuario

El simulador cuántico incluye una interfaz mejorada con las siguientes características:

### Navegación Intuitiva

- **Menú Principal**: Acceso rápido a todas las funcionalidades desde la página principal
  - Sección de Circuitos Cuánticos: Diseño y ejecución de circuitos
  - Sección de Computación Clásica: Comparación con operaciones clásicas
  - Sección de Resultados: Visualización detallada de las simulaciones
- **Barra de Herramientas**: Contiene acciones comunes como guardar, cargar y ejecutar circuitos
  - Botones con iconos intuitivos para cada acción
  - Acceso rápido a operaciones frecuentes
  - Indicadores visuales del estado de la simulación
- **Panel de Ayuda Contextual**: Disponible en cada sección con instrucciones específicas
  - Ayuda sensible al contexto según la operación actual
  - Ejemplos relevantes para cada tipo de operación
  - Enlaces a recursos adicionales de aprendizaje

### Visualizaciones Interactivas

- **Gráficos Dinámicos**: Visualiza las probabilidades de estados cuánticos en tiempo real
  - Actualización automática después de cada operación
  - Opciones para personalizar la visualización
  - Posibilidad de descargar gráficos en formato PNG
- **Circuitos Interactivos**: Interfaz drag-and-drop para construir circuitos
  - Biblioteca visual de compuertas cuánticas
  - Validación instantánea de circuitos
  - Representación gráfica del circuito en tiempo real
- **Animaciones de Estados**: Observa la evolución de los estados cuánticos durante la simulación
  - Visualización de la esfera de Bloch para estados de un qubit
  - Animación paso a paso de las transformaciones
  - Control de velocidad para análisis detallado

### Tutoriales Integrados

- **Guías Paso a Paso**: Aprende a usar el simulador con ejemplos prácticos
  - Tutorial interactivo para principiantes
  - Ejercicios progresivos de dificultad creciente
  - Retroalimentación inmediata sobre cada paso
- **Ejemplos Predefinidos**: Biblioteca de circuitos de ejemplo para entender conceptos cuánticos
  - Algoritmos cuánticos fundamentales (Deutsch, Grover, etc.)
  - Ejemplos de entrelazamiento y superposición
  - Casos prácticos con explicaciones detalladas
- **Tooltips Informativos**: Información detallada sobre cada elemento al pasar el cursor
  - Descripción de compuertas y sus matrices
  - Fórmulas matemáticas relevantes
  - Referencias a conceptos teóricos

## Verificación de Despliegue

Después de desplegar, sigue esta lista de verificación completa:

1. **Verificación básica**:
   - Que la aplicación responda correctamente en la URL principal
   - Que la interfaz se cargue completamente con todos sus elementos visuales
   - Que no haya errores de JavaScript en la consola del navegador

2. **Verificación de diagnóstico**:
   - Que `/api/health` muestre estado "ok" en todos los componentes
   - Que `/dbtest` muestre conexión exitosa (si usas base de datos)

3. **Verificación funcional**:
   - Que puedas ejecutar simulaciones cuánticas básicas
   - Que los gráficos y visualizaciones se generen correctamente
   - Que puedas descargar los resultados de las simulaciones

4. **Verificación de rendimiento**:
   - Que el tiempo de carga inicial sea razonable (menos de 5 segundos)
   - Que las simulaciones complejas se ejecuten sin errores de memoria
   - Que la aplicación responda rápidamente a las interacciones del usuario

## Contacto y Soporte

Si encuentras problemas adicionales después de seguir estas instrucciones, por favor:

1. **Recopila información**:
   - Revisa los logs completos en Render
   - Captura la respuesta de `/api/health` y `/dbtest`
   - Anota los pasos exactos para reproducir el problema

2. **Reporta el problema**:
   - Crea un issue en el repositorio de GitHub con los detalles del problema
   - Utiliza el formato de reporte de errores proporcionado en la plantilla
   - Incluye capturas de pantalla si son relevantes

3. **Soluciones temporales**:
   - Consulta la sección de problemas conocidos en el repositorio
   - Prueba reiniciar el servicio en Render
   - Verifica si hay actualizaciones disponibles para el simulador

## Recursos Adicionales

- [Documentación oficial de Render](https://render.com/docs)
- [Guía de Flask en producción](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Tutoriales del Simulador Cuántico](https://github.com/yourusername/simulador-cuantico/wiki)
- [Comunidad de Soporte](https://discord.gg/simuladorcuantico)