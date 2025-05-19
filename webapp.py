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
              <form method='post' class='mb-3'>
                <label class='form-label'>Nombre del qubit: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Elige un nombre único para tu qubit.'></i></label>
                <input type='text' name='qubit_name' class='form-control mb-2' required>
                <button type='submit' class='btn btn-primary'><i class='bi bi-plus-circle'></i> Crear Qubit</button>
              </form>
              {alert}
              <h5>Qubits activos:</h5>
              <div>{qubit_table}</div>
              <form method='post' class='mb-2'>
                <label class='form-label'>Eliminar qubit: <i class='bi bi-question-circle' data-bs-toggle='tooltip' title='Selecciona un qubit para eliminarlo.'></i></label>
                <select name='delete_qubit' class='form-select mb-2'>
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
              <h5>Operaciones y Visualización</h5>
              {gate_form}
              {bloch_form}
              {prob_amp_form}
              {metrics_form}
            </div>
          </div>
        </div>
      </div>
    </div>
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
              <div class='feedback'>{msg}</div>
              {add_gate_form}
              {reset_form}
              <h5>Operaciones actuales:</h5>
              <div class='table-responsive'>{ops_html}</div>
              <h5>Controles de visualización y exportación:</h5>
              {controls_form}
              <h5>Visualización del circuito:</h5>
              {img_html}
              {export_html}
              <div class='mt-3'>
                <span class='badge bg-info'>Tip:</span> <span>Haz zoom, cambia el estilo o exporta tu circuito para usarlo en otros simuladores.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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
              {html}
            </div>
          </div>
        </div>
      </div>
    </div>
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
              <div class='feedback'>{msg}</div>
              {result_html}
              {download_form}
              {download_hist_form}
            </div>
          </div>
        </div>
      </div>
    </div>
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
    <form method='post' action='/download_csv' style='margin-top:10px;'>
        <input type='hidden' name='csv_data' value='{csv_data}'>
        <input type='hidden' name='csv_name' value='metricas_{qubit_name}.csv'>
        <button type='submit' class='btn btn-primary'><i class='bi bi-download'></i> Descargar CSV</button>
    </form>
    """
    return info

# Endpoint para feedback visual
@app.route('/feedback', methods=['POST'])
def feedback():
    # Aquí podrías guardar el feedback en un archivo, base de datos o enviarlo por email
    # Por ahora solo muestra un mensaje de agradecimiento
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar() +
        """
        <div class='container fade-in'>
          <div class='row'>
            <div class='col-md-8 offset-md-2'>
              <div class='alert alert-success mt-5'>¡Gracias por tu feedback! <a href='/' class='btn btn-link'>Volver al inicio</a></div>
            </div>
          </div>
        </div>
        """ + FOOTER
    )

@app.route('/download_csv', methods=['POST'])
def download_csv():
    from flask import Response
    import base64
    csv_data = request.form.get('csv_data', '')
    csv_name = request.form.get('csv_name', 'simulacion_resultados.csv')
    csv_bytes = base64.b64decode(csv_data)
    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={csv_name}'}
    )

@app.route('/metrics')
def metrics_panel():
    from interpreter.qlang_interpreter import qubits
    import numpy as np
    import matplotlib.pyplot as plt
    import io
    import base64
    qubit_names = list(qubits.keys())
    html = ""
    if len(qubit_names) < 2:
        html = "<i>Se requieren al menos dos qubits para métricas globales.</i>"
        return render_template_string(
            BOOTSTRAP_HEAD +
            build_navbar(active='metrics') +
            f"""
        <div class='container fade-in'>
          <div class='row'>
            <div class='col-md-10 offset-md-1'>
              <div class='card shadow'>
                <div class='card-body'>
                  <h2 class='card-title'><i class='bi bi-graph-up'></i> Métricas Avanzadas y Diagnóstico</h2>
                  <p>Panel global de métricas cuánticas, diagnóstico y recomendaciones para tu sistema.</p>
                  {html}
                </div>
              </div>
            </div>
          </div>
        </div>
        """ + FOOTER + FEEDBACK_BUTTON
        )
    # Estado global
    states = [qubits[q].state for q in qubit_names]
    state = states[0]
    for s in states[1:]:
        state = np.kron(state, s)
    rho = np.outer(state, state.conj())
    # Métricas globales
    coherence = np.sum(np.abs(rho - np.diag(np.diag(rho))))
    purity = np.trace(rho @ rho).real
    eigs = np.linalg.eigvalsh(rho)
    entropy = -sum(e*np.log2(e) for e in eigs if e > 1e-10)
    # Entrelazamiento simple
    entangled_pairs = set()
    for q in qubit_names:
        ent_set = getattr(qubits[q], 'entangled_with', set())
        for other in ent_set:
            pair = tuple(sorted([q, other]))
            entangled_pairs.add(pair)
    # Mapa de fidelidad
    n = len(qubit_names)
    fidelity_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            state1 = qubits[qubit_names[i]].state
            state2 = qubits[qubit_names[j]].state
            fidelity_matrix[i, j] = abs(np.vdot(state1, state2)) ** 2
    # Visualización de matriz de densidad
    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(np.real(rho), cmap='RdYlBu')
    fig.colorbar(im)
    ax.set_title('Matriz de Densidad Global (Re)')
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # Diagnóstico y recomendaciones
    recs = []
    if purity < 0.8:
        recs.append('⚠️ Baja pureza global: considera reducir el ruido o simplificar el circuito.')
    if coherence < 0.5:
        recs.append('⚠️ Baja coherencia: revisa la superposición y posibles fuentes de decoherencia.')
    if len(entangled_pairs) == 0:
        recs.append('ℹ️ No se detecta entrelazamiento entre qubits.')
    if np.any(fidelity_matrix < 0.5):
        recs.append('ℹ️ Algunos qubits tienen baja fidelidad entre sí.')
    if not recs:
        recs.append('✅ El sistema cuántico muestra métricas saludables.')
    # Panel visual
    html += f"""
    <div class='row g-3 mb-3'>
      <div class='col-md-4'>
        <div class='card border-success h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Pureza Global <span class='badge bg-success'>{purity:.4f}</span></h5>
            <p class='card-text'>Indica cuán puro es el estado global (1 = puro).</p>
          </div>
        </div>
      </div>
      <div class='col-md-4'>
        <div class='card border-info h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Coherencia l1 Global <span class='badge bg-info text-dark'>{coherence:.4f}</span></h5>
            <p class='card-text'>Mide la superposición cuántica global.</p>
          </div>
        </div>
      </div>
      <div class='col-md-4'>
        <div class='card border-warning h-100'>
          <div class='card-body'>
            <h5 class='card-title'>Entropía von Neumann <span class='badge bg-warning text-dark'>{entropy:.4f}</span></h5>
            <p class='card-text'>Mide el desorden o mezcla del sistema.</p>
          </div>
        </div>
      </div>
    </div>
    <div class='row g-3 mb-3'>
      <div class='col-md-6'>
        <div class='card border-primary'>
          <div class='card-body'>
            <h5 class='card-title'>Matriz de Densidad Global</h5>
            <img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;'>
          </div>
        </div>
      </div>
      <div class='col-md-6'>
        <div class='card border-secondary'>
          <div class='card-body'>
            <h5 class='card-title'>Diagnóstico y Recomendaciones</h5>
            <ul>{''.join(f'<li>{r}</li>' for r in recs)}</ul>
            <b>Pares de qubits entrelazados:</b> {len(entangled_pairs)}<br>
            <b>Total de qubits:</b> {len(qubit_names)}<br>
          </div>
        </div>
      </div>
    </div>
    <div class='row g-3 mb-3'>
      <div class='col-md-12'>
        <div class='card border-dark'>
          <div class='card-body'>
            <h5 class='card-title'>Tabla de Fidelidad Global</h5>
            <table class='table table-bordered' style='border-collapse:collapse;'>
              <tr><th></th>{''.join(f'<th>{q}</th>' for q in qubit_names)}</tr>
              {''.join('<tr><th>'+qubit_names[i]+'</th>' + ''.join(f'<td title="F({qubit_names[i]},{qubit_names[j]})={fidelity_matrix[i,j]:.4f}">{fidelity_matrix[i,j]:.2f}</td>' for j in range(n)) + '</tr>' for i in range(n))}
            </table>
          </div>
        </div>
      </div>
    </div>
    """
    # Exportar métricas CSV
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Métrica', 'Valor'])
    writer.writerow(['Pureza Global', f'{purity:.6f}'])
    writer.writerow(['Coherencia l1 Global', f'{coherence:.6f}'])
    writer.writerow(['Entropía von Neumann', f'{entropy:.6f}'])
    writer.writerow(['Qubits', len(qubit_names)])
    writer.writerow(['Pares entrelazados', len(entangled_pairs)])
    csv_data = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')
    output.close()
    html += f"""
    <form method='post' action='/download_csv' style='margin-top:10px;'>
        <input type='hidden' name='csv_data' value='{csv_data}'>
        <input type='hidden' name='csv_name' value='metricas_globales.csv'>
        <button type='submit' class='btn btn-primary'><i class='bi bi-download'></i> Descargar métricas CSV</button>
    </form>
    """
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='metrics') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-10 offset-md-1'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-graph-up'></i> Métricas Avanzadas y Diagnóstico</h2>
              <p>Panel global de métricas cuánticas, diagnóstico y recomendaciones para tu sistema.</p>
              {html}
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/algorithms', methods=['GET', 'POST'])
def algorithms_panel():
    # Ejemplos de algoritmos cuánticos
    examples = [
        {
            'name': 'Teleportación Cuántica',
            'desc': 'Transfiere el estado de un qubit a otro usando entrelazamiento y medición.',
            'code': 'QUBIT q1\nQUBIT q2\nQUBIT q3\nGATE H q2\nGATE CX q2 q3\nGATE CX q1 q2\nGATE H q1\nMEASURE q1\nMEASURE q2\n# ...'
        },
        {
            'name': 'Algoritmo de Grover',
            'desc': 'Búsqueda cuántica en una base de datos no estructurada.',
            'code': 'QUBIT q0\nQUBIT q1\nGATE H q0\nGATE H q1\n# ...'
        },
        {
            'name': 'Deutsch-Jozsa',
            'desc': 'Distingue funciones balanceadas de constantes con una sola consulta.',
            'code': 'QUBIT q0\nQUBIT q1\nGATE H q0\nGATE H q1\n# ...'
        },
        {
            'name': 'Algoritmo de Shor',
            'desc': 'Factorización eficiente de números enteros (esquema simplificado).',
            'code': 'QUBIT q0\nQUBIT q1\nQUBIT q2\n# ...'
        },
    ]
    selected = request.form.get('example', '') if request.method == 'POST' else ''
    loaded_code = ''
    msg = ''
    if request.method == 'POST' and selected:
        for ex in examples:
            if ex['name'] == selected:
                loaded_code = ex['code']
                msg = f"<div class='alert alert-success'>Ejemplo '{ex['name']}' cargado. Puedes copiar el código y ejecutarlo en el panel de circuito.</div>"
                break
    example_cards = ''.join(f"""
      <div class='col-md-6 mb-3'>
        <div class='card h-100'>
          <div class='card-body'>
            <h5 class='card-title'>{ex['name']}</h5>
            <p class='card-text'>{ex['desc']}</p>
            <form method='post'>
              <input type='hidden' name='example' value='{ex['name']}'>
              <button type='submit' class='btn btn-primary'><i class='bi bi-lightning'></i> Cargar ejemplo</button>
            </form>
          </div>
        </div>
      </div>
    """ for ex in examples)
    code_area = f"""
    <div class='card mt-4'>
      <div class='card-header'>Código del ejemplo seleccionado</div>
      <div class='card-body'>
        <textarea class='form-control' rows='8' readonly>{loaded_code}</textarea>
        <div class='mt-2'><span class='badge bg-info'>Tip:</span> Copia este código y pégalo en el panel de circuito para ejecutarlo.</div>
      </div>
    </div>
    """ if loaded_code else ''
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='algorithms') +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-10 offset-md-1'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-lightbulb'></i> Ejemplos de Algoritmos Cuánticos</h2>
              <p>Explora y carga ejemplos de algoritmos cuánticos clásicos. Pronto podrás ejecutarlos y visualizarlos directamente.</p>
              {msg}
              <div class='row'>
                {example_cards}
              </div>
              {code_area}
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

# Paneles avanzados base
@app.route('/glossary')
def glossary_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='glossary') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-book'></i> Glosario Cuántico</h2>
              <p>Consulta términos y conceptos clave de computación cuántica. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/tutorial')
def tutorial_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='tutorial') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-mortarboard'></i> Tutorial Interactivo</h2>
              <p>Aprende paso a paso sobre qubits, puertas, circuitos y simulación. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/decoherence')
def decoherence_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='decoherence') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-cloud-drizzle'></i> Decoherencia</h2>
              <p>Explora el fenómeno de la decoherencia y su impacto en los sistemas cuánticos. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/history')
def history_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='history') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-clock-history'></i> Historial de Circuitos</h2>
              <p>Consulta y recupera el historial de tus circuitos y simulaciones. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/ai')
def ai_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='ai') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-robot'></i> Asistente IA</h2>
              <p>Recibe sugerencias inteligentes y asistencia para tus circuitos cuánticos. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/exercises')
def exercises_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='exercises') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-trophy'></i> Ejercicios y Retos</h2>
              <p>Pon a prueba tus conocimientos con ejercicios y desafíos cuánticos. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/references')
def references_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='references') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-journal-bookmark'></i> Referencias</h2>
              <p>Consulta bibliografía, papers y recursos recomendados. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )

@app.route('/export')
def export_panel():
    return render_template_string(
        BOOTSTRAP_HEAD +
        build_navbar(active='export') +
        """
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-box-arrow-up'></i> Exportación Avanzada</h2>
              <p>Exporta tus circuitos y resultados a PDF, Q#, QuTiP y más formatos. <span class='badge bg-warning'>Próximamente</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER + FEEDBACK_BUTTON
    )