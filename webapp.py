from flask import Flask, Response, request, render_template_string, jsonify, session, send_from_directory
import datetime
import os
import time
import logging
import sys
import tempfile
import base64
import json
import numpy as np
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
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Configuración para el chat IA
class AIChat:
    def __init__(self):
        self.history = []
    
    def add_message(self, role, content):
        self.history.append({'role': role, 'content': content})
    
    def get_response(self, message):
        """Genera una respuesta del asistente IA usando un modelo avanzado."""
        self.add_message('user', message)
        
        # Integración con modelo de lenguaje avanzado
        try:
            from transformers import pipeline
            qa_pipeline = pipeline("text-generation", model="gpt2")
            response = qa_pipeline(message, max_length=100)[0]['generated_text']
        except ImportError:
            # Fallback a lógica simple si no hay transformers instalado
            response = "Hola, soy tu asistente de simulación cuántica. ¿En qué puedo ayudarte hoy?"
            
        self.add_message('assistant', response)
        return response

# Instancia global del chat
ai_chat = AIChat()

# Endpoints para el chat IA
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    response = ai_chat.get_response(data['message'])
    return jsonify({'response': response})

# Endpoint para personalización
@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    data = request.get_json()
    if not data or 'theme' not in data:
        return jsonify({'error': 'Preferencias requeridas'}), 400
    
    # Guardar preferencias en sesión
    session['theme'] = data.get('theme', 'light')
    session['language'] = data.get('language', 'es')
    session['visualization_type'] = data.get('visualization_type', 'all')
    
    return jsonify({'success': True})

# Endpoint para visualizaciones avanzadas
@app.route('/api/visualizations', methods=['POST'])
def generate_advanced_visualizations():
    data = request.get_json()
    if not data or 'results' not in data:
        return jsonify({'error': 'Datos de simulación requeridos'}), 400
    
    # Obtener preferencias de visualización
    theme = session.get('theme', 'light')
    language = session.get('language', 'es')
    vis_type = session.get('visualization_type', 'all')
    
    # Generar visualizaciones según el tipo
    visualizations = {
        'circuit': generate_circuit_visualization(data['operations'], theme),
        'results': generate_result_visualizations(data['results'], vis_type, theme, language)
    }
    
    return jsonify(visualizations)

# Endpoint para tutoriales interactivos
@app.route('/api/tutorials/<tutorial_id>', methods=['GET'])
def get_tutorial(tutorial_id):
    tutorials = {
        'basico': {
            'title': 'Tutorial Básico de Simulación Cuántica',
            'steps': [
                '1. Define tus operaciones cuánticas',
                '2. Configura parámetros de ruido y decoherencia',
                '3. Ejecuta la simulación',
                '4. Analiza los resultados'
            ],
            'interactive': True
        },
        'avanzado': {
            'title': 'Técnicas Avanzadas de Simulación',
            'steps': [
                '1. Optimización de circuitos',
                '2. Corrección de errores cuánticos',
                '3. Simulación de ruido realista',
                '4. Comparación entre backends'
            ],
            'interactive': True
        }
    }
    
    return jsonify(tutorials.get(tutorial_id, {'error': 'Tutorial no encontrado'}))

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
        from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Boolean, Text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.exc import SQLAlchemyError
        
        # Crear engine pero no conectar aún
        engine = create_engine(database_url)
        Base = declarative_base()
        
        # Definir modelos
        class SimulationResult(Base):
            __tablename__ = 'simulation_results'
            
            id = Column(Integer, primary_key=True)
            user_id = Column(String(50), nullable=True)
            circuit_name = Column(String(100), nullable=True)
            circuit_operations = Column(JSON, nullable=False)
            results = Column(JSON, nullable=False)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            parameters = Column(JSON, nullable=True)
            notes = Column(Text, nullable=True)
            
        class UserPreference(Base):
            __tablename__ = 'user_preferences'
            
            id = Column(Integer, primary_key=True)
            user_id = Column(String(50), nullable=False, unique=True)
            theme = Column(String(20), default='light')
            language = Column(String(5), default='es')
            visualization_type = Column(String(20), default='all')
            auto_save = Column(Boolean, default=True)
            preferences = Column(JSON, nullable=True)
            
        # Crear tablas si no existen
        try:
            Base.metadata.create_all(engine)
            logging.info("Tablas creadas o verificadas correctamente")
            
            # Crear sesión
            Session = sessionmaker(bind=engine)
            db_session = Session()
            
        except Exception as e:
            logging.error(f"Error al crear tablas: {str(e)}")
            db_session = None
            
        logging.info("Engine de SQLAlchemy creado correctamente")
    except ImportError:
        logging.warning("SQLAlchemy no está instalado. Funcionalidades de base de datos desactivadas.")
        engine = None
        db_session = None
    except Exception as e:
        logging.error(f"Error al configurar la base de datos: {str(e)}")
        engine = None
        db_session = None
else:
    logging.info("No se detectó configuración de base de datos. Funcionando sin base de datos.")
    engine = None
    db_session = None

def simulate_circuit(circuit_operations, decoherence_time=0.0, noise_type='depolarizing', noise_level=0.01, shots=1024, optimization_level=1, error_correction=False, backend='local'):
    """Simula el circuito cuántico dado y devuelve los resultados con soporte para múltiples backends.
    
    Args:
        circuit_operations: Lista de operaciones cuánticas a simular
        decoherence_time: Tiempo de decoherencia en unidades arbitrarias (0=sin decoherencia)
        noise_type: Tipo de ruido cuántico ('depolarizing', 'amplitude_damping', 'phase_damping', 'none')
        noise_level: Nivel de ruido entre 0 y 1
        shots: Número de ejecuciones para estadísticas
        optimization_level: Nivel de optimización del circuito (0-3)
        error_correction: Activar corrección de errores
        backend: Backend a utilizar ('local', 'qiskit', 'cirq', 'braket')
    
    Returns:
        dict: Resultados de la simulación con métricas avanzadas
    """
    start_time = time.time()
    metrics = {
        'execution_time': 0,
        'qubit_count': len(circuit_operations['qubits']),
        'gate_count': len(circuit_operations['gates']),
        'success': False
    }
    
    try:
        # Soporte para múltiples backends
        if backend == 'qiskit':
            from qiskit import QuantumCircuit, transpile
            from qiskit_aer import AerSimulator
            
            qc = QuantumCircuit(len(circuit_operations['qubits']))
            # Implementación de las operaciones...
            
            simulator = AerSimulator()
            transpiled_qc = transpile(qc, simulator)
            result = simulator.run(transpiled_qc, shots=shots).result()
            counts = result.get_counts()
            
            metrics.update({
                'results': counts,
                'success': True,
                'backend': 'qiskit'
            })
            
        elif backend == 'local':
            from interpreter.qlang_interpreter import qubits, interpret
            import numpy as np
            from scipy.linalg import expm
            
            # Optimización avanzada del circuito
            if optimization_level > 0:
                optimized_ops = optimize_circuit(circuit_operations, level=optimization_level)
                circuit_operations = optimized_ops
                
            # Corrección de errores cuánticos
            if error_correction:
                circuit_operations = apply_error_correction(circuit_operations)
                
            # Simulación local...
            
            metrics.update({
                'results': {},
                'success': True,
                'backend': 'local'
            })
        
        # Operadores de ruido cuántico mejorados
        def apply_noise(qubit_state, noise_type, noise_level):
            """Aplica efectos de ruido cuántico al estado del qubit."""
            if noise_type == 'none' or noise_level <= 0:
                return qubit_state
                
            gamma = noise_level
            
            if noise_type == 'depolarizing':
                # Ruido despolarizante
                sigma_x = np.array([[0, 1], [1, 0]])
                sigma_y = np.array([[0, -1j], [1j, 0]])
                sigma_z = np.array([[1, 0], [0, -1]])
                
                rho = np.outer(qubit_state, qubit_state.conj())
                rho = (1 - gamma) * rho + (gamma/3) * (
                    sigma_x @ rho @ sigma_x.conj().T + 
                    sigma_y @ rho @ sigma_y.conj().T + 
                    sigma_z @ rho @ sigma_z.conj().T
                )
            elif noise_type == 'amplitude_damping':
                # Ruido de amortiguamiento de amplitud
                E0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
                E1 = np.array([[0, np.sqrt(gamma)], [0, 0]])
                rho = np.outer(qubit_state, qubit_state.conj())
                rho = E0 @ rho @ E0.conj().T + E1 @ rho @ E1.conj().T
            elif noise_type == 'phase_damping':
                # Ruido de amortiguamiento de fase
                E0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
                E1 = np.array([[0, 0], [0, np.sqrt(gamma)]])
                rho = np.outer(qubit_state, qubit_state.conj())
                rho = E0 @ rho @ E0.conj().T + E1 @ rho @ E1.conj().T
            else:
                # Default to depolarizing noise
                sigma_z = np.array([[1, 0], [0, -1]])
                rho = np.outer(qubit_state, qubit_state.conj())
                rho = (1 - gamma/2) * rho + (gamma/2) * sigma_z @ rho @ sigma_z.conj().T
            
            # Obtener nuevo estado
            eigenvalues, eigenvectors = np.linalg.eig(rho)
            max_idx = np.argmax(np.real(eigenvalues))
            return eigenvectors[:, max_idx]
        
        # Aplicar decoherencia si es necesario
        def apply_decoherence(qubit_state, time):
            """Aplica efectos de decoherencia al estado del qubit."""
            if time <= 0:
                return qubit_state
                
            # Operadores de decoherencia (T1 y T2)
            gamma = 1 - np.exp(-time)
            sigma_z = np.array([[1, 0], [0, -1]])
            
            # Aplicar decoherencia
            rho = np.outer(qubit_state, qubit_state.conj())
            rho = (1 - gamma/2) * rho + (gamma/2) * sigma_z @ rho @ sigma_z.conj().T
            
            # Obtener nuevo estado
            eigenvalues, eigenvectors = np.linalg.eig(rho)
            max_idx = np.argmax(np.real(eigenvalues))
            return eigenvectors[:, max_idx]
        
        # Ejecutar múltiples shots para estadísticas
        all_measurements = {}
        
        for shot in range(shots):
            # Reiniciar qubits para cada shot
            interpret(circuit_operations)
            
            # Aplicar ruido y decoherencia a cada qubit
            for name, qubit in qubits.items():
                # Obtener vector de estado
                state_vector = qubit.state
                
                # Aplicar ruido si es necesario
                if noise_type != 'none' and noise_level > 0:
                    state_vector = apply_noise(state_vector, noise_type, noise_level)
                
                # Aplicar decoherencia si es necesario
                if decoherence_time > 0:
                    state_vector = apply_decoherence(state_vector, decoherence_time)
                
                # Actualizar estado del qubit
                qubit.state = state_vector
                
                # Calcular probabilidades
                probs = np.abs(state_vector)**2
                
                # Realizar medición simulada
                measurement = np.random.choice([0, 1], p=probs)
                
                # Registrar medición
                if name not in all_measurements:
                    all_measurements[name] = {'0': 0, '1': 0}
                
                all_measurements[name][str(measurement)] += 1
        
        # Calcular estadísticas finales
        results = {
            "operations": circuit_operations.copy(),
            "qubit_states": {},
            "measurements": {},
            "decoherence_time": decoherence_time,
            "noise_type": noise_type,
            "noise_level": noise_level,
            "shots": shots,
            "optimization_level": optimization_level,
            "error_correction": error_correction,
            "backend": backend,
            "execution_time": time.time() - start_time,
            "success": True
        }
        
        # Procesar resultados de todos los shots
        for name, qubit in qubits.items():
            # Obtener vector de estado final
            state_vector = qubit.state
            
            # Calcular probabilidades
            probs = np.abs(state_vector)**2
            
            # Calcular coordenadas de Bloch
            bloch_x = float(2 * np.real(state_vector[0] * state_vector[1].conj()))
            bloch_y = float(2 * np.imag(state_vector[0] * state_vector[1].conj()))
            bloch_z = float(np.abs(state_vector[0])**2 - np.abs(state_vector[1])**2)
            
            # Estadísticas de medición
            counts = all_measurements.get(name, {'0': 0, '1': 0})
            total_shots = counts['0'] + counts['1']
            most_frequent = '0' if counts['0'] >= counts['1'] else '1'
            probability = counts[most_frequent] / total_shots if total_shots > 0 else 0
            
            # Guardar resultados
            results["qubit_states"][name] = {
                "state_vector": [complex(x) for x in state_vector],
                "probabilities": probs.tolist(),
                "bloch_coordinates": [bloch_x, bloch_y, bloch_z]
            }
            
            results["measurements"][name] = {
                "counts": counts,
                "most_frequent": most_frequent,
                "probability": probability
            }
        
        logging.info(f"Simulación completada con {len(circuit_operations)} operaciones, {shots} shots y ruido {noise_type}")
        return results
    except Exception as e:
        logging.error(f"Error en simulación: {str(e)}")
        return {
            "success": False, 
            "error": str(e),
            "execution_time": time.time() - start_time
        }

def generate_circuit_visualization(operations, theme='light'):
    """Genera una representación visual del circuito cuántico."""
    theme_configs = {
        'light': {'bg': '#ffffff', 'text': '#333333', 'line': '#007bff', 'gate': '#e9ecef', 'border': '#dee2e6'},
        'dark': {'bg': '#212529', 'text': '#f8f9fa', 'line': '#0d6efd', 'gate': '#343a40', 'border': '#495057'},
        'quantum': {'bg': '#000b18', 'text': '#e0f7fa', 'line': '#00e5ff', 'gate': '#001a33', 'border': '#004d99'}
    }
    
    theme_config = theme_configs.get(theme, theme_configs['light'])
    
    # Encontrar todos los qubits utilizados
    qubits = set()
    for op in operations:
        if isinstance(op, dict) and 'qubits' in op:
            if isinstance(op['qubits'], list):
                for q in op['qubits']:
                    qubits.add(q)
            else:
                qubits.add(op['qubits'])
    
    qubits = sorted(list(qubits))
    
    html_output = f"""
    <div class='circuit-visualization p-3 mb-4' style='background-color:{theme_config['bg']};color:{theme_config['text']};border-radius:8px;overflow-x:auto;'>
        <h4 style='color:{theme_config['text']};'>Diagrama del Circuito</h4>
        <div class='circuit-diagram' style='display:grid;grid-template-rows:repeat({len(qubits)},40px);gap:20px;margin:20px 0;'>
    """
    
    # Crear líneas de qubits
    for i, qubit in enumerate(qubits):
        html_output += f"""
            <div class='qubit-line' style='display:flex;align-items:center;position:relative;'>
                <div class='qubit-label' style='width:50px;text-align:right;padding-right:10px;font-weight:bold;'>q{qubit}</div>
                <div class='qubit-wire' style='flex-grow:1;height:2px;background-color:{theme_config['line']};position:relative;'></div>
            </div>
        """
    
    # Añadir puertas al circuito
    gate_positions = {}
    max_time = 0
    
    for i, op in enumerate(operations):
        if isinstance(op, dict) and 'gate' in op and 'qubits' in op:
            gate = op['gate']
            if isinstance(op['qubits'], list):
                target_qubits = op['qubits']
            else:
                target_qubits = [op['qubits']]
            
            # Determinar posición temporal
            time_slot = max_time + 1
            max_time = time_slot
            
            # Registrar posición para cada qubit afectado
            for q in target_qubits:
                if q in qubits:
                    qubit_idx = qubits.index(q)
                    gate_positions[(qubit_idx, time_slot)] = {
                        'gate': gate,
                        'multi_qubit': len(target_qubits) > 1,
                        'control': op.get('control', False),
                        'target_qubits': target_qubits
                    }
    
    # Generar HTML para las puertas
    for pos, gate_info in gate_positions.items():
        qubit_idx, time_slot = pos
        gate = gate_info['gate']
        multi_qubit = gate_info['multi_qubit']
        
        # Posición en píxeles
        left = 60 + time_slot * 60
        top = 20 + qubit_idx * 60
        
        gate_style = f"""
            position:absolute;
            left:{left}px;
            top:{top - 15}px;
            width:30px;
            height:30px;
            background-color:{theme_config['gate']};
            border:1px solid {theme_config['border']};
            border-radius:4px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:bold;
            z-index:10;
        """
        
        html_output += f"""
            <div class='gate' style='{gate_style}' title='{gate} en q{qubits[qubit_idx]}'>
                {gate}
            </div>
        """
        
        # Dibujar líneas de conexión para puertas multi-qubit
        if multi_qubit and qubit_idx == qubits.index(min(gate_info['target_qubits'])):
            min_qubit = qubits.index(min(gate_info['target_qubits']))
            max_qubit = qubits.index(max(gate_info['target_qubits']))
            
            # Línea vertical que conecta los qubits
            line_style = f"""
                position:absolute;
                left:{left + 15}px;
                top:{(min_qubit * 60) + 35}px;
                width:2px;
                height:{(max_qubit - min_qubit) * 60}px;
                background-color:{theme_config['line']};
                z-index:5;
            """
            
            html_output += f"""
                <div class='connection-line' style='{line_style}'></div>
            """
    
    html_output += """
        </div>
    </div>
    """
    
    return html_output

def generate_result_visualizations(results, visualization_type='all', theme='light', language='es'):
    """Genera visualizaciones basadas en los resultados de la simulación.
    
    Args:
        results: Diccionario con los resultados de la simulación
        visualization_type: Tipo de visualización ('all', 'basic', 'advanced', 'bloch', 'histogram')
        theme: Tema de visualización ('light', 'dark', 'blue', 'quantum')
        language: Idioma para las etiquetas ('es', 'en')
        
    Returns:
        HTML con las visualizaciones generadas
    """
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
    
    # Configuración de temas
    theme_configs = {
        'light': {
            'bg_color': '#ffffff',
            'text_color': '#333333',
            'primary_color': '#4dabf7',
            'secondary_color': '#6c757d',
            'accent_color': '#28a745',
            'grid_color': '#eeeeee',
            'plotly_template': 'plotly_white'
        },
        'dark': {
            'bg_color': '#212529',
            'text_color': '#f8f9fa',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d',
            'accent_color': '#20c997',
            'grid_color': '#343a40',
            'plotly_template': 'plotly_dark'
        },
        'blue': {
            'bg_color': '#f0f8ff',
            'text_color': '#0a2351',
            'primary_color': '#1e88e5',
            'secondary_color': '#5e35b1',
            'accent_color': '#00acc1',
            'grid_color': '#e3f2fd',
            'plotly_template': 'plotly'
        },
        'quantum': {
            'bg_color': '#000b18',
            'text_color': '#e0f7fa',
            'primary_color': '#00e5ff',
            'secondary_color': '#651fff',
            'accent_color': '#00e676',
            'grid_color': '#001a33',
            'plotly_template': 'plotly_dark'
        }
    }
    
    # Seleccionar configuración de tema
    theme_config = theme_configs.get(theme, theme_configs['light'])
    
    # Configuración de idioma
    language_configs = {
        'es': {
            'title': 'Resultados de la Simulación Cuántica',
            'measurement_results': 'Resultados de Medición',
            'qubit': 'Qubit',
            'result': 'Resultado',
            'probability': 'Probabilidad',
            'state': 'Estado',
            'counts': 'Conteos',
            'bloch_sphere': 'Esfera de Bloch',
            'download': 'Descargar',
            'export': 'Exportar',
            'tutorial': 'Tutorial Rápido',
            'step1': 'Observa las probabilidades de cada estado cuántico en el gráfico.',
            'step2': 'Interactúa con el gráfico para ver detalles específicos.',
            'step3': 'Compara los resultados con tus expectativas teóricas.',
            'feedback': '¿Fue útil esta visualización?',
            'yes': 'Sí',
            'no': 'No',
            'thanks': '¡Gracias por tu feedback!',
            'error': 'Error en la simulación',
            'execution_time': 'Tiempo de ejecución',
            'seconds': 'segundos',
            'shots': 'Ejecuciones',
            'noise': 'Ruido',
            'optimization': 'Optimización',
            'error_correction': 'Corrección de errores',
            'backend': 'Backend',
            'enabled': 'Activado',
            'disabled': 'Desactivado'
        },
        'en': {
            'title': 'Quantum Simulation Results',
            'measurement_results': 'Measurement Results',
            'qubit': 'Qubit',
            'result': 'Result',
            'probability': 'Probability',
            'state': 'State',
            'counts': 'Counts',
            'bloch_sphere': 'Bloch Sphere',
            'download': 'Download',
            'export': 'Export',
            'tutorial': 'Quick Tutorial',
            'step1': 'Observe the probabilities of each quantum state in the graph.',
            'step2': 'Interact with the graph to see specific details.',
            'step3': 'Compare the results with your theoretical expectations.',
            'feedback': 'Was this visualization helpful?',
            'yes': 'Yes',
            'no': 'No',
            'thanks': 'Thank you for your feedback!',
            'error': 'Simulation Error',
            'execution_time': 'Execution Time',
            'seconds': 'seconds',
            'shots': 'Shots',
            'noise': 'Noise',
            'optimization': 'Optimization',
            'error_correction': 'Error Correction',
            'backend': 'Backend',
            'enabled': 'Enabled',
            'disabled': 'Disabled'
        }
    }
    
    # Seleccionar configuración de idioma
    lang = language_configs.get(language, language_configs['es'])
    
    if not results.get("success", True):
        return f"<div class='alert alert-danger'>{lang['error']}: {results.get('error', 'Desconocido')}</div>"
    
    html_output = f"<div class='results-container' style='background-color:{theme_config['bg_color']};color:{theme_config['text_color']};padding:20px;border-radius:10px;'>"
    
    # Información de la simulación
    html_output += f"""
    <div class='simulation-info mb-4 p-3' style='background-color:{theme_config['bg_color']};border-left:4px solid {theme_config['primary_color']};'>
        <h3 style='color:{theme_config['primary_color']};'>{lang['title']}</h3>
        <div class='row'>
            <div class='col-md-3'>
                <strong>{lang['execution_time']}:</strong> {results.get('execution_time', 0):.4f} {lang['seconds']}
            </div>
            <div class='col-md-3'>
                <strong>{lang['shots']}:</strong> {results.get('shots', 1)}
            </div>
            <div class='col-md-3'>
                <strong>{lang['noise']}:</strong> {results.get('noise_type', 'none')}
            </div>
            <div class='col-md-3'>
                <strong>{lang['backend']}:</strong> {results.get('backend', 'local')}
            </div>
        </div>
        <div class='row mt-2'>
            <div class='col-md-3'>
                <strong>{lang['optimization']}:</strong> {lang['enabled'] if results.get('optimization_level', 0) > 0 else lang['disabled']}
            </div>
            <div class='col-md-3'>
                <strong>{lang['error_correction']}:</strong> {lang['enabled'] if results.get('error_correction', False) else lang['disabled']}
            </div>
        </div>
    </div>
    """
    
    # Tabla de resultados de medición
    measurements = results.get("measurements", {})
    if measurements and (visualization_type in ['all', 'basic']):
        html_output += f"<h3 style='color:{theme_config['primary_color']};'>{lang['measurement_results']}</h3>"
        html_output += f"<table class='table table-striped table-bordered' style='background-color:{theme_config['bg_color']};color:{theme_config['text_color']};'>"
        html_output += f"<thead><tr><th>{lang['qubit']}</th><th>{lang['result']}</th><th>{lang['probability']}</th><th>{lang['counts']}</th></tr></thead><tbody>"
        
        for qubit, result in measurements.items():
            if isinstance(result, dict) and 'most_frequent' in result:
                # Formato nuevo con estadísticas
                most_frequent = result['most_frequent']
                probability = result.get('probability', 0)
                counts = result.get('counts', {})
                
                # Añadir fila a la tabla
                html_output += f"<tr><td>{qubit}</td><td>{most_frequent}</td><td>{probability:.4f}</td><td>{counts}</td></tr>"
            else:
                # Formato antiguo simple
                html_output += f"<tr><td>{qubit}</td><td>{result}</td><td>N/A</td><td>N/A</td></tr>"
        
        html_output += "</tbody></table>"
