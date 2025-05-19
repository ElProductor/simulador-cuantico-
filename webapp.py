from flask import Flask, render_template_string, request, jsonify
import os
from interpreter.qlang_interpreter import qubits, interpret

app = Flask(__name__)

def build_navbar(active=None):
    # Diccionario de rutas y nombres con íconos
    items = [
        ('qubits', 'Qubits', 'bi-cpu'),
        ('circuit', 'Circuito', 'bi-diagram-3'),
        ('visualization', 'Visualización', 'bi-bar-chart'),
        ('simulate', 'Simular', 'bi-play-circle'),
        ('algorithms', 'Algoritmos', 'bi-lightbulb'),
        ('metrics', 'Métricas', 'bi-graph-up'),
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
    msg = ''
    result_html = ''
    csv_data = ''
    hist_b64 = ''
    if request.method == 'POST':
        from interpreter.qlang_interpreter import run_circuit, qubits
        import matplotlib.pyplot as plt
        import io
        import base64
        import csv
        try:
            run_circuit()
            # Histograma de probabilidades de medición
            result_html = '<h3>Resultados de la simulación:</h3>'
            probs = []
            labels = []
            csv_rows = [['Qubit', 'Amplitud |0⟩', 'Amplitud |1⟩', 'P(|0⟩)', 'P(|1⟩)']]
            for name, q in qubits.items():
                state = q.state
                prob0 = abs(state[0])**2
                prob1 = abs(state[1])**2
                result_html += f"<b>{name}:</b> |ψ⟩ = ({state[0]:.4f})|0⟩ + ({state[1]:.4f})|1⟩<br>"
                result_html += f"P(|0⟩) = {prob0:.4f}, P(|1⟩) = {prob1:.4f}<br><br>"
                probs.append([prob0, prob1])
                labels.append(name)
                csv_rows.append([name, f"{state[0]:.6f}", f"{state[1]:.6f}", f"{prob0:.6f}", f"{prob1:.6f}"])
            # Graficar histograma
            if labels:
                fig, ax = plt.subplots(figsize=(6,4))
                import numpy as np
                x = np.arange(len(labels))
                width = 0.35
                prob0s = [p[0] for p in probs]
                prob1s = [p[1] for p in probs]
                ax.bar(x - width/2, prob0s, width, label='P(|0⟩)')
                ax.bar(x + width/2, prob1s, width, label='P(|1⟩)')
                ax.set_xticks(x)
                ax.set_xticklabels(labels)
                ax.set_ylabel('Probabilidad')
                ax.set_title('Probabilidades de medición por qubit')
                ax.legend()
                buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format='png')
                plt.close(fig)
                hist_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                result_html += f"<img src='data:image/png;base64,{hist_b64}' style='max-width:100%;height:auto;border:1px solid #888;'>"
            # Exportar CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_rows)
            csv_data = output.getvalue()
            output.close()
            msg = "<span style='color:green'>Simulación completada.</span>"
        except Exception as e:
            msg = f"<span style='color:red'>Error en la simulación: {e}</span>"
    download_form = """
    <form method='post' action='/download_csv' style='margin-top:10px;'>
        <input type='hidden' name='csv_data' id='csv_data'>
        <button type='submit' class='btn btn-primary'>Descargar resultados CSV</button>
    </form>
    <script>
    // Insertar el CSV en el campo oculto
    document.addEventListener('DOMContentLoaded', function() {
        var csv = `{csv_data}`;
        document.getElementById('csv_data').value = csv;
    });
    </script>
    """ if csv_data else ''
    download_hist_form = f"""
    <form method='post' action='/download_img' style='margin-top:10px;'>
        <input type='hidden' name='img_data' value='{hist_b64}'>
        <input type='hidden' name='img_name' value='histograma_simulacion.png'>
        <button type='submit' class='btn btn-primary'>Descargar histograma</button>
    </form>
    """ if hist_b64 else ''
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='simulate') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-play-circle'></i> Panel de Simulación</h2>
              <form method='post' class='mb-3'>
                <button type='submit' class='btn btn-success'><i class='bi bi-play'></i> Ejecutar Simulación</button>
              </form>
              <div class='feedback' id='simulate-feedback' aria-live='polite'>{msg}</div>
              {result_html}
              {download_form}
              {download_hist_form}
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
    // Microinteracción: loading spinner al simular
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function(e) {{
        if (form.querySelector('button[type="submit"][class*="btn-success"]')) {{
          var feedback = document.getElementById('simulate-feedback');
          if (feedback) {{
            feedback.innerHTML = '<div style="text-align:center;"><div class="spinner-border text-success" role="status" aria-label="Simulando..."></div><div class="mt-2">Simulando...</div></div>';
          }}
        }}
      }});
    }});
    // Accesibilidad: enfocar feedback tras acción
    window.addEventListener('DOMContentLoaded', function() {{
      var feedback = document.getElementById('simulate-feedback');
      if (feedback && feedback.textContent.trim().length > 0) {{
        if (feedback.focus) feedback.focus();
      }}
    }});
    </script>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/dbtest', methods=['POST'])
def dbtest():
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL", "postgres://usuario:contraseña@host:puerto/dbname")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f"<p>Conexión exitosa: {version}</p><a href='/'>Volver</a>"
    except Exception as e:
        return f"<p>Error de conexión: {e}</p><a href='/'>Volver</a>"

@app.route('/api/health')
def health():
    return jsonify(status="ok")

@app.route('/bloch')
def bloch_sphere():
    from matplotlib import pyplot as plt
    import io
    import base64
    import numpy as np
    qubit_name = request.args.get('qubit', '').strip()
    if not qubit_name or qubit_name not in qubits:
        return "<p>Qubit no válido. <a href='/qubits'>Volver</a></p>"
    # Obtener el estado del qubit
    state = qubits[qubit_name].state
    # Calcular coordenadas de Bloch
    x = 2 * np.real(state[0]*np.conj(state[1]))
    y = 2 * np.imag(state[0]*np.conj(state[1]))
    z = np.abs(state[0])**2 - np.abs(state[1])**2
    # Graficar esfera de Bloch
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, projection='3d')
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    ax.plot_surface(np.outer(np.cos(u), np.sin(v)),
                    np.outer(np.sin(u), np.sin(v)),
                    np.outer(np.ones(np.size(u)), np.cos(v)),
                    color='c', alpha=0.1)
    # Ejes
    ax.quiver(0,0,0,1,0,0,color='r',arrow_length_ratio=0.1)
    ax.quiver(0,0,0,0,1,0,color='g',arrow_length_ratio=0.1)
    ax.quiver(0,0,0,0,0,1,color='b',arrow_length_ratio=0.1)
    # Vector del qubit
    ax.quiver(0,0,0,x,y,z,color='purple',arrow_length_ratio=0.15,linewidth=2)
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1])
    ax.set_zlim([-1,1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Esfera de Bloch: {qubit_name}')
    ax.grid(False)
    # Imagen a base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"""
    <a href='/qubits'>← Volver</a><br>
    <h2>Esfera de Bloch de {qubit_name}</h2>
    <img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;'>
    <form method='post' action='/download_img' style='margin-top:10px;'>
        <input type='hidden' name='img_data' value='{img_b64}'>
        <input type='hidden' name='img_name' value='bloch_{qubit_name}.png'>
        <button type='submit' class='btn btn-primary'>Descargar imagen</button>
    </form>
    """

@app.route('/qubit_info')
def qubit_info():
    import numpy as np
    qubit_name = request.args.get('qubit', '').strip()
    if not qubit_name or qubit_name not in qubits:
        return "<p>Qubit no válido. <a href='/qubits'>Volver</a></p>"
    state = qubits[qubit_name].state
    amp0, amp1 = state[0], state[1]
    prob0, prob1 = np.abs(amp0)**2, np.abs(amp1)**2
    # CSV para descarga
    import base64
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Qubit', 'Amplitud |0⟩', 'Amplitud |1⟩', 'P(|0⟩)', 'P(|1⟩)'])
    writer.writerow([qubit_name, f"{amp0:.6f}", f"{amp1:.6f}", f"{prob0:.6f}", f"{prob1:.6f}"])
    csv_data = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')
    output.close()
    info = f"""
    <a href='/qubits'>← Volver</a><br>
    <h2>Estado de {qubit_name}</h2>
    <b>Amplitudes:</b><br>
    |ψ⟩ = ({amp0:.4f})|0⟩ + ({amp1:.4f})|1⟩<br>
    <b>Probabilidades:</b><br>
    P(|0⟩) = {prob0:.4f}<br>
    P(|1⟩) = {prob1:.4f}<br>
    <form method='post' action='/download_csv' style='margin-top:10px;'>
        <input type='hidden' name='csv_data' value='{csv_data}'>
        <input type='hidden' name='csv_name' value='estado_{qubit_name}.csv'>
        <button type='submit' class='btn btn-primary'>Descargar CSV</button>
    </form>
    """
    return info

@app.route('/qubit_metrics')
def qubit_metrics():
    import numpy as np
    qubit_name = request.args.get('qubit', '').strip()
    if not qubit_name or qubit_name not in qubits:
        return "<p>Qubit no válido. <a href='/qubits'>Volver</a></p>"
    state = qubits[qubit_name].state
    # Pureza
    rho = np.outer(state, state.conj())
    purity = np.trace(rho @ rho).real
    # Coherencia l1
    coherence = np.sum(np.abs(rho - np.diag(np.diag(rho))))
    # Coordenadas de Bloch
    x = 2 * np.real(state[0]*np.conj(state[1]))
    y = 2 * np.imag(state[0]*np.conj(state[1]))
    z = np.abs(state[0])**2 - np.abs(state[1])**2
    # Entropía de von Neumann
    eigs = np.linalg.eigvalsh(rho)
    entropy = -sum(e*np.log2(e) for e in eigs if e > 1e-10)
    # CSV para descarga
    import base64
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Qubit', 'Pureza', 'Coherencia l1', 'Entropía von Neumann', 'Bloch X', 'Bloch Y', 'Bloch Z'])
    writer.writerow([qubit_name, f"{purity:.6f}", f"{coherence:.6f}", f"{entropy:.6f}", f"{x:.4f}", f"{y:.4f}", f"{z:.4f}"])
    csv_data = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')
    output.close()
    info = f"""
    <a href='/qubits'>← Volver</a><br>
    <h2>Métricas avanzadas de {qubit_name}</h2>
    <div class='row g-3 mb-3'>
      <div class='col-md-4'>
        <div class='card border-success h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Pureza <span class='badge bg-success'>{purity:.4f}</span></h5>
            <p class='card-text'>Indica cuán puro es el estado del qubit (1 = puro).</p>
          </div>
        </div>
      </div>
      <div class='col-md-4'>
        <div class='card border-info h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Coherencia l1 <span class='badge bg-info text-dark'>{coherence:.4f}</span></h5>
            <p class='card-text'>Mide la superposición cuántica del qubit.</p>
          </div>
        </div>
      </div>
      <div class='col-md-4'>
        <div class='card border-warning h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Entropía von Neumann <span class='badge bg-warning text-dark'>{entropy:.4f}</span></h5>
            <p class='card-text'>Mide el desorden o mezcla del estado.</p>
          </div>
        </div>
      </div>
    </div>
    <div class='row g-3 mb-3'>
      <div class='col-md-12'>
        <div class='card border-primary'>
          <div class='card-body'>
            <h5 class='card-title'>Coordenadas de Bloch</h5>
            <span class='badge bg-primary'>X={x:.4f}</span>
            <span class='badge bg-primary'>Y={y:.4f}</span>
            <span class='badge bg-primary'>Z={z:.4f}</span>
            <p class='card-text mt-2'>Representan la posición del estado en la esfera de Bloch.</p>
          </div>
        </div>
      </div>
    </div>
    """
    # Exportar métricas CSV (solo del qubit actual)
    info += f"""
    <form method='post' action='/download_csv' style='margin-top:10px;'>
        <input type='hidden' name='csv_data' value='{csv_data}'>
        <input type='hidden' name='csv_name' value='metricas_{qubit_name}.csv'>
        <button type='submit' class='btn btn-primary'><i class='bi bi-download'></i> Descargar CSV</button>
    </form>
    """
    return info

@app.route('/references', methods=['GET'])
def references_panel():
    # Lista profesional de referencias y recursos
    references = [
        {"title": "Quantum Computation and Quantum Information",
         "authors": "M. Nielsen, I. Chuang",
         "type": "Libro",
         "desc": "El libro de referencia más citado en computación cuántica.",
         "year": 2010,
         "link": "https://www.cambridge.org/9781107002173"
        },
        {"title": "IBM Quantum Experience",
         "authors": "IBM Research",
         "type": "Web",
         "desc": "Plataforma online para experimentar con computadoras cuánticas reales.",
         "year": 2024,
         "link": "https://quantum-computing.ibm.com/"
        },
        {"title": "Qiskit: An Open-source Framework for Quantum Computing",
         "authors": "IBM Qiskit Team",
         "type": "Framework",
         "desc": "Framework Python para programación y simulación cuántica.",
         "year": 2024,
         "link": "https://qiskit.org/"
        },
        {"title": "Quantum Algorithm Zoo",
         "authors": "S. Jordan",
         "type": "Web",
         "desc": "Catálogo de algoritmos cuánticos conocidos.",
         "year": 2023,
         "link": "https://quantumalgorithmzoo.org/"
        },
        {"title": "QuTiP: Quantum Toolbox in Python",
         "authors": "J. Johansson et al.",
         "type": "Framework",
         "desc": "Librería Python para simulación de sistemas cuánticos abiertos.",
         "year": 2022,
         "link": "http://qutip.org/"
        },
        {"title": "Quantum Country",
         "authors": "M. Nielsen, A. Olah",
         "type": "Web",
         "desc": "Notas interactivas y tarjetas mnemotécnicas sobre computación cuántica.",
         "year": 2024,
         "link": "https://quantum.country/"
        },
        {"title": "Wikipedia: Computación cuántica",
         "authors": "Wikipedia",
         "type": "Web",
         "desc": "Artículo introductorio y enlaces a recursos adicionales.",
         "year": 2025,
         "link": "https://es.wikipedia.org/wiki/Computaci%C3%B3n_cu%C3%A1ntica"
        },
        {"title": "Quantum Machine Learning",
         "authors": "P. Wittek",
         "type": "Libro",
         "desc": "Introducción a machine learning cuántico.",
         "year": 2014,
         "link": "https://www.springer.com/gp/book/9783319267013"
        },
        {"title": "Quantum Information Theory",
         "authors": "M. Wilde",
         "type": "Libro",
         "desc": "Cobertura moderna de teoría de la información cuántica.",
         "year": 2017,
         "link": "https://www.cambridge.org/9781107176164"
        },
        {"title": "Quantum Error Correction",
         "authors": "D. Gottesman",
         "type": "Paper",
         "desc": "Revisión fundamental sobre corrección de errores cuánticos.",
         "year": 2009,
         "link": "https://arxiv.org/abs/0904.2557"
        },
    ]
    # Filtros y búsqueda
    query = request.args.get('q', '').strip().lower()
    ftype = request.args.get('type', '')
    filtered = [r for r in references if (query in r['title'].lower() or query in r['desc'].lower() or query in r['authors'].lower()) and (ftype == '' or r['type'] == ftype)] if query or ftype else references
    types = sorted(set(r['type'] for r in references))
    # Formulario de búsqueda y filtro
    search_form = f"""
    <form method='get' class='mb-4 row g-2'>
      <div class='col-md-6'>
        <input type='text' class='form-control' name='q' placeholder='Buscar por título, autor o descripción...' value='{query}'>
      </div>
      <div class='col-md-4'>
        <select name='type' class='form-select'>
          <option value=''>--Tipo--</option>
          {''.join(f"<option value='{t}'{' selected' if t==ftype else ''}>{t}</option>" for t in types)}
        </select>
      </div>
      <div class='col-md-2'>
        <button class='btn btn-primary w-100' type='submit'><i class='bi bi-search'></i> Buscar</button>
      </div>
    </form>
    """
    # Tarjetas visuales
    cards = ''.join(f"""
      <div class='col-md-6 mb-3'>
        <div class='card h-100 border-{('primary' if r['type']=='Libro' else 'success' if r['type']=='Framework' else 'info' if r['type']=='Web' else 'warning')}'>
          <div class='card-body'>
            <h5 class='card-title'>{r['title']} <span class='badge bg-secondary'>{r['type']}</span></h5>
            <h6 class='card-subtitle mb-2 text-muted'>{r['authors']} ({r['year']})</h6>
            <p class='card-text'>{r['desc']}</p>
            <a href='{r['link']}' target='_blank' class='btn btn-outline-info btn-sm'><i class='bi bi-box-arrow-up-right'></i> Ver recurso</a>
          </div>
        </div>
      </div>
    """ for r in filtered) if filtered else "<div class='alert alert-warning'>No se encontraron referencias para esa búsqueda.</div>"
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='references') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-12'>
          <h2 class='mb-4'><i class='bi bi-journal-bookmark'></i> Referencias y Recursos</h2>
          {search_form}
        </div>
      </div>
      <div class='row'>
        {cards}
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/export', methods=['GET', 'POST'])
def export_panel():
    # Formatos de exportación ampliados y mejorados
    export_types = [
        {"name": "QASM", "desc": "Exporta el circuito en formato OpenQASM estándar.", "icon": "bi-file-earmark-code", "ext": ".qasm"},
        {"name": "Qiskit", "desc": "Código Python listo para Qiskit.", "icon": "bi-filetype-py", "ext": ".py"},
        {"name": "QuTiP", "desc": "Script Python para simulación con QuTiP.", "icon": "bi-terminal", "ext": ".py"},
        {"name": "Q#", "desc": "Código para Microsoft Q# (Quantum Development Kit).", "icon": "bi-microsoft", "ext": ".qs"},
        {"name": "Cirq", "desc": "Código Python para Google Cirq.", "icon": "bi-google", "ext": ".py"},
        {"name": "Braket", "desc": "Código Python para Amazon Braket.", "icon": "bi-amazon", "ext": ".py"},
        {"name": "ProjectQ", "desc": "Código Python para ProjectQ.", "icon": "bi-terminal-dash", "ext": ".py"},
        {"name": "LaTeX", "desc": "Código LaTeX para \texttt{quantikz}, \texttt{qcircuit} o TikZ.", "icon": "bi-filetype-tex", "ext": ".tex"},
        {"name": "TikZ", "desc": "Circuito en formato TikZ para LaTeX.", "icon": "bi-diagram-3", "ext": ".tex"},
        {"name": "SVG", "desc": "Imagen vectorial escalable del circuito.", "icon": "bi-filetype-svg", "ext": ".svg"},
        {"name": "PNG", "desc": "Imagen PNG del circuito.", "icon": "bi-image", "ext": ".png"},
        {"name": "BMP", "desc": "Imagen BMP del circuito.", "icon": "bi-image", "ext": ".bmp"},
        {"name": "TIFF", "desc": "Imagen TIFF del circuito.", "icon": "bi-image", "ext": ".tiff"},
        {"name": "SVGZ", "desc": "SVG comprimido.", "icon": "bi-filetype-svg", "ext": ".svgz"},
        {"name": "EPS", "desc": "Imagen EPS vectorial.", "icon": "bi-filetype-eps", "ext": ".eps"},
        {"name": "GIF", "desc": "Animación GIF del circuito.", "icon": "bi-filetype-gif", "ext": ".gif"},
        {"name": "MP4", "desc": "Animación MP4 del circuito.", "icon": "bi-filetype-mp4", "ext": ".mp4"},
        {"name": "MOV", "desc": "Animación MOV del circuito.", "icon": "bi-filetype-mov", "ext": ".mov"},
        {"name": "PDF", "desc": "Exporta la visualización del circuito o resultados como PDF.", "icon": "bi-file-earmark-pdf", "ext": ".pdf"},
        {"name": "HTML", "desc": "Exporta el circuito como página HTML interactiva.", "icon": "bi-filetype-html", "ext": ".html"},
        {"name": "JSON", "desc": "Exporta la estructura del circuito en JSON.", "icon": "bi-filetype-json", "ext": ".json"},
        {"name": "YAML", "desc": "Exporta la estructura del circuito en YAML.", "icon": "bi-filetype-yml", "ext": ".yaml"},
        {"name": "CSV", "desc": "Exporta resultados o métricas en CSV.", "icon": "bi-filetype-csv", "ext": ".csv"},
        {"name": "Markdown", "desc": "Exporta el circuito como código Markdown.", "icon": "bi-markdown", "ext": ".md"},
        {"name": "ZIP", "desc": "Descarga todos los archivos relevantes en un ZIP.", "icon": "bi-file-zip", "ext": ".zip"},
        {"name": "DOCX", "desc": "Exporta resultados a Word.", "icon": "bi-file-earmark-word", "ext": ".docx"},
        {"name": "PPTX", "desc": "Exporta resultados a PowerPoint.", "icon": "bi-file-earmark-ppt", "ext": ".pptx"},
        {"name": "XML", "desc": "Exporta el circuito en XML.", "icon": "bi-filetype-xml", "ext": ".xml"},
        {"name": "TXT", "desc": "Exporta el circuito como texto plano.", "icon": "bi-file-earmark-text", "ext": ".txt"},
    ]
    msg = ''
    export_result = ''
    selected = request.form.get('export_type', '') if request.method == 'POST' else ''
    # Procesar exportación (mejor UX y feedback)
    if request.method == 'POST' and selected:
        if selected == 'QASM':
            try:
                from gates.quantum_gates import get_circuit_qasm
                from interpreter.qlang_interpreter import circuit_operations
                qasm = get_circuit_qasm(circuit_operations)
                export_result = f"<textarea class='form-control' rows='8' readonly>{qasm}</textarea>"
                msg = "<div class='alert alert-success'>Código QASM generado. Puedes copiarlo o descargarlo.</div>"
            except Exception as e:
                msg = f"<div class='alert alert-danger'>Error al exportar QASM: {e}</div>"
        elif selected == 'Qiskit':
            try:
                from gates.quantum_gates import get_circuit_qiskit
                from interpreter.qlang_interpreter import circuit_operations
                code = get_circuit_qiskit(circuit_operations)
                export_result = f"<textarea class='form-control' rows='8' readonly>{code}</textarea>"
                msg = "<div class='alert alert-success'>Código Qiskit generado. Puedes copiarlo o descargarlo.</div>"
            except Exception as e:
                msg = f"<div class='alert alert-danger'>Error al exportar Qiskit: {e}</div>"
        elif selected == 'JSON':
            try:
                from interpreter.qlang_interpreter import circuit_operations
                import json
                export_result = f"<textarea class='form-control' rows='8' readonly>{json.dumps(circuit_operations, indent=2)}</textarea>"
                msg = "<div class='alert alert-success'>JSON generado. Puedes copiarlo o descargarlo.</div>"
            except Exception as e:
                msg = f"<div class='alert alert-danger'>Error al exportar JSON: {e}</div>"
        elif selected == 'TXT':
            try:
                from interpreter.qlang_interpreter import circuit_operations
                txt = '\n'.join(str(op) for op in circuit_operations)
                export_result = f"<textarea class='form-control' rows='8' readonly>{txt}</textarea>"
                msg = "<div class='alert alert-success'>Texto plano generado. Puedes copiarlo o descargarlo.</div>"
            except Exception as e:
                msg = f"<div class='alert alert-danger'>Error al exportar TXT: {e}</div>"
        elif selected == 'CSV':
            msg = "<div class='alert alert-info'>Exporta métricas y resultados en CSV desde los paneles de Métricas y Simulación.</div>"
        elif selected == 'HTML':
            msg = "<div class='alert alert-info'>Exportación a HTML interactivo estará disponible próximamente.</div>"
        elif selected == 'PDF':
            msg = "<div class='alert alert-info'>Exporta a PDF desde el panel Circuito o Visualización usando la opción de imprimir/guardar como PDF.</div>"
        elif selected == 'SVG' or selected == 'PNG' or selected == 'BMP' or selected == 'TIFF' or selected == 'SVGZ' or selected == 'EPS' or selected == 'GIF':
            msg = "<div class='alert alert-info'>Descarga la imagen o animación desde el panel Circuito o Visualización.</div>"
        elif selected == 'Markdown':
            msg = "<div class='alert alert-info'>Exportación a Markdown estará disponible próximamente.</div>"
        elif selected == 'YAML':
            msg = "<div class='alert alert-info'>Exportación a YAML estará disponible próximamente.</div>"
        elif selected == 'ZIP':
            msg = "<div class='alert alert-info'>Pronto podrás descargar todos los archivos relevantes en un ZIP.</div>"
        elif selected == 'DOCX':
            msg = "<div class='alert alert-info'>Exportación a Word estará disponible próximamente.</div>"
        elif selected == 'PPTX':
            msg = "<div class='alert alert-info'>Exportación a PowerPoint estará disponible próximamente.</div>"
        elif selected == 'XML':
            msg = "<div class='alert alert-info'>Exportación a XML estará disponible próximamente.</div>"
        elif selected == 'Q#':
            msg = "<div class='alert alert-info'>Exportación a Q# estará disponible próximamente.</div>"
        elif selected == 'QuTiP':
            msg = "<div class='alert alert-info'>Exportación a QuTiP estará disponible próximamente.</div>"
        elif selected == 'Cirq':
            msg = "<div class='alert alert-info'>Exportación a Cirq estará disponible próximamente.</div>"
        elif selected == 'Braket':
            msg = "<div class='alert alert-info'>Exportación a Braket estará disponible próximamente.</div>"
        elif selected == 'ProjectQ':
            msg = "<div class='alert alert-info'>Exportación a ProjectQ estará disponible próximamente.</div>"
        elif selected == 'LaTeX' or selected == 'TikZ':
            msg = "<div class='alert alert-info'>Exportación a LaTeX/TikZ estará disponible próximamente.</div>"
        elif selected == 'MP4' or selected == 'MOV':
            msg = "<div class='alert alert-info'>Exportación de animaciones estará disponible próximamente.</div>"
        else:
            msg = "<div class='alert alert-warning'>Selecciona un formato válido.</div>"
    # Formulario de exportación
    export_form = f"""
    <form method='post' class='mb-4'>
      <div class='row g-3'>
        <div class='col-md-8'>
          <label class='form-label'>Selecciona el formato de exportación:</label>
          <select name='export_type' class='form-select'>
            <option value=''>--Formato--</option>
            {''.join(f"<option value='{e['name']}'{' selected' if selected==e['name'] else ''}>{e['name']}</option>" for e in export_types)}
          </select>
        </div>
        <div class='col-md-4 d-flex align-items-end'>
          <button type='submit' class='btn btn-primary w-100'><i class='bi bi-box-arrow-up'></i> Exportar</button>
        </div>
      </div>
    </form>
    """
    # Tarjetas de exportación rápida
    cards = ''.join(f"""
      <div class='col-md-6 mb-3'>
        <div class='card h-100'>
          <div class='card-body'>
            <h5 class='card-title'>{et['name']} <i class='bi {et['icon']}'></i></h5>
            <p class='card-text'>{et['desc']}</p>
            <form method='post' action='/export' style='display:inline;'>
              <input type='hidden' name='export_type' value='{et['name']}'>
              <button type='submit' class='btn btn-outline-primary btn-sm'><i class='bi bi-download'></i> Exportar {et['name']}</button>
            </form>
          </div>
        </div>
      </div>
    """ for et in export_types)
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='export') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-12'>
          <h2 class='mb-4'><i class='bi bi-box-arrow-up'></i> Exportación Avanzada</h2>
          <p>Exporta tu circuito o resultados en múltiples formatos profesionales para usar en otros simuladores, artículos o presentaciones.</p>
          <div id="export-loading" style="display:none;text-align:center;">
            <div class="spinner-border text-primary" role="status" aria-label="Cargando exportación..."></div>
            <div class="mt-2">Procesando exportación...</div>
          </div>
          {export_form}
          <div aria-live="polite" id="export-feedback">{msg}</div>
          {export_result}
        </div>
      </div>
      <div class='row'>
        {cards}
      </div>
      <div class='alert alert-info mt-4' role='alert'>¿Necesitas un formato especial? ¡Envíanos feedback!</div>
    </div>
    <script>
    // Microinteracción: loading spinner al exportar
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function(e) {{
        if (form.querySelector('select[name="export_type"]')) {{
          document.getElementById('export-loading').style.display = 'block';
        }}
      }});
    }});
    // Accesibilidad: enfocar feedback tras exportar
    window.addEventListener('DOMContentLoaded', function() {{
      var feedback = document.getElementById('export-feedback');
      if (feedback && feedback.textContent.trim().length > 0) {{
        if (feedback.focus) feedback.focus();
      }}
    }});
    </script>
    """ + FOOTER + FEEDBACK_BUTTON
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)