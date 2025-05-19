from flask import Flask, render_template_string, request, jsonify
import os
from interpreter.qlang_interpreter import qubits, interpret

app = Flask(__name__)

NAVBAR = """
<nav class='navbar navbar-expand-lg navbar-dark bg-dark mb-4'>
  <div class='container-fluid'>
    <a class='navbar-brand' href='/'>Simulador Cuántico</a>
    <div class='collapse navbar-collapse'>
      <ul class='navbar-nav me-auto mb-2 mb-lg-0'>
        <li class='nav-item'><a class='nav-link' href='/qubits'>Qubits</a></li>
        <li class='nav-item'><a class='nav-link' href='/circuit'>Circuito</a></li>
        <li class='nav-item'><a class='nav-link' href='/visualization'>Visualización</a></li>
        <li class='nav-item'><a class='nav-link' href='/simulate'>Simular</a></li>
      </ul>
    </div>
  </div>
</nav>
"""

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

@app.route('/')
def index():
    return render_template_string(
        BOOTSTRAP_HEAD +
        NAVBAR +
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
    """ + FOOTER
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
        NAVBAR +
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
    """ + TOOLTIP_SCRIPT + FOOTER
    )

@app.route('/circuit', methods=['GET', 'POST'])
def circuit_panel():
    from visualizer.circuit_visualizer import plot_circuit
    import io
    import base64
    import matplotlib.pyplot as plt
    from interpreter.qlang_interpreter import circuit_operations, qubits, interpret
    msg = ''
    # Procesar formulario para agregar/eliminar puerta o resetear circuito
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
            # Eliminar la operación idx
            # Se asume que existe un comando para eliminar por índice
            interpret(f"DELETEOP {idx}")
            msg = f"<span style='color:green'>Operación {idx+1} eliminada.</span>"
    # Generar imagen del circuito si hay operaciones
    img_html = "<i>No hay operaciones en el circuito.</i>"
    if circuit_operations:
        fig = plot_circuit(circuit_operations)
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        img_html = f"<img src='data:image/png;base64,{img_b64}' style='max-width:100%;height:auto;border:1px solid #888;' title='Visualización del circuito'>"
    # Formulario para agregar puertas
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
    # Botón para resetear circuito
    reset_form = """
    <form method='post' style='margin-top:10px;display:inline;'>
        <button type='submit' name='action' value='reset_circuit' style='background:#f55;color:white;'>Resetear Circuito</button>
    </form>
    """
    # Mostrar operaciones actuales con opción de eliminar
    ops_html = "<i>No hay operaciones en el circuito.</i>"
    if circuit_operations:
        ops_html = "<ul>" + ''.join(
            f"<li>{op} <form method='post' style='display:inline;'><button type='submit' name='action' value='delete_op_{i}' style='color:#f55;background:none;border:none;cursor:pointer;' title='Eliminar operación'>&#10060;</button></form></li>"
            for i, op in enumerate(circuit_operations)
        ) + "</ul>"
    return render_template_string(
        BOOTSTRAP_HEAD +
        NAVBAR +
        f"""
    <div class='container fade-in'>
      <div class='row'>
        <div class='col-md-8 offset-md-2'>
          <div class='card shadow'>
            <div class='card-body'>
              <h2 class='card-title'><i class='bi bi-diagram-3'></i> Panel de Circuito Cuántico</h2>
              <p>Construye y visualiza tu circuito cuántico aquí.</p>
              <div class='feedback'>{msg}</div>
              {add_gate_form}
              {reset_form}
              <h5>Operaciones actuales:</h5>
              <div class='table-responsive'>{ops_html}</div>
              <h5>Visualización del circuito:</h5>
              {img_html}
            </div>
          </div>
        </div>
      </div>
    </div>
    """ + FOOTER
    )

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
        NAVBAR +
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
    """ + FOOTER
    )

@app.route('/download_img', methods=['POST'])
def download_img():
    from flask import Response
    import base64
    img_data = request.form.get('img_data', '')
    img_name = request.form.get('img_name', 'visualizacion.png')
    img_bytes = base64.b64decode(img_data)
    return Response(
        img_bytes,
        mimetype='image/png',
        headers={'Content-Disposition': f'attachment;filename={img_name}'}
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
        NAVBAR +
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
    """ + FOOTER
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
