# Robustez ante errores de importación y dependencias
import os
import sys
import logging
import datetime
import time

# Configuración de logging mejorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importaciones con manejo de errores robusto
try:
    import matplotlib
    matplotlib.use('Agg')  # Ensure compatibility with non-GUI environments
    os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp', '.matplotlib')
    import numpy as np
    import io
    import base64
    from flask import Flask, render_template_string, request, jsonify, Response
    logger.info("Importaciones básicas completadas con éxito")
except ImportError as e:
    logger.critical(f"Error de importación crítica: {e}")
    # No terminamos el proceso, pero registramos el error
    logger.error(f"Dependencia faltante: {e}. Por favor, revisa requirements.txt e instala las dependencias.")

# Asegurar que el directorio temporal existe
try:
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp'), exist_ok=True)
    logger.info("Directorio temporal creado/verificado correctamente")
except Exception as e:
    logger.warning(f"No se pudo crear el directorio temporal: {e}")

# Importar módulos de la aplicación con manejo de errores
try:
    from interpreter.qlang_interpreter import qubits, interpret
    logger.info("Módulos de la aplicación importados correctamente")
except ImportError as e:
    logger.error(f"Error al importar módulos de la aplicación: {e}")

app = Flask(__name__)

# Verificar la conexión a la base de datos durante el inicio
def check_database_connection():
    """
    Verifica la conexión a la base de datos con manejo robusto de errores.
    
    Returns:
        bool: True si la conexión es exitosa o se configuró por defecto
    """
    logger.info("Verificando conexión a la base de datos durante el inicio")
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            logger.warning("Variable DATABASE_URL no configurada. La aplicación funcionará sin base de datos.")
            # Configurar valores por defecto para evitar errores
            os.environ['DATABASE_URL'] = "postgresql://localhost:5432/quantum_sim"
            DATABASE_URL = os.environ['DATABASE_URL']
            logger.info("Configurada URL de base de datos por defecto")
            return True
            
        # Manejar URL de Render que comienza con postgres:// en lugar de postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            logger.info("URL de base de datos convertida de postgres:// a postgresql://")
        
        # Intentar conexión con reintentos
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento de conexión a la base de datos {attempt+1}/{max_retries}")
                conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
                conn.close()
                logger.info("Conexión a la base de datos exitosa durante el inicio")
                return True
            except Exception as e:
                logger.warning(f"Intento {attempt+1} fallido: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Esperando {retry_delay} segundos antes del siguiente intento...")
                    time.sleep(retry_delay)
        
        logger.error(f"No se pudo conectar a la base de datos después de {max_retries} intentos")
        logger.warning("La aplicación continuará ejecutándose sin funcionalidades de base de datos")
        return False
    except ImportError as e:
        logger.warning(f"Módulo psycopg2 no instalado: {str(e)}. La aplicación funcionará sin base de datos.")
        # Configurar valores por defecto para evitar errores
        os.environ['DATABASE_URL'] = "postgresql://localhost:5432/quantum_sim"
        logger.info("Configurada URL de base de datos por defecto")
        return True
    except psycopg2.OperationalError as e:
        logger.error(f"Error operacional de la base de datos: {str(e)}")
        return False
    except psycopg2.ProgrammingError as e:
        logger.error(f"Error de programación en la base de datos: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al verificar la base de datos: {str(e)}", exc_info=True)
        return False

# Intentar verificar la conexión a la base de datos al inicio, pero no bloquear el arranque
try:
    check_database_connection()
except Exception as e:
    logger.error(f"Error al verificar la base de datos durante el inicio: {e}")
    logger.warning("La aplicación continuará ejecutándose con funcionalidad limitada")

# Configurar manejo de errores para la aplicación
@app.errorhandler(500)
def server_error(e):
    # Registrar información detallada del error
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_details = {
        'type': str(exc_type),
        'message': str(exc_value),
        'traceback': ''.join(traceback.format_tb(exc_traceback)),
        'request': {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'data': request.data.decode('utf-8') if request.data else None,
            'form': dict(request.form),
            'args': dict(request.args)
        },
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    logger.error(f"Error interno del servidor - Detalles: {json.dumps(error_details, indent=2)}")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error - Simulador Cuántico</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .error-container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            h1 { color: #d9534f; }
            .back-link { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Error del servidor</h1>
            <p>Lo sentimos, ha ocurrido un error al procesar tu solicitud.</p>
            <p>El equipo técnico ha sido notificado y estamos trabajando para resolverlo.</p>
            <div class="back-link"><a href="/">Volver al inicio</a></div>
        </div>
    </body>
    </html>
    """), 500

def build_navbar(active=None):
    # Diccionario de rutas y nombres con íconos
    items = [
        ('qubits', 'Qubits', 'bi-cpu'),
        ('circuit', 'Circuito', 'bi-diagram-3'),
        ('visualization', 'Visualización', 'bi-bar-chart'),
        ('simulate', 'Simular', 'bi-play-circle'),
        ('algorithms', 'Algoritmos', 'bi-lightbulb'),
        ('metrics', 'Métricas', 'bi-graph-up'),
        ('classic', 'Clásica', 'bi-calculator'),
        ('glossary', 'Glosario', 'bi-book'),
        ('tutorial', 'Tutorial', 'bi-mortarboard'),
        ('decoherence', 'Decoherencia', 'bi-cloud-drizzle'),
        ('history', 'Historial', 'bi-clock-history'),
        ('ai', 'IA', 'bi-robot'),
        ('exercises', 'Ejercicios', 'bi-trophy'),
        ('references', 'Referencias', 'bi-journal-bookmark'),
        ('export', 'Exportar+', 'bi-box-arrow-up'),
    ]
    nav = "<nav class='navbar navbar-expand-lg navbar-dark bg-dark mb-4'><div class='container-fluid'>"
    nav += "<a class='navbar-brand' href='/'><i class='bi bi-atom'></i> Simulador Cuántico</a>"
    nav += "<button class='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#navbarNav'><span class='navbar-toggler-icon'></span></button>"
    nav += "<div class='collapse navbar-collapse' id='navbarNav'><ul class='navbar-nav me-auto mb-2 mb-lg-0'>"
    for route, name, icon in items:
        active_class = ' active' if active == route else ''
        nav += f"<li class='nav-item'><a class='nav-link{active_class}' href='/{route}'><i class='bi {icon}'></i> {name}</a></li>"
    nav += "</ul></div></div></nav>"
    return nav

NAVBAR = build_navbar()

BOOTSTRAP_HEAD = """
<!DOCTYPE html>
<html lang='es'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Simulador Cuántico</title>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'>
  <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'></script>
  <style>
    body { background: #f8f9fa; }
    .card { margin-bottom: 1.5rem; animation: fadein 0.7s; }
    .navbar-brand { font-weight: bold; }
    .btn-primary, .btn-danger, .btn-success { min-width: 120px; }
    .table th, .table td { vertical-align: middle; }
    .form-label { font-weight: 500; }
    .feedback { margin-top: 10px; }
    .fade-in { animation: fadein 0.7s; }
    @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
    .help-fab {
      position: fixed; bottom: 30px; right: 30px; z-index: 9999;
      background: #0d6efd; color: #fff; border-radius: 50%; width: 56px; height: 56px;
      display: flex; align-items: center; justify-content: center; font-size: 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2); cursor: pointer;
    }
    .help-fab:hover { background: #084298; }
    .footer {
      background: #222; color: #bbb; padding: 16px 0; text-align: center; margin-top: 40px;
    }
    .footer a { color: #0d6efd; text-decoration: underline; }
  </style>
</head>
<body>
<div id='helpModal' class='modal fade' tabindex='-1'>
  <div class='modal-dialog'>
    <div class='modal-content'>
      <div class='modal-header'>
        <h5 class='modal-title'><i class='bi bi-info-circle'></i> Ayuda rápida</h5>
        <button type='button' class='btn-close' data-bs-dismiss='modal'></button>
      </div>
      <div class='modal-body'>
        <ul>
          <li>Usa el panel <b>Qubits</b> para crear, eliminar y manipular qubits individuales.</li>
          <li>En <b>Circuito</b> puedes construir y visualizar circuitos cuánticos paso a paso.</li>
          <li>El panel <b>Visualización</b> muestra métricas globales, mapas de fidelidad y entrelazamiento.</li>
          <li>En <b>Simular</b> ejecuta el circuito y descarga resultados o visualizaciones.</li>
          <li>Haz clic en los <i class='bi bi-question-circle'></i> para ver más información contextual.</li>
        </ul>
      </div>
    </div>
  </div>
</div>
<button class='help-fab' title='Ayuda' data-bs-toggle='modal' data-bs-target='#helpModal'><i class='bi bi-question-circle'></i></button>
"""

TOOLTIP_SCRIPT = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});
</script>
'''

FOOTER = """
<div class='footer'>
  Simulador Cuántico Web &copy; 2025 | Desarrollado por <a href='https://github.com/ElProductor/simulador-cuantico-' target='_blank'><i class='bi bi-github'></i> GitHub</a>
</div>
</body></html>
"""

# Botón flotante de feedback
FEEDBACK_BUTTON = """
<button class='help-fab' title='Enviar feedback' data-bs-toggle='modal' data-bs-target='#feedbackModal' style='right:100px;background:#28a745;'>
  <i class='bi bi-chat-dots'></i>
</button>
<div id='feedbackModal' class='modal fade' tabindex='-1'>
  <div class='modal-dialog'>
    <div class='modal-content'>
      <div class='modal-header'>
        <h5 class='modal-title'><i class='bi bi-chat-dots'></i> Enviar feedback</h5>
        <button type='button' class='btn-close' data-bs-dismiss='modal'></button>
      </div>
      <form method='post' action='/feedback'>
      <div class='modal-body'>
        <label class='form-label'>¿Cómo podemos mejorar?</label>
        <textarea class='form-control' name='feedback' rows='4' required></textarea>
      </div>
      <div class='modal-footer'>
        <button type='submit' class='btn btn-success'>Enviar</button>
      </div>
      </form>
    </div>
  </div>
</div>
"""

@app.route('/')
def index():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='index') +
        """
    <div class='container fade-in'>
      <div class='row justify-content-center'>
        <div class='col-md-8'>
          <div class='card shadow'>
            <div class='card-body'>
              <h1 class='card-title mb-3'><i class='bi bi-cpu'></i> Simulador Cuántico (Web)</h1>
              <p class='lead'>¡Bienvenido! Selecciona un panel del menú para comenzar.</p>
              <form method='post' action='/dbtest'>
                <button type='submit' class='btn btn-outline-secondary'><i class='bi bi-database-check'></i> Probar conexión a PostgreSQL</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/classic', methods=['GET', 'POST'])
def classic_panel():
    """Panel para operaciones de computación clásica"""
    msg = ''
    if request.method == 'POST':
        # Crear bit clásico
        name = request.form.get('bit_name', '').strip()
        # Eliminar bit
        delete_name = request.form.get('delete_bit', '').strip()
        action = request.form.get('action', '')
        operation = request.form.get('operation', '')
        
        if name and not action:
            if name in qubits:
                msg = f"<span style='color:red'>El bit '{name}' ya existe.</span>"
            else:
                interpret(f"BIT {name}")
                msg = f"<span style='color:green'>Bit '{name}' creado.</span>"
        elif action == 'delete' and delete_name:
            if delete_name in qubits:
                interpret(f"DELETE {delete_name}")
                msg = f"<span style='color:green'>Bit '{delete_name}' eliminado.</span>"
            else:
                msg = f"<span style='color:red'>El bit '{delete_name}' no existe.</span>"
        elif action == 'delete' and not delete_name:
            msg = "<span style='color:red'>Selecciona un bit para eliminar.</span>"
        elif action == 'reset_all':
            interpret("RESETALL")
            msg = "<span style='color:green'>Todos los bits fueron reseteados.</span>"
        elif operation and action == 'operate':
            bit1 = request.form.get('bit1', '')
            bit2 = request.form.get('bit2', '')
            if bit1 and bit2 and bit1 in qubits and bit2 in qubits:
                interpret(f"{operation.upper()} {bit1} {bit2}")
                msg = f"<span style='color:green'>Operación {operation} realizada entre {bit1} y {bit2}.</span>"
            else:
                msg = "<span style='color:red'>Selecciona bits válidos para operar.</span>"
    
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='classic') +
        """
    <div class='container fade-in'>
      <div class='row justify-content-center'>
        <div class='col-md-10'>
          <div class='card shadow'>
            <div class='card-body'>
              <h1 class='card-title mb-3'><i class='bi bi-calculator'></i> Computación Clásica</h1>
              <p class='lead'>Administra bits clásicos y realiza operaciones lógicas avanzadas.</p>
              
              <div class='mb-4'>""" + msg + """</div>
              
              <div class='row'>
                <div class='col-md-6'>
                  <div class='card mb-4'>
                    <div class='card-header bg-primary text-white'>
                      <i class='bi bi-plus-circle'></i> Administración de Bits
                    </div>
                    <div class='card-body'>
                      <form method='post'>
                        <div class='mb-3'>
                          <label class='form-label'>Nombre del bit:</label>
                          <input type='text' class='form-control' name='bit_name' required>
                        </div>
                        <button type='submit' class='btn btn-primary'><i class='bi bi-plus-circle'></i> Crear bit</button>
                      </form>
                      
                      <hr>
                      
                      <form method='post'>
                        <div class='mb-3'>
                          <label class='form-label'>Bit a eliminar:</label>
                          <select class='form-select' name='delete_bit'>
                            <option value=''>Selecciona un bit</option>""" +
                            ''.join(f"<option value='{bit}'>{bit}</option>" for bit in qubits.keys()) +
                            """
                          </select>
                        </div>
                        <input type='hidden' name='action' value='delete'>
                        <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i> Eliminar bit</button>
                      </form>
                      
                      <hr>
                      
                      <form method='post'>
                        <input type='hidden' name='action' value='reset_all'>
                        <button type='submit' class='btn btn-warning'><i class='bi bi-arrow-counterclockwise'></i> Resetear todo</button>
                      </form>
                    </div>
                  </div>
                </div>
                
                <div class='col-md-6'>
                  <div class='card'>
                    <div class='card-header bg-success text-white'>
                      <i class='bi bi-code-square'></i> Operaciones Lógicas
                    </div>
                    <div class='card-body'>
                      <form method='post'>
                        <div class='mb-3'>
                          <label class='form-label'>Bit 1:</label>
                          <select class='form-select' name='bit1'>
                            <option value=''>Selecciona bit 1</option>""" +
                            ''.join(f"<option value='{bit}'>{bit}</option>" for bit in qubits.keys()) +
                            """
                          </select>
                        </div>
                        
                        <div class='mb-3'>
                          <label class='form-label'>Bit 2:</label>
                          <select class='form-select' name='bit2'>
                            <option value=''>Selecciona bit 2</option>""" +
                            ''.join(f"<option value='{bit}'>{bit}</option>" for bit in qubits.keys()) +
                            """
                          </select>
                        </div>
                        
                        <div class='mb-3'>
                          <label class='form-label'>Operación:</label>
                          <select class='form-select' name='operation'>
                            <option value='and'>AND</option>
                            <option value='or'>OR</option>
                            <option value='xor'>XOR</option>
                            <option value='nand'>NAND</option>
                            <option value='nor'>NOR</option>
                          </select>
                        </div>
                        
                        <input type='hidden' name='action' value='operate'>
                        <button type='submit' class='btn btn-success'><i class='bi bi-play-fill'></i> Ejecutar Operación</button>
                      </form>
                      
                      <div class='mt-4'>
                        <h5><i class='bi bi-info-circle'></i> Ayuda</h5>
                        <ul class='list-group'>
                          <li class='list-group-item'><b>AND:</b> Resultado 1 solo si ambos bits son 1</li>
                          <li class='list-group-item'><b>OR:</b> Resultado 1 si al menos un bit es 1</li>
                          <li class='list-group-item'><b>XOR:</b> Resultado 1 si los bits son diferentes</li>
                          <li class='list-group-item'><b>NAND:</b> Negación de AND</li>
                          <li class='list-group-item'><b>NOR:</b> Negación de OR</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/qubits', methods=['GET', 'POST'])
def qubits_panel():
    msg = ''
    if request.method == 'POST':
        # Crear qubit
        name = request.form.get('qubit_name', '').strip()
        # Eliminar qubit
        delete_name = request.form.get('delete_qubit', '').strip()
        action = request.form.get('action', '')
        if name and not action:
            if name in qubits:
                msg = f"<span style='color:red'>El qubit '{name}' ya existe.</span>"
            else:
                interpret(f"QUBIT {name}")
                msg = f"<span style='color:green'>Qubit '{name}' creado.</span>"
        elif action == 'delete' and delete_name:
            if delete_name in qubits:
                interpret(f"DELETE {delete_name}")
                msg = f"<span style='color:green'>Qubit '{delete_name}' eliminado.</span>"
            else:
                msg = f"<span style='color:red'>El qubit '{delete_name}' no existe.</span>"
        elif action == 'delete' and not delete_name:
            msg = "<span style='color:red'>Selecciona un qubit para eliminar.</span>"
        elif action == 'reset_all':
            interpret("RESETALL")
            msg = "<span style='color:green'>Todos los qubits han sido reseteados.</span>"
        elif not name and not action:
            msg = "<span style='color:red'>Debes ingresar un nombre.</span>"
    qubit_list = list(qubits.keys())
    # Opciones de puertas cuánticas básicas
    gates = ['H', 'X', 'Y', 'Z']
    gate_form = f"""
    <form method='post' style='margin-top:20px;'>
        <label>Aplicar puerta a qubit:</label>
        <select name='target_qubit'>
            <option value=''>--Qubit--</option>
            {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
        </select>
        <select name='gate'>
            <option value=''>--Puerta--</option>
            {''.join(f'<option value="{g}">{g}</option>' for g in gates)}
        </select>
        <button type='submit' name='action' value='apply_gate'>Aplicar</button>
    </form>
    """
    # Botón para resetear todos los qubits
    reset_all_form = """
    <form method='post' style='margin-top:10px;display:inline;'>
        <button type='submit' name='action' value='reset_all' style='background:#f55;color:white;'>Resetear todos los qubits</button>
    </form>
    """

    if request.method == 'POST':
        # Aplicar puerta cuántica
        if action == 'apply_gate':
            target = request.form.get('target_qubit', '').strip()
            gate = request.form.get('gate', '').strip()
            if not target or not gate:
                msg = "<span style='color:red'>Selecciona un qubit y una puerta.</span>"
            elif target not in qubits:
                msg = f"<span style='color:red'>El qubit '{target}' no existe.</span>"
            else:
                interpret(f"GATE {gate} {target}")
                msg = f"<span style='color:green'>Puerta {gate} aplicada a {target}.</span>"
    qubit_list = list(qubits.keys())
    # Visualización: Esfera de Bloch para un qubit seleccionado
    bloch_form = f"""
    <form method='get' action='/bloch' style='margin-top:20px;'>
        <label>Visualizar esfera de Bloch de:</label>
        <select name='qubit'>
            <option value=''>--Qubit--</option>
            {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
        </select>
        <button type='submit'>Ver Esfera de Bloch</button>
    </form>
    """
    # Visualización: Probabilidades y amplitudes del qubit seleccionado
    prob_amp_form = f"""
    <form method='get' action='/qubit_info' style='margin-top:20px;'>
        <label>Ver info de qubit:</label>
        <select name='qubit'>
            <option value=''>--Qubit--</option>
            {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
        </select>
        <button type='submit'>Ver Estado</button>
    </form>
    """
    # Visualización: Métricas extra del qubit seleccionado
    metrics_form = f"""
    <form method='get' action='/qubit_metrics' style='margin-top:20px;'>
        <label>Ver métricas avanzadas de qubit:</label>
        <select name='qubit'>
            <option value=''>--Qubit--</option>
            {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
        </select>
        <button type='submit'>Ver Métricas</button>
    </form>
    """
    alert = ''
    if msg:
        if 'color:green' in msg:
            alert = f"<div class='alert alert-success alert-dismissible fade show' role='alert'>{msg}<button type='button' class='btn-close' data-bs-dismiss='alert'></button></div>"
        else:
            alert = f"<div class='alert alert-danger alert-dismissible fade show' role='alert'>{msg}<button type='button' class='btn-close' data-bs-dismiss='alert'></button></div>"
    qubit_table = ''
    if qubit_list:
        qubit_table = "<table class='table table-striped table-bordered'><thead><tr><th>Qubit</th></tr></thead><tbody>" + ''.join(f"<tr><td>{q}</td></tr>" for q in qubit_list) + "</tbody></table>"
    else:
        qubit_table = '<i>No hay qubits activos.</i>'
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='qubits') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-6'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-gear'></i> Panel de Qubits</h2>
              <form method='post' class='mb-3' autocomplete='off'>
                <label class='form-label'>Nombre del qubit: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Elige un nombre único para tu qubit. Puedes usar letras, números y guiones bajos. Ejemplo: q0, qubit1, ancilla.' tabindex='0' aria-label='Ayuda sobre nombre de qubit'></i></label>
                <input type='text' name='qubit_name' class='form-control mb-2' required aria-label='Nombre del qubit'>
                <button type='submit' class='btn btn-primary'><i class='bi bi-plus-circle'></i> Crear Qubit</button>
              </form>
              {alert}
              <h5>Qubits activos:</h5>
              <div>{qubit_table}</div>
              <form method='post' class='mb-2'>
                <label class='form-label'>Eliminar qubit: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Selecciona un qubit para eliminarlo. Esta acción es irreversible.' tabindex='0' aria-label='Ayuda sobre eliminar qubit'></i></label>
                <select name='delete_qubit' class='form-select mb-2' aria-label='Seleccionar qubit a eliminar'>
                  <option value=''>--Selecciona--</option>
                  {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
                </select>
                <button type='submit' name='action' value='delete' class='btn btn-danger'><i class='bi bi-trash'></i> Eliminar</button>
              </form>
              {reset_all_form}
            </div>
          </div>
        </div>
        <div class='col-md-6'>
          <div class='card shadow'>
            <div class='card-body'>
              <h5>Operaciones y Visualización <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Aquí puedes aplicar puertas, ver la esfera de Bloch, amplitudes, probabilidades y métricas avanzadas.' tabindex='0' aria-label='Ayuda sobre operaciones y visualización'></i></h5>
              <div id='qubit-feedback' aria-live='polite'>{gate_form}</div>
              {bloch_form}
              {prob_amp_form}
              {metrics_form}
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
    // Microinteracción: loading spinner al crear/eliminar qubit
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function(e) {{
        if (form.querySelector('input[name="qubit_name"]') || form.querySelector('select[name="delete_qubit"]')) {{
          var feedback = document.getElementById('qubit-feedback');
          if (feedback) {{
            feedback.innerHTML = '<div style="text-align:center;"><div class="spinner-border text-primary" role="status" aria-label="Procesando..."></div><div class="mt-2">Procesando...</div></div>';
          }}
        }}
      }});
    }});
    // Accesibilidad: enfocar feedback tras acción
    window.addEventListener('DOMContentLoaded', function() {{
      var feedback = document.getElementById('qubit-feedback');
      if (feedback && feedback.textContent.trim().length > 0) {{
        if (feedback.focus) feedback.focus();
      }}
    }});
    </script>
    """ + TOOLTIP_SCRIPT + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/circuit', methods=['GET', 'POST'])
def circuit_panel():
    from visualizer.circuit_visualizer import plot_circuit
    import io
    import base64
    import matplotlib.pyplot as plt
    from interpreter.qlang_interpreter import circuit_operations, qubits, interpret
    msg = ''
    zoom = float(request.form.get('zoom', 1.0)) if request.method == 'POST' else 1.0
    style = request.form.get('style', 'modern') if request.method == 'POST' else 'modern'
    export_type = request.form.get('export_type', '') if request.method == 'POST' else ''
    export_data = ''
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'add_gate':
            gate = request.form.get('gate', '').strip()
            target = request.form.get('target_qubit', '').strip()
            if not gate or not target:
                msg = "<span style='color:red'>Selecciona un qubit y una puerta.</span>"
            elif target not in qubits:
                msg = f"<span style='color:red'>El qubit '{target}' no existe.</span>"
            else:
                interpret(f"GATE {gate} {target}")
                msg = f"<span style='color:green'>Puerta {gate} agregada a {target}.</span>"
        elif action == 'reset_circuit':
            interpret("RESETCIRCUIT")
            msg = "<span style='color:green'>Circuito reseteado.</span>"
        elif action.startswith('delete_op_'):
            idx = int(action.replace('delete_op_', ''))
            interpret(f"DELETEOP {idx}")
            msg = f"<span style='color:green'>Operación {idx+1} eliminada.</span>"
        elif action == 'export_img':
            if circuit_operations:
                fig = plot_circuit(circuit_operations, zoom=zoom, style=style)
                buf = io.BytesIO()
                plt.tight_layout()
                fig.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                export_data = img_b64
                export_type = 'img'
        elif action == 'export_qasm':
            try:
                from gates.quantum_gates import get_circuit_qasm
                qasm = get_circuit_qasm(circuit_operations)
                export_data = base64.b64encode(qasm.encode('utf-8')).decode('utf-8')
                export_type = 'qasm'
            except Exception as e:
                msg = f"<span style='color:red'>Error al exportar QASM: {e}</span>"
        elif action == 'export_qiskit':
            try:
                from gates.quantum_gates import get_circuit_qiskit
                code = get_circuit_qiskit(circuit_operations)
                export_data = base64.b64encode(code.encode('utf-8')).decode('utf-8')
                export_type = 'qiskit'
            except Exception as e:
                msg = f"<span style='color:red'>Error al exportar Qiskit: {e}</span>"
    img_html = "<i>No hay operaciones en el circuito.</i>"
    if circuit_operations:
        fig = plot_circuit(circuit_operations, zoom=zoom, style=style)
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        img_html = f"<img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;' title='Visualización del circuito'>"
    qubit_list = list(qubits.keys())
    gates = ['H', 'X', 'Y', 'Z', 'CX', 'CZ']
    add_gate_form = f"""
    <form method='post' style='margin-top:20px;'>
        <label>Agregar puerta:</label>
        <select name='gate'>
            <option value=''>--Puerta--</option>
            {''.join(f'<option value="{g}">{g}</option>' for g in gates)}
        </select>
        <select name='target_qubit'>
            <option value=''>--Qubit--</option>
            {''.join(f'<option value="{q}">{q}</option>' for q in qubit_list)}
        </select>
        <button type='submit' name='action' value='add_gate'>Agregar</button>
    </form>
    """
    reset_form = """
    <form method='post' style='margin-top:10px;display:inline;'>
        <button type='submit' name='action' value='reset_circuit' style='background:#f55;color:white;'>Resetear Circuito</button>
    </form>
    """
    ops_html = "<i>No hay operaciones en el circuito.</i>"
    if circuit_operations:
        ops_html = "<ul>" + ''.join(
            f"<li>{op} <form method='post' style='display:inline;'><button type='submit' name='action' value='delete_op_{i}' style='color:#f55;background:none;border:none;cursor:pointer;' title='Eliminar operación'>&#10060;</button></form></li>"
            for i, op in enumerate(circuit_operations)
        ) + "</ul>"
    controls_form = f"""
    <form method='post' class='row g-2 mb-3' style='align-items:center;'>
      <div class='col-auto'>
        <label class='form-label'>Zoom:</label>
        <input type='range' min='0.5' max='2.0' step='0.1' name='zoom' value='{zoom}' style='width:120px;'>
        <span class='badge bg-secondary'>{zoom}x</span>
      </div>
      <div class='col-auto'>
        <label class='form-label'>Estilo:</label>
        <select name='style' class='form-select'>
          <option value='modern' {'selected' if style=='modern' else ''}>Moderno</option>
          <option value='classic' {'selected' if style=='classic' else ''}>Clásico</option>
        </select>
      </div>
      <div class='col-auto'>
        <button type='submit' class='btn btn-outline-primary'>Actualizar Vista</button>
      </div>
      <div class='col-auto'>
        <button type='submit' name='action' value='export_img' class='btn btn-outline-success'><i class='bi bi-image'></i> Exportar PNG</button>
      </div>
      <div class='col-auto'>
        <button type='submit' name='action' value='export_qasm' class='btn btn-outline-secondary'><i class='bi bi-file-earmark-code'></i> Exportar QASM</button>
      </div>
      <div class='col-auto'>
        <button type='submit' name='action' value='export_qiskit' class='btn btn-outline-dark'><i class='bi bi-filetype-py'></i> Exportar Qiskit</button>
      </div>
      <div class='col-auto'>
        <span data-bs-toggle='tooltip' title='Puedes exportar el circuito como imagen, QASM o código Qiskit para usarlo en otros simuladores.'><i class='bi bi-question-circle'></i></span>
      </div>
    </form>
    """
    export_html = ''
    if export_type == 'img' and export_data:
        export_html = f"""
        <form method='post' action='/download_img' style='margin-top:10px;'>
            <input type='hidden' name='img_data' value='{export_data}'>
            <input type='hidden' name='img_name' value='circuito.png'>
            <button type='submit' class='btn btn-success'><i class='bi bi-download'></i> Descargar imagen PNG</button>
        </form>
        """
    elif export_type == 'qasm' and export_data:
        export_html = f"""
        <form method='post' action='/download_qasm' style='margin-top:10px;'>
            <input type='hidden' name='qasm_data' value='{export_data}'>
            <button type='submit' class='btn btn-secondary'><i class='bi bi-download'></i> Descargar QASM</button>
        </form>
        """
    elif export_type == 'qiskit' and export_data:
        export_html = f"""
        <form method='post' action='/download_qiskit' style='margin-top:10px;'>
            <input type='hidden' name='qiskit_data' value='{export_data}'>
            <button type='submit' class='btn btn-dark'><i class='bi bi-download'></i> Descargar Qiskit</button>
        </form>
        """
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='circuit') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-10 offset-md-1'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-diagram-3'></i> Panel de Circuito Cuántico</h2>
              <p>Construye y visualiza tu circuito cuántico aquí. Usa los controles para personalizar la visualización y exportar tu circuito.</p>
              <div class='feedback' id='circuit-feedback' aria-live='polite'>{msg}</div>
              {add_gate_form}
              {reset_form}
              <h5>Operaciones actuales: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Lista de puertas aplicadas al circuito. Puedes deshacer o reiniciar.' tabindex='0' aria-label='Ayuda sobre operaciones actuales'></i></h5>
              <div class='table-responsive'>{ops_html}</div>
              <h5>Controles de visualización y exportación: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Ajusta el zoom, cambia el estilo visual o exporta tu circuito en varios formatos.' tabindex='0' aria-label='Ayuda sobre controles de visualización'></i></h5>
              {controls_form}
              <h5>Visualización del circuito:</h5>
              <div id='circuit-img-area'>{img_html}</div>
              {export_html}
              <div class='mt-3'>
                <span class='badge bg-info'>Tip:</span> <span>Haz zoom, cambia el estilo o exporta tu circuito para usarlo en otros simuladores.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
    // Microinteracción: loading spinner al actualizar vista o exportar
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function(e) {{
        if (
          form.querySelector('input[name="zoom"]') ||
          form.querySelector('select[name="style"]') ||
          form.querySelector('button[name="action"][value="export_img"]') ||
          form.querySelector('button[name="action"][value="export_qasm"]') ||
          form.querySelector('button[name="action"][value="export_qiskit"]')
        ) {{
          var feedback = document.getElementById('circuit-feedback');
          if (feedback) {{
            feedback.innerHTML = '<div style="text-align:center;"><div class="spinner-border text-primary" role="status" aria-label="Procesando..."></div><div class="mt-2">Procesando...</div></div>';
          }}
          var imgArea = document.getElementById('circuit-img-area');
          if (imgArea) {{
            imgArea.innerHTML = '<div style="text-align:center;"><div class="spinner-border text-info" role="status" aria-label="Cargando visualización..." style="width:3rem;height:3rem;"></div><div class="mt-2">Cargando visualización...</div></div>';
          }}
        }}
      }});
    }});
    // Accesibilidad: enfocar feedback tras acción
    window.addEventListener('DOMContentLoaded', function() {{
      var feedback = document.getElementById('circuit-feedback');
      if (feedback && feedback.textContent.trim().length > 0) {{
        if (feedback.focus) feedback.focus();
      }}
    }});
    </script>
    """ + TOOLTIP_SCRIPT + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/download_qasm', methods=['POST'])
def download_qasm():
    from flask import Response
    import base64
    qasm_data = request.form.get('qasm_data', '')
    qasm_bytes = base64.b64decode(qasm_data)
    return Response(qasm_bytes, mimetype='text/plain', headers={'Content-Disposition': 'attachment;filename=circuito.qasm'})

@app.route('/download_qiskit', methods=['POST'])
def download_qiskit():
    from flask import Response
    import base64
    qiskit_data = request.form.get('qiskit_data', '')
    qiskit_bytes = base64.b64decode(qiskit_data)
    return Response(qiskit_bytes, mimetype='text/x-python', headers={'Content-Disposition': 'attachment;filename=circuito_qiskit.py'})

@app.route('/visualization', methods=['GET', 'POST'])
def visualization_panel():
    from interpreter.qlang_interpreter import qubits
    import numpy as np
    import matplotlib.pyplot as plt
    import io
    import base64
    qubit_names = list(qubits.keys())
    html = ""
    selected = request.form.get('highlight_qubit', '') if request.method == 'POST' else ''
    img_b64 = ''
    img_b64_2 = ''
    if len(qubit_names) >= 2:
        # Matriz de densidad global
        states = [qubits[q].state for q in qubit_names]
        state = states[0]
        for s in states[1:]:
            state = np.kron(state, s)
        rho = np.outer(state, state.conj())
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(np.real(rho), cmap='RdYlBu')
        fig.colorbar(im)
        ax.set_title('Matriz de Densidad Global (parte real)')
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        # Métricas globales
        coherence = np.sum(np.abs(rho - np.diag(np.diag(rho))))
        purity = np.trace(rho @ rho).real
        eigs = np.linalg.eigvalsh(rho)
        entropy = -sum(e*np.log2(e) for e in eigs if e > 1e-10)
        html += "<h3>Matriz de Densidad Global</h3>"
        html += f"<img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;'><br>"
        html += f"<form method='post' action='/download_img' style='display:inline;'><input type='hidden' name='img_data' value='{img_b64}'><input type='hidden' name='img_name' value='matriz_densidad.png'><button type='submit' class='btn btn-primary'>Descargar imagen</button></form>"
        html += f"<br><b>Coherencia global l1:</b> {coherence:.6f}<br>"
        html += f"<b>Pureza global:</b> {purity:.6f}<br>"
        html += f"<b>Entropía von Neumann global:</b> {entropy:.6f}<br>"
        # Mapa de fidelidad
        n = len(qubit_names)
        fidelity_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                state1 = qubits[qubit_names[i]].state
                state2 = qubits[qubit_names[j]].state
                fidelity_matrix[i, j] = abs(np.vdot(state1, state2)) ** 2
        highlight_idx = qubit_names.index(selected) if selected in qubit_names else None
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        im2 = ax2.imshow(fidelity_matrix, cmap='viridis', vmin=0, vmax=1)
        fig2.colorbar(im2)
        ax2.set_xticks(np.arange(n))
        ax2.set_yticks(np.arange(n))
        ax2.set_xticklabels(qubit_names)
        ax2.set_yticklabels(qubit_names)
        ax2.set_title('Mapa de Fidelidad entre Qubits')
        for i in range(n):
            for j in range(n):
                color = 'yellow' if (highlight_idx is not None and (i == highlight_idx or j == highlight_idx)) else 'w'
                ax2.text(j, i, f"{fidelity_matrix[i, j]:.2f}", ha='center', va='center', color=color, fontsize=8, fontweight='bold' if color=='yellow' else 'normal')
        buf2 = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf2, format='png')
        plt.close(fig2)
        img_b64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
        html += f"""
        <h3>Mapa de Fidelidad</h3>
        <form method='post' style='margin-bottom:10px;'>
            <label>Resaltar qubit:</label>
            <select name='highlight_qubit'>
                <option value=''>--Qubit--</option>
                {''.join(
                    f'<option value="{q}"{" selected" if q==selected else ""}>{q}</option>'
                    for q in qubit_names
                )}
            </select>
            <button type='submit' class='btn btn-primary'>Resaltar</button>
        </form>
        <img src='data:image/png;base64,{img_b64_2}' style='max-width:100%;height:auto;border:1px solid #888;' title='Mapa de fidelidad'>
        <form method='post' action='/download_img' style='display:inline;'><input type='hidden' name='img_data' value='{img_b64_2}'><input type='hidden' name='img_name' value='mapa_fidelidad.png'><button type='submit' class='btn btn-primary'>Descargar imagen</button></form>
        <br>
        <b>Tabla de fidelidad:</b>
        <table class='table table-bordered' style='border-collapse:collapse;'>
            <tr><th></th>{''.join(f'<th>{q}</th>' for q in qubit_names)}</tr>
            {''.join('<tr><th>'+qubit_names[i]+'</th>' + ''.join(f'<td title="F({qubit_names[i]},{qubit_names[j]})={fidelity_matrix[i,j]:.4f}">{fidelity_matrix[i,j]:.2f}</td>' for j in range(n)) + '</tr>' for i in range(n))}
        </table>
        """
        # Entrelazamiento simple: contar pares de qubits entrelazados
        entangled_pairs = set()
        for q in qubit_names:
            ent_set = getattr(qubits[q], 'entangled_with', set())
            for other in ent_set:
                pair = tuple(sorted([q, other]))
                entangled_pairs.add(pair)
        html += f"<b>Pares de qubits entrelazados:</b> {len(entangled_pairs)}<br>"
        html += f"<b>Total de qubits:</b> {len(qubit_names)}<br>"
    else:
        html = "<i>Se requieren al menos dos qubits para visualización global.</i>"
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='visualization') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-10 offset-md-1'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-bar-chart'></i> Panel de Visualización</h2>
              <p>Visualiza el estado cuántico (esfera de Bloch, matriz de densidad global, coherencia, etc.).</p>
              <div id='visualization-feedback' aria-live='polite'></div>
              {html}
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
    // Microinteracción: loading spinner al resaltar qubit o descargar imagen
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function(e) {{
        if (
          form.querySelector('select[name="highlight_qubit"]') ||
          form.querySelector('button[type="submit"][class*="btn-primary"]')
        ) {{
          var feedback = document.getElementById('visualization-feedback');
          if (feedback) {{
            feedback.innerHTML = '<div style="text-align:center;"><div class="spinner-border text-primary" role="status" aria-label="Procesando..."></div><div class="mt-2">Procesando...</div></div>';
          }}
        }}
      }});
    }});
    // Accesibilidad: enfocar feedback tras acción
    window.addEventListener('DOMContentLoaded', function() {{
      var feedback = document.getElementById('visualization-feedback');
      if (feedback && feedback.textContent.trim().length > 0) {{
        if (feedback.focus) feedback.focus();
      }}
    }});
    </script>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/simulate', methods=['GET', 'POST'])
def simulate_panel():
    logging.info("Accediendo al panel de simulación")
    msg = ''
    result_html = ''
    try:
        if request.method == 'POST':
            action = request.form.get('action', '')
            if action == 'simulate':
                logging.info("Iniciando simulación del circuito")
                try:
                    # Validar estado del circuito
                    if not circuit_operations:
                        msg = "<div class='alert alert-warning'>No hay operaciones en el circuito para simular.</div>"
                    else:
                        # Ejecutar simulación
                        results = simulate_circuit(circuit_operations)
                        # Generar visualizaciones
                        result_html = generate_result_visualizations(results)
                        msg = "<div class='alert alert-success'>Simulación completada exitosamente.</div>"
                        logging.info("Simulación completada con éxito")
                except NameError as ne:
                    msg = f"<div class='alert alert-danger'>Error: {str(ne)}</div>"
                    logging.error(f"NameError en simulación: {ne}")
                except Exception as e:
                    msg = f"<div class='alert alert-danger'>Error durante la simulación: {str(e)}</div>"
                    logging.error(f"Error en simulación: {e}")
    except Exception as e:
        msg = f"<div class='alert alert-danger'>Error inesperado: {str(e)}</div>"
        logging.error(f"Error inesperado en simulate_panel: {e}")

    return render_template_string(
        BOOTSTRAP_HEAD + 
        build_navbar(active='simulate') +
        f"""
        <div class='container fade-in'>
            <div class='card shadow'>
                <div class='card-body'>
                    <h2><i class='bi bi-play-circle'></i> Simulación</h2>
                    <div id='simulation-feedback' aria-live='polite'>{msg}</div>
                    <form method='post' class='mb-4'>
                        <button type='submit' name='action' value='simulate' class='btn btn-primary'>
                            <i class='bi bi-play-fill'></i> Ejecutar Simulación
                        </button>
                    </form>
                    {result_html}
                </div>
            </div>
        </div>
        """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/dbtest', methods=['POST'])
def test_db_connection():
    logger.info("Probando conexión a PostgreSQL")
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            msg = "<div class='alert alert-warning'>Variable de entorno DATABASE_URL no configurada. Usando configuración local.</div>"
            logger.warning("DATABASE_URL no configurada")
            DATABASE_URL = "postgresql://localhost:5432/quantum_sim"
        
        # Manejar URL de Render que comienza con postgres:// en lugar de postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            logger.info("URL de base de datos convertida de postgres:// a postgresql://")
        
        # Intentar conexión con reintentos
        max_retries = 3
        retry_delay = 2  # segundos
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento de conexión {attempt+1}/{max_retries}")
                conn = psycopg2.connect(
                    DATABASE_URL,
                    connect_timeout=10  # Timeout de conexión en segundos
                )
                conn.close()
                msg = "<div class='alert alert-success'>Conexión a PostgreSQL exitosa ✓</div>"
                logger.info("Prueba de conexión PostgreSQL exitosa")
                break
            except psycopg2.OperationalError as e:
                last_error = e
                logger.warning(f"Intento {attempt+1} fallido: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Esperando {retry_delay} segundos antes del siguiente intento...")
                    time.sleep(retry_delay)
        else:  # Se ejecuta si el bucle termina normalmente (sin break)
            msg = f"<div class='alert alert-danger'>Error de conexión después de {max_retries} intentos: {str(last_error)}</div>"
            logger.error(f"Error en prueba PostgreSQL después de {max_retries} intentos: {last_error}")
            
            # Información de diagnóstico adicional
            try:
                import socket
                host = DATABASE_URL.split('@')[1].split('/')[0].split(':')[0] if '@' in DATABASE_URL else 'unknown'
                port = int(DATABASE_URL.split('@')[1].split('/')[0].split(':')[1]) if '@' in DATABASE_URL and ':' in DATABASE_URL.split('@')[1].split('/')[0] else 5432
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                result = s.connect_ex((host, port))
                s.close()
                
                if result == 0:
                    msg += "<div class='alert alert-info'>El puerto está abierto, pero hay un problema con las credenciales o la configuración de la base de datos.</div>"
                else:
                    msg += "<div class='alert alert-warning'>El puerto está cerrado o bloqueado. Verifica que la base de datos esté en ejecución y accesible desde este servicio.</div>"
                
                logger.info(f"Diagnóstico de red: host={host}, port={port}, resultado={result}")
            except Exception as net_error:
                logger.warning(f"No se pudo realizar diagnóstico de red: {net_error}")
    except ImportError:
        msg = "<div class='alert alert-warning'>Módulo psycopg2 no instalado. Instálalo con: pip install psycopg2-binary</div>"
        logger.warning("psycopg2 no instalado")
    except Exception as e:
        msg = f"<div class='alert alert-danger'>Error inesperado: {str(e)}</div>"
        logger.error(f"Error inesperado en prueba PostgreSQL: {e}")
    
    # Información de entorno
    env_info = "<h4>Información de entorno:</h4><ul>"
    env_info += f"<li>PYTHON_VERSION: {sys.version}</li>"
    env_info += f"<li>DATABASE_URL configurada: {'Sí' if os.getenv('DATABASE_URL') else 'No'}</li>"
    env_info += f"<li>Entorno: {os.getenv('FLASK_ENV', 'no configurado')}</li>"
    env_info += "</ul>"
    
    return render_template_string(BOOTSTRAP_HEAD + build_navbar() + f"""
        <div class='container fade-in'>
            <div class='card shadow'>
                <div class='card-body'>
                    <h3><i class='bi bi-database'></i> Diagnóstico de Base de Datos</h3>
                    {msg}
                    {env_info}
                    <div class='mt-3'>
                        <a href='/' class='btn btn-primary'>Volver</a>
                    </div>
                </div>
            </div>
        </div>
    """ + FOOTER)

@app.route('/api/health')
def health_check():
    """
    Endpoint de diagnóstico para verificar el estado del servicio
    
    Returns:
        JSON con estado general y detalles de dependencias
    """
    logger.info("Verificando estado del servicio")
    
    # Verificar dependencias críticas con más detalle
    dependencies = {
        'matplotlib': {
            'status': 'ok',
            'version': 'unknown'
        },
        'numpy': {
            'status': 'ok',
            'version': 'unknown'
        },
        'flask': {
            'status': 'ok',
            'version': 'unknown'
        },
        'interpreter': {
            'status': 'ok',
            'version': 'unknown'
        },
        'database': {
            'status': 'unknown',
            'connection_string': 'hidden'
        }
    }
    
    # Verificar conexión a la base de datos con más detalle
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if DATABASE_URL:
            # Ocultar credenciales en el log
            safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
            dependencies['database']['connection_string'] = safe_url
            
            # Convertir URL si es necesario
            if DATABASE_URL.startswith('postgres://'):
                DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            
            # Intentar conexión con timeout corto
            try:
                conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
                dependencies['database'].update({
                    'status': 'ok',
                    'server_version': conn.server_version,
                    'transaction_status': conn.get_transaction_status()
                })
                conn.close()
            except psycopg2.OperationalError as db_error:
                dependencies['database'].update({
                    'status': f'error: {type(db_error).__name__}',
                    'error_details': str(db_error)
                })
                logger.warning(f"Error operacional en health check: {type(db_error).__name__} - {db_error}")
            except psycopg2.ProgrammingError as db_error:
                dependencies['database'].update({
                    'status': f'error: {type(db_error).__name__}',
                    'error_details': str(db_error)
                })
                logger.warning(f"Error de programación en health check: {type(db_error).__name__} - {db_error}")
            except Exception as db_error:
                dependencies['database'].update({
                    'status': f'error: {type(db_error).__name__}',
                    'error_details': str(db_error)
                })
                logger.error(f"Error inesperado en health check: {type(db_error).__name__} - {db_error}", exc_info=True)
        else:
            dependencies['database'].update({
                'status': 'not_configured',
                'error_details': 'DATABASE_URL no configurada'
            })
    except ImportError:
        dependencies['database'] = 'driver_missing'
    
    # Verificar otras dependencias
    try:
        import matplotlib
        import numpy
        from interpreter.qlang_interpreter import qubits
    except ImportError as e:
        dependencies['interpreter'] = f'error: {str(e)}'
        logger.error(f"Error en health check: {e}")
    
    # Determinar estado general
    has_errors = any('error' in str(value) for value in dependencies.values())
    overall_status = 'degraded' if has_errors else 'healthy'
    
    status = {
        'status': overall_status,
        'timestamp': datetime.datetime.now().isoformat(),
        'dependencies': dependencies,
        'environment': os.getenv('FLASK_ENV', 'production')
    }
    
    # Responder con código 200 incluso si hay problemas, para que Render no reinicie el servicio
    return jsonify(status)

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
    import matplotlib.pyplot as plt
    import numpy as np
    import io
    import base64
    
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
        
        # Convertir gráfico a imagen base64
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        html_output += f"<h3>Probabilidades de Estados</h3>"
        html_output += f"<img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;'>"
        html_output += f"<form method='post' action='/download_img' style='display:inline;margin-top:10px;'>"
        html_output += f"<input type='hidden' name='img_data' value='{img_b64}'>"
        html_output += f"<input type='hidden' name='img_name' value='probabilidades.png'>"
        html_output += f"<button type='submit' class='btn btn-primary'><i class='bi bi-download'></i> Descargar gráfico</button>"
        html_output += f"</form>"
    
    html_output += "</div>"
    return html_output

# Inicializar variables necesarias
try:
    from interpreter.qlang_interpreter import circuit_operations
except ImportError:
    circuit_operations = []

# Añadir ruta para descargar imágenes
@app.route('/download_img', methods=['POST'])
def download_img():
    img_data = request.form.get('img_data', '')
    img_name = request.form.get('img_name', 'imagen.png')
    img_bytes = base64.b64decode(img_data)
    return Response(img_bytes, mimetype='image/png', headers={'Content-Disposition': f'attachment;filename={img_name}'})

if __name__ == '__main__':
    # Configuración para entorno de desarrollo y producción
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # En producción, asegurarse de que debug esté desactivado
    if os.environ.get('RENDER') or os.environ.get('PRODUCTION'):
        debug_mode = False
    
    logging.info(f"Iniciando servidor en puerto {port} (debug: {debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)