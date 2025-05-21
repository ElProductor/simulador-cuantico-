from flask import Flask, Response, request, render_template_string, jsonify
import datetime
import os
import time
import logging
import sys
import tempfile
import base64
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configuración de logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logging.basicConfig(
    level=log_level_map.get(log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

# Función para corregir URL de PostgreSQL para SQLAlchemy
def fix_postgres_url(url):
    """Corrige la URL de PostgreSQL para SQLAlchemy si es necesario."""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url

# Configuración de base de datos si está disponible
database_url = os.environ.get('DATABASE_URL')
if database_url:
    database_url = fix_postgres_url(database_url)
    logging.info(f"Configuración de base de datos detectada")
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.exc import SQLAlchemyError
        
        # Crear engine pero no conectar aún
        engine = create_engine(database_url)
        logging.info("Engine de SQLAlchemy creado correctamente")
    except ImportError:
        logging.warning("SQLAlchemy no está instalado. Funcionalidades de base de datos desactivadas.")
        engine = None
    except Exception as e:
        logging.error(f"Error al configurar la base de datos: {str(e)}")
        engine = None
else:
    logging.info("No se detectó configuración de base de datos. Funcionando sin base de datos.")
    engine = None

def simulate_circuit(circuit_operations):
    """Simula el circuito cuántico dado y devuelve los resultados."""
    from interpreter.qlang_interpreter import qubits, interpret
    import numpy as np
    
    try:
        # Ejecutar cada operación del circuito
        results = {
            "operations": circuit_operations.copy(),
            "qubit_states": {},
            "measurements": {},
            "success": True
        }
        
        # Guardar estados finales de los qubits
        for name, qubit in qubits.items():
            # Obtener vector de estado
            state_vector = qubit.state
            # Calcular probabilidades
            probs = np.abs(state_vector)**2
            # Realizar medición simulada
            measurement = np.random.choice([0, 1], p=probs)
            
            results["qubit_states"][name] = {
                "state_vector": state_vector.tolist(),
                "probabilities": probs.tolist()
            }
            results["measurements"][name] = int(measurement)
        
        logging.info(f"Simulación completada con {len(circuit_operations)} operaciones")
        return results
    except Exception as e:
        logging.error(f"Error en simulación: {str(e)}")
        return {"success": False, "error": str(e)}

def generate_result_visualizations(results):
    """Genera visualizaciones basadas en los resultados de la simulación."""
    import matplotlib
    # Configurar matplotlib para usar un backend no interactivo (necesario para entornos sin GUI como Render)
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import io
    import base64
    import tempfile
    import os
    import json
    
    if not results.get("success", True):
        return f"<div class='alert alert-danger'>Error en la simulación: {results.get('error', 'Desconocido')}</div>"
    
    html_output = "<div class='results-container'>"
    
    # Tabla de resultados de medición
    measurements = results.get("measurements", {})
    if measurements:
        html_output += "<h3>Resultados de Medición</h3>"
        html_output += "<table class='table table-striped table-bordered'>"
        html_output += "<thead><tr><th>Qubit</th><th>Resultado</th></tr></thead><tbody>"
        for qubit, result in measurements.items():
            html_output += f"<tr><td>{qubit}</td><td>{result}</td></tr>"
        html_output += "</tbody></table>"
    
    # Gráfico de probabilidades
    qubit_states = results.get("qubit_states", {})
    if qubit_states:
        try:
            # Gráfico estático con matplotlib
            fig, ax = plt.subplots(figsize=(8, 4))
            qubits = list(qubit_states.keys())
            x = np.arange(len(qubits))
            width = 0.35
            
            # Probabilidad de |0⟩
            prob_0 = [qubit_states[q]["probabilities"][0] for q in qubits]
            # Probabilidad de |1⟩
            prob_1 = [qubit_states[q]["probabilities"][1] for q in qubits]
            
            ax.bar(x - width/2, prob_0, width, label='|0⟩')
            ax.bar(x + width/2, prob_1, width, label='|1⟩')
            
            ax.set_ylabel('Probabilidad')
            ax.set_title('Probabilidades de estados por qubit')
            ax.set_xticks(x)
            ax.set_xticklabels(qubits)
            ax.legend()
            ax.set_ylim(0, 1)
            
            # Usar un directorio temporal seguro para guardar la imagen
            temp_dir = tempfile.gettempdir()
            os.makedirs(temp_dir, exist_ok=True)
            
            # Convertir gráfico a imagen base64
            buf = io.BytesIO()
            plt.tight_layout()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)  # Cerrar la figura para liberar memoria
            img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            # Gráfico interactivo con Plotly
            plotly_data = [
                {
                    'x': qubits,
                    'y': prob_0,
                    'name': '|0⟩',
                    'type': 'bar'
                },
                {
                    'x': qubits,
                    'y': prob_1,
                    'name': '|1⟩',
                    'type': 'bar'
                }
            ]
            
            plotly_config = {
                'displayModeBar': True,
                'responsive': True
            }
            
            html_output += """
            <h3>Visualización Interactiva</h3>
            <div id='plotly-chart'></div>
            <script>
                Plotly.newPlot('plotly-chart', %s, {}, %s);
            </script>
            """ % (json.dumps(plotly_data), json.dumps(plotly_config))
            
            html_output += "<h3>Visualización Estática</h3>"
            html_output += f"<img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;'>"
            html_output += f"<form method='post' action='/download_img' style='display:inline;margin-top:10px;'>"
            html_output += f"<input type='hidden' name='img_data' value='{img_b64}'>"
            html_output += f"<input type='hidden' name='img_name' value='probabilidades.png'>"
            html_output += f"<button type='submit' class='btn btn-primary'><i class='bi bi-download'></i> Descargar gráfico</button>"
            html_output += f"</form>"
            
            # Tutorial paso a paso
            html_output += """
            <div class='tutorial-container mt-4'>
                <h4>Tutorial Rápido</h4>
                <div class='tutorial-step'>
                    <strong>Paso 1:</strong> Observa las probabilidades de cada estado cuántico en el gráfico.
                </div>
                <div class='tutorial-step'>
                    <strong>Paso 2:</strong> Interactúa con el gráfico para ver detalles específicos.
                </div>
                <div class='tutorial-step'>
                    <strong>Paso 3:</strong> Compara los resultados con tus expectativas teóricas.
                </div>
            </div>
            """
            
        except Exception as e:
            logging.error(f"Error al generar gráfico: {str(e)}")
            html_output += f"<div class='alert alert-warning'>No se pudo generar el gráfico: {str(e)}</div>"
    
    # Feedback visual
    html_output += """
    <div class='feedback-section mt-4'>
        <h4>¿Fue útil esta visualización?</h4>
        <button class='btn btn-sm btn-success me-2 feedback-btn' data-value='yes'>Sí</button>
        <button class='btn btn-sm btn-danger feedback-btn' data-value='no'>No</button>
        <div id='feedback-thanks' class='mt-2 text-muted' style='display:none;'>¡Gracias por tu feedback!</div>
    </div>
    <script>
        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('feedback-thanks').style.display = 'block';
                // Aquí podrías agregar código para enviar el feedback al servidor
            });
        });
    </script>
    """
    
    html_output += "</div>"
    return html_output

# Inicializar variables necesarias
try:
    from interpreter.qlang_interpreter import circuit_operations, interpret
except ImportError:
    circuit_operations = []
    # Define a dummy interpret function if the module is not available
    def interpret(operations):
        logging.warning("qlang_interpreter not found. Using dummy interpret function.")
        # Simulate some basic output structure for testing
        return {
            'qubits': {'q0': type('obj', (object,), {'state': [1, 0]})(), 'q1': type('obj', (object,), {'state': [0, 1]})()},
            'classical_bits': {'c0': 0, 'c1': 1}
        }

# HTML base para la interfaz
BASE_HTML = """
<!doctype html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css\" rel=\"stylesheet\">
    <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
    <title>Simulador Cuántico-Clásico</title>
    <style>
        body { background-color: #f4f6fa; }
        .tutorial-container { background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .visualization-panel { transition: all 0.3s ease; }
        .visualization-panel:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .bloch-sphere { width: 100%; height: 400px; margin: 20px 0; }
        .circuit-builder { background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .gate-palette { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
        .quantum-gate { padding: 8px 12px; background: #e9ecef; border-radius: 5px; cursor: grab; }
        .tutorial-step { margin-bottom: 15px; padding: 10px; background: #f1f8ff; border-left: 4px solid #4dabf7; }
        .container { margin-top: 20px; }
        .card { margin-bottom: 20px; }
        .form-control { margin-bottom: 10px; }
        .results-container img { max-width: 100%; height: auto; border: 1px solid #888; }
        .results-container table { margin-top: 15px; }
    </style>
</head>
<body>
    <div class=\"container\">
        <h1 class=\"mb-4 text-center\">Simulador Cuántico-Clásico</h1>
        <div class=\"row\">
            <div class=\"col-md-6\">
                <div class=\"card\">
                    <div class=\"card-header\">Computación Cuántica</div>
                    <div class=\"card-body\">
                        <form method=\"post\" action=\"/run_quantum\">
                            <div class=\"mb-3\">
                                <label for=\"quantum_code\" class=\"form-label\">Código QLang:</label>
                                <textarea class=\"form-control\" id=\"quantum_code\" name=\"quantum_code\" rows=\"10\">{{ quantum_code }}</textarea>
                            </div>
                            <button type=\"submit\" class=\"btn btn-primary\"><i class=\"bi bi-play-fill\"></i> Ejecutar Circuito Cuántico</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class=\"col-md-6\">
                <div class=\"card\">
                    <div class=\"card-header\">Computación Clásica (Ejemplo)</div>
                    <div class=\"card-body\">
                         <form method=\"post\" action=\"/run_classical\">
                            <div class=\"mb-3\">
                                <label for=\"classical_input\" class=\"form-label\">Entrada Clásica:</label>
                                <input type=\"text\" class=\"form-control\" id=\"classical_input\" name=\"classical_input\" value=\"{{ classical_input }}\" placeholder=\"Introduce texto o números\">
                            </div>
                            <button type=\"submit\" class=\"btn btn-success mt-3\">Ejecutar Clásico</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <div class=\"row\">
            <div class=\"col-12\">
                <div class=\"card\">
                    <div class=\"card-header\">Resultados</div>
                    <div class=\"card-body\">
                        {{ results_html | safe }}
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(BASE_HTML, quantum_code="", classical_input="", results_html="")

@app.route('/run_quantum', methods=['POST'])
def run_quantum():
    quantum_code = request.form.get('quantum_code', '')
    # Lógica para interpretar el código QLang y simular el circuito
    try:
        if not quantum_code or quantum_code.strip() == "":
            logging.warning("Se intentó ejecutar código cuántico vacío")
            return render_template_string(BASE_HTML, 
                                         quantum_code="", 
                                         classical_input="", 
                                         results_html="<div class='alert alert-warning'>Por favor, ingrese código QLang para ejecutar.</div>")
        
        logging.info(f"Ejecutando código cuántico: {quantum_code[:50]}...")
        
        # Asumiendo que interpret() maneja la ejecución y el estado de los qubits
        try:
            interpretation_results = interpret(quantum_code)
            logging.info("Interpretación completada correctamente")
        except Exception as interp_error:
            logging.error(f"Error durante la interpretación: {str(interp_error)}")
            return render_template_string(BASE_HTML, 
                                         quantum_code=quantum_code, 
                                         classical_input="", 
                                         results_html=f"<div class='alert alert-danger'>Error en la interpretación: {str(interp_error)}</div>")
        
        # La función simulate_circuit ya está definida para usar el estado global de qubits
        # después de la interpretación.
        try:
            simulation_results = simulate_circuit(interpretation_results.get('operations', []))
            logging.info("Simulación completada correctamente")
        except Exception as sim_error:
            logging.error(f"Error durante la simulación: {str(sim_error)}")
            return render_template_string(BASE_HTML, 
                                         quantum_code=quantum_code, 
                                         classical_input="", 
                                         results_html=f"<div class='alert alert-danger'>Error en la simulación: {str(sim_error)}</div>")
        
        if simulation_results.get("success", False):
            results_html = generate_result_visualizations(simulation_results)
        else:
            error_msg = simulation_results.get('error', 'Desconocido')
            logging.error(f"Simulación fallida: {error_msg}")
            results_html = f"<div class='alert alert-danger'>Error en la simulación: {error_msg}</div>"
            
    except Exception as e:
        logging.error(f"Error general durante el procesamiento: {str(e)}")
        results_html = f"<div class='alert alert-danger'>Error en el procesamiento: {str(e)}</div>"
    
    return render_template_string(BASE_HTML, quantum_code=quantum_code, classical_input="", results_html=results_html)

@app.route('/run_classical', methods=['POST'])
def run_classical():
    classical_input = request.form.get('classical_input', '')
    # Aquí iría la lógica para procesar la entrada clásica
    # Por ahora, solo devolvemos un mensaje simple
    results_html = f"<div class='alert alert-info'>Entrada clásica recibida: {classical_input}</div>"
    return render_template_string(BASE_HTML, quantum_code="", classical_input=classical_input, results_html=results_html)

# Añadir ruta para descargar imágenes
@app.route('/download_img', methods=['POST'])
def download_img():
    try:
        img_data = request.form.get('img_data', '')
        if not img_data:
            logging.error("No se proporcionaron datos de imagen para descargar")
            return "<div class='alert alert-danger'>Error: No se proporcionaron datos de imagen</div>", 400
            
        img_name = request.form.get('img_name', 'imagen.png')
        img_bytes = base64.b64decode(img_data)
        
        # Asegurar que el nombre del archivo sea seguro
        img_name = os.path.basename(img_name)
        
        return Response(img_bytes, mimetype='image/png', headers={'Content-Disposition': f'attachment;filename={img_name}'})
    except Exception as e:
        logging.error(f"Error al procesar la descarga de imagen: {str(e)}")
        return "<div class='alert alert-danger'>Error al procesar la descarga</div>", 500

# Configuración para manejo de archivos temporales en Render
@app.before_request
def before_request():
    # Asegurarse de que las carpetas temporales existan
    # Usar tempfile para obtener el directorio temporal del sistema
    temp_dir = tempfile.gettempdir()
    os.makedirs(temp_dir, exist_ok=True)
    # En Render, asegurarse de que /tmp exista
    if os.environ.get('RENDER') and os.name != 'nt':
        os.makedirs('/tmp', exist_ok=True)
    
    # Configurar variables de entorno específicas para Render si es necesario
    if os.environ.get('RENDER') and not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'

# Endpoints de diagnóstico para Render
@app.route('/api/health')
def health_check():
    """Endpoint para verificar el estado de la aplicación."""
    status = {
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'render_instance': bool(os.environ.get('RENDER')),
        'python_version': sys.version,
        'database_configured': database_url is not None,
        'temp_dir_writable': os.access(tempfile.gettempdir(), os.W_OK)
    }
    
    # Verificar conexión a la base de datos si está configurada
    if engine:
        try:
            with engine.connect() as conn:
                status['database_connection'] = 'ok'
        except Exception as e:
            status['database_connection'] = 'error'
            status['database_error'] = str(e)
    
    return jsonify(status)

@app.route('/dbtest')
def db_test():
    """Endpoint para probar la conexión a la base de datos."""
    if not engine:
        return jsonify({
            'status': 'not_configured',
            'message': 'No se ha configurado una conexión a la base de datos.'
        })
    
    try:
        # Intentar conectar a la base de datos
        with engine.connect() as conn:
            # Ejecutar una consulta simple
            result = conn.execute("SELECT 1 as test").fetchone()
            if result and result[0] == 1:
                return jsonify({
                    'status': 'ok',
                    'message': 'Conexión a la base de datos exitosa',
                    'database_url_type': 'postgresql' if database_url and 'postgresql://' in database_url else 'unknown'
                })
    except Exception as e:
        logging.error(f"Error al probar la conexión a la base de datos: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error al conectar a la base de datos: {str(e)}',
            'database_url_type': 'postgresql' if database_url and 'postgresql://' in database_url else 'unknown'
        })

# Configuración para manejo de errores
@app.errorhandler(500)
def server_error(e):
    logging.exception('Error interno del servidor')
    return "<h1>Error interno del servidor</h1><p>El servidor encontró un error. Por favor, inténtelo de nuevo más tarde.</p>", 500

if __name__ == '__main__':
    # Configuración para entorno de desarrollo y producción
    port = int(os.environ.get('PORT', 5000))
    
    # Detección mejorada del entorno
    is_production = os.environ.get('RENDER') or os.environ.get('PRODUCTION') or os.environ.get('FLASK_ENV') == 'production'
    debug_mode = not is_production
    
    # En producción, asegurarse de que debug esté desactivado
    if is_production:
        debug_mode = False
        logging.info("Ejecutando en modo producción")
    else:
        logging.info("Ejecutando en modo desarrollo")
    
    # Configuración de servidor para Render
    host = '0.0.0.0'  # Necesario para Render
    logging.info(f"Iniciando servidor en {host}:{port} (debug: {debug_mode})")
    
    # Mostrar información de diagnóstico al inicio
    logging.info(f"Versión de Python: {sys.version}")
    logging.info(f"Directorio temporal: {tempfile.gettempdir()}")
    logging.info(f"Base de datos configurada: {database_url is not None}")
    logging.info(f"Entorno detectado: {'Render' if os.environ.get('RENDER') else 'Local'}")
    
    # Verificar conexión a la base de datos si está configurada
    if engine:
        try:
            with engine.connect() as conn:
                logging.info("Conexión a la base de datos verificada correctamente")
        except Exception as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            logging.info("La aplicación continuará funcionando sin conexión a la base de datos")
    
    try:
        app.run(host=host, port=port, debug=debug_mode)
    except Exception as e:
        logging.error(f"Error al iniciar el servidor: {str(e)}")
        sys.exit(1)