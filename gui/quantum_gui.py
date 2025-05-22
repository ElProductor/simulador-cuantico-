import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from interpreter.qlang_interpreter import interpret, qubits, bits
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkthemes
import numpy as np

class QuantumGUI:
    EXPLANATION_LABEL = "Explicación Interactiva"
    EXERCISES_LABEL = "Ejercicios y Retos"
    # --- TOOL MENU LABEL CONSTANTS (sin duplicados) ---
    GROVER_EXAMPLE_LABEL = "Ejemplo: Grover"
    SHOR_EXAMPLE_LABEL = "Ejemplo: Shor"
    GHZ_LABEL = "Ecuación Estado GHZ"
    PAULI_LABEL = "Matrices de Pauli"
    HADAMARD_LABEL = "Matriz de Hadamard"
    BELL_LABEL = "Ecuación Estado Bell"
    BLOCH_LABEL = "Ecuación Esfera de Bloch"
    QUBIT_PROB_LABEL = "Graficar Probabilidad Qubit"
    BIT_STATE_LABEL = "Graficar Estados de Bits"
    AMP_SUM_LABEL = "Suma de Amplitudes de Qubits"
    ELIMINAR_QUBIT_LABEL = "Eliminar Qubit"
    TRANSLATOR_LABEL = "Traductor de Lenguajes Cuánticos"
    NOISE_LABEL = "Simulación de Ruido"
    DIAGNOSTIC_LABEL = "Diagnóstico Cuántico"
    OPTIMIZER_LABEL = "Optimizar Circuito"
    HARDWARE_LABEL = "Simular Hardware Real"
    PREMIUM_EXPORT_LABEL = "Exportación Premium"
    ADV_METRICS_LABEL = "Métricas Avanzadas"
    ASSISTANT_LABEL = "Asistente Cuántico (IA)"
    # --- NUEVAS FUNCIONALIDADES ---
    THEME_SELECTOR_LABEL = "Selector de Temas"
    USER_PROFILE_LABEL = "Perfil de Usuario"
    CUSTOM_CIRCUIT_LABEL = "Circuitos Personalizados"
    QUANTUM_GAMES_LABEL = "Juegos Cuánticos"
    LEARNING_PATH_LABEL = "Ruta de Aprendizaje"
    REAL_TIME_COLLAB_LABEL = "Colaboración en Tiempo Real"
    QUANTUM_CHALLENGES_LABEL = "Desafíos Cuánticos"
    HARDWARE_COMPARISON_LABEL = "Comparación de Hardware"
    QUANTUM_NOTEBOOK_LABEL = "Cuaderno Cuántico"
    VOICE_COMMANDS_LABEL = "Comandos de Voz"
    # --- NUEVAS FUNCIONALIDADES ---
    THEME_SELECTOR_LABEL = "Selector de Temas"
    USER_PROFILE_LABEL = "Perfil de Usuario"
    CUSTOM_CIRCUIT_LABEL = "Circuitos Personalizados"
    QUANTUM_GAMES_LABEL = "Juegos Cuánticos"
    LEARNING_PATH_LABEL = "Ruta de Aprendizaje"
    REAL_TIME_COLLAB_LABEL = "Colaboración en Tiempo Real"
    QUANTUM_CHALLENGES_LABEL = "Desafíos Cuánticos"
    HARDWARE_COMPARISON_LABEL = "Comparación de Hardware"
    QUANTUM_NOTEBOOK_LABEL = "Cuaderno Cuántico"
    VOICE_COMMANDS_LABEL = "Comandos de Voz"
    # --- NEW FEATURES ---
    ADVANCED_QUANTUM_LABEL = "Quantum Avanzado"
    MULTI_QUBIT_VISUALIZATION = "Visualización Multi-Qubit"
    TEMPORAL_EVOLUTION = "Evolución Temporal"
    HARDWARE_SIMULATION = "Simulación de Hardware"
    QUANTUM_ALGORITHMS = "Algoritmos Cuánticos"
    QISKIT_INTEGRATION = "Integración con Qiskit"
    STATE_COMPARISON = "Comparación de Estados"
    QUANTUM_ML = "Ejemplos de Machine Learning Cuántico"
    HYBRID_CIRCUITS = "Circuitos Híbridos"
    AI_EXPLANATIONS = "Explicaciones con IA"
    COLLABORATIVE_MODE = "Modo Colaborativo"

    def __init__(self, root):
        # Aplicar tema moderno y colores personalizados
        self.root = root
        self.style = ttkthemes.ThemedStyle(root)
        self.style.set_theme("arc")  # Tema moderno
        # Personalización de colores y fuentes (sin afectar menús)
        # root.option_add("*Font", "Segoe UI 12")  # Eliminar esta línea para evitar errores en menús
        root.configure(bg="#f4f6fa")
        self.style.configure("TLabel", background="#f4f6fa", font=("Segoe UI", 12))
        self.style.configure("TButton", font=("Segoe UI", 12), padding=6)
        self.style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"), foreground="#fff", background="#0072bd")
        self.style.map("Accent.TButton", background=[('active', '#005b8a')])
        self.style.configure("TNotebook", background="#eaf1fb", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 12, "bold"), padding=[12, 6], background="#eaf1fb")
        self.style.map("TNotebook.Tab", background=[('selected', '#0072bd')], foreground=[('selected', '#fff')])
        self.root.title("Simulador Cuántico-Clásico v3.0")
        self.root.geometry("1200x800")
        # Menú principal
        self._setup_menu()
        # Layout principal
        self.main_frame = ttk.Frame(root, style="TFrame")
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        # Panel izquierdo para pestañas
        self.left_panel = ttk.Frame(self.main_frame, style="TFrame")
        self.left_panel.pack(side='left', fill='both', expand=True)
        # Panel derecho para estado y mediciones
        self.right_panel = ttk.Frame(self.main_frame, style="TFrame")
        self.right_panel.pack(side='right', fill='y', padx=5)
        self._setup_state_panel()
        # Crear pestañas
        self.notebook = ttk.Notebook(self.left_panel, style="TNotebook")
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        # Pestaña de Computación Cuántica
        self.quantum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quantum_frame, text='Computación Cuántica')
        self._setup_quantum_tab()
        # Pestaña de Computación Clásica
        self.classical_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.classical_frame, text='Computación Clásica')
        self._setup_classical_tab()
        # Pestaña de Visualización
        self.visual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_frame, text='Visualización')
        self._setup_visual_tab()
        # Área de consola
        self._setup_console()
        # Configurar atajos de teclado
        self._setup_shortcuts()
        # Lista de operaciones recientes
        self.recent_ops = []

    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo Circuito", command=self._new_circuit)
        file_menu.add_command(label="Guardar Circuito", command=self._save_circuit)
        file_menu.add_command(label="Cargar Circuito", command=self._load_circuit)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Mostrar Circuito", command=self._show_circuit)
        view_menu.add_command(label="Mostrar QASM", command=self._show_qasm)
        view_menu.add_command(label="Estadísticas", command=self._show_statistics)
        view_menu.add_command(label="Fidelidad entre Qubits", command=self._show_fidelity)
        view_menu.add_command(label="Entrelazamiento", command=self._show_entanglement)
        view_menu.add_command(label="Matriz de Densidad", command=self._show_density_matrix)
        view_menu.add_command(label="Mapa de Fidelidad", command=self._show_fidelity_heatmap)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Tutorial", command=self._show_tutorial)
        help_menu.add_command(label="Acerca de", command=self._show_about)

        # Menú Educación
        edu_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Educación", menu=edu_menu)
        edu_menu.add_command(label=self.EXPLANATION_LABEL, command=self._show_explanation)
        edu_menu.add_command(label=self.EXERCISES_LABEL, command=self._show_exercises)
        edu_menu.add_separator()
        edu_menu.add_command(label="Recargar Ejercicios", command=self._show_exercises)
        edu_menu.add_command(label="Glosario Cuántico", command=self._show_glossary)
        edu_menu.add_command(label="Referencias y Recursos", command=self._show_references)
        edu_menu.add_separator()
        edu_menu.add_command(label="Más sobre Computación Cuántica", command=self._show_more_quantum_info)

        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label=self.QUBIT_PROB_LABEL, command=self._plot_qubit_probability)
        tools_menu.add_command(label=self.BIT_STATE_LABEL, command=self._plot_bit_state)
        tools_menu.add_command(label=self.AMP_SUM_LABEL, command=self._sum_qubit_amplitudes)
        tools_menu.add_command(label=self.BELL_LABEL, command=self._show_bell_state_equation)
        tools_menu.add_command(label=self.BLOCH_LABEL, command=self._show_bloch_equation)
        tools_menu.add_command(label=self.GROVER_EXAMPLE_LABEL, command=self._show_grover_example)
        tools_menu.add_command(label=self.SHOR_EXAMPLE_LABEL, command=self._show_shor_example)
        tools_menu.add_command(label=self.GHZ_LABEL, command=self._show_ghz_state_equation)
        tools_menu.add_command(label=self.PAULI_LABEL, command=self._show_pauli_matrices)
        tools_menu.add_command(label=self.HADAMARD_LABEL, command=self._show_hadamard_matrix)
        tools_menu.add_command(label="Ejemplo: Suma de Bits", command=self._show_sum_example)
        tools_menu.add_command(label="Ejemplo: Teleportación Cuántica", command=self._show_teleportation_example)
        tools_menu.add_command(label="Ecuación Estado W", command=self._show_w_state_equation)
        tools_menu.add_command(label="Matriz de Toffoli (CCNOT)", command=self._show_toffoli_matrix)
        tools_menu.add_command(label="Ejemplo: Deutsch-Jozsa", command=self._show_deutsch_jozsa_example)
        tools_menu.add_command(label="Ejemplo: Simon", command=self._show_simon_example)
        tools_menu.add_command(label="Ecuación Estado Cluster", command=self._show_cluster_state_equation)
        tools_menu.add_command(label="Matriz de Fredkin (CSWAP)", command=self._show_fredkin_matrix)
        tools_menu.add_command(label="Ejemplo: Bernstein-Vazirani", command=self._show_bernstein_vazirani_example)
        tools_menu.add_separator()
        tools_menu.add_command(label=self.TRANSLATOR_LABEL, command=self._show_translator)

        # Menú Exclusivo
        advanced_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Quantum Avanzado", menu=advanced_menu)
        advanced_menu.add_command(label="Simulación de Ruido", command=self._show_noise_simulation)
        advanced_menu.add_command(label="Diagnóstico y Sugerencias", command=self._show_diagnostic)
        advanced_menu.add_command(label="Optimizador de Circuitos", command=self._show_optimizer)
        advanced_menu.add_command(label="Simulación de Hardware", command=self._show_hardware_sim)
        advanced_menu.add_command(label="Exportación Avanzada", command=self._show_premium_export)
        advanced_menu.add_command(label="Métricas Globales", command=self._show_advanced_metrics)
        advanced_menu.add_command(label="Asistente Inteligente", command=self._show_quantum_assistant)
        advanced_menu.add_command(label="Decoherencia Dinámica", command=self._show_dynamic_decoherence)
        advanced_menu.add_command(label="Métricas Globales", command=self._show_global_metrics)
        advanced_menu.add_command(label=self.MULTI_QUBIT_VISUALIZATION, command=self.show_multi_qubit_visualization)
        advanced_menu.add_command(label=self.TEMPORAL_EVOLUTION, command=self.show_temporal_evolution)
        advanced_menu.add_command(label=self.HARDWARE_SIMULATION, command=self.show_hardware_simulation)
        advanced_menu.add_command(label=self.QUANTUM_ALGORITHMS, command=self.show_quantum_algorithms)
        advanced_menu.add_command(label=self.QISKIT_INTEGRATION, command=self.show_qiskit_integration)
        advanced_menu.add_command(label=self.STATE_COMPARISON, command=self.show_state_comparison)
        advanced_menu.add_command(label=self.QUANTUM_ML, command=self.show_quantum_ml_examples)
        advanced_menu.add_command(label=self.HYBRID_CIRCUITS, command=self.show_hybrid_circuits)
        advanced_menu.add_command(label=self.AI_EXPLANATIONS, command=self.show_ai_explanations)
        advanced_menu.add_command(label=self.COLLABORATIVE_MODE, command=self.show_collaborative_mode)
        
        # Menú Personalización
        personal_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Personalización", menu=personal_menu)
        personal_menu.add_command(label=self.THEME_SELECTOR_LABEL, command=self._show_theme_selector)
        personal_menu.add_command(label=self.USER_PROFILE_LABEL, command=self._show_user_profile)
        personal_menu.add_command(label=self.CUSTOM_CIRCUIT_LABEL, command=self._show_custom_circuits)
        personal_menu.add_command(label=self.QUANTUM_GAMES_LABEL, command=self._show_quantum_games)
        personal_menu.add_command(label=self.LEARNING_PATH_LABEL, command=self._show_learning_path)
        personal_menu.add_command(label=self.REAL_TIME_COLLAB_LABEL, command=self._show_real_time_collab)
        personal_menu.add_command(label=self.QUANTUM_CHALLENGES_LABEL, command=self._show_quantum_challenges)
        personal_menu.add_command(label=self.HARDWARE_COMPARISON_LABEL, command=self._show_hardware_comparison)
        personal_menu.add_command(label=self.QUANTUM_NOTEBOOK_LABEL, command=self._show_quantum_notebook)
        personal_menu.add_command(label=self.VOICE_COMMANDS_LABEL, command=self._show_voice_commands)
        # Menú Historial y Decoherencia
        menubar.add_command(label="Historial de Circuitos", command=self._show_circuit_history)
        menubar.add_command(label="Decoherencia Temporal", command=self._show_decoherence_sim)
        menubar.add_command(label="Pregúntale al Simulador", command=self._show_ask_simulator)

    def _show_explanation(self):
        win = tk.Toplevel(self.root)
        win.title(self.EXPLANATION_LABEL)
        win.geometry("800x600")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        explanation_text = """
        Explicación Interactiva:

        1. Qubits:
           - Los qubits son las unidades básicas de información cuántica.
           - Pueden estar en estados |0⟩, |1⟩ o en una superposición de ambos.

        2. Puertas Cuánticas:
           - Las puertas cuánticas manipulan los estados de los qubits.
           - Ejemplos: Hadamard (H), Pauli-X (X), CNOT.

        3. Entrelazamiento:
           - Dos qubits están entrelazados si sus estados están correlacionados.
           - Cambiar el estado de uno afecta al otro.

        4. Medición:
           - La medición colapsa el estado del qubit a |0⟩ o |1⟩.
           - El resultado depende de las probabilidades del estado.

        5. Circuitos Cuánticos:
           - Los circuitos son secuencias de operaciones cuánticas.
           - Se representan gráficamente con líneas y puertas.

        ¡Explora las herramientas del simulador para aprender más!
        """
        text.insert('1.0', explanation_text)
        text.configure(state='disabled')

    def _show_exercises(self):
        win = tk.Toplevel(self.root)
        win.title(self.EXERCISES_LABEL)
        win.geometry("800x600")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        exercises_text = """
        Ejercicios y Retos:

        1. Crear un qubit y aplicar una puerta Hadamard (H).
           - Observa el estado resultante y las probabilidades.

        2. Entrelazar dos qubits usando una puerta CNOT.
           - Verifica el entrelazamiento en la sección correspondiente.

        3. Implementar el algoritmo de Deutsch-Jozsa:
           - Crea un circuito con 2 qubits.
           - Aplica las puertas necesarias para determinar si una función es constante o balanceada.

        4. Simular ruido en un circuito:
           - Aplica varias puertas a un qubit.
           - Usa la opción de simular ruido y observa los cambios.

        5. Medir fidelidad entre dos qubits:
           - Crea dos qubits en estados diferentes.
           - Calcula la fidelidad entre ellos.

        ¡Completa estos retos para mejorar tus habilidades cuánticas!
        """
        text.insert('1.0', exercises_text)
        text.configure(state='disabled')

    def _show_glossary(self):
        win = tk.Toplevel(self.root)
        win.title("Glosario Cuántico")
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        glossary = """
        Glosario Cuántico:

        Qubit: Unidad básica de información cuántica.
        Superposición: Capacidad de un qubit de estar en varios estados a la vez.
        Entrelazamiento: Correlación cuántica entre dos o más qubits.
        Puerta Cuántica: Operación que modifica el estado de uno o más qubits.
        Medición: Proceso de obtener un valor clásico de un qubit.
        Fidelidad: Medida de similitud entre dos estados cuánticos.
        Decoherencia: Pérdida de propiedades cuánticas debido al entorno.
        Ruido: Alteraciones no deseadas en el sistema cuántico.
        Algoritmo Cuántico: Secuencia de operaciones cuánticas para resolver un problema.
        Circuito Cuántico: Representación gráfica de un algoritmo cuántico.
        """
        text.insert('1.0', glossary)
        text.configure(state='disabled')

    def _show_references(self):
        win = tk.Toplevel(self.root)
        win.title("Referencias y Recursos")
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        references = """
        Referencias y Recursos:

        - Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation and Quantum Information.
        - IBM Quantum Experience: https://quantum-computing.ibm.com/
        - Qiskit: https://qiskit.org/
        - Quantum Country: https://quantum.country/
        - QuTiP: http://qutip.org/
        - Quantum Algorithm Zoo: https://quantumalgorithmzoo.org/
        - Wikipedia: Computación cuántica
        """
        text.insert('1.0', references)
        text.configure(state='disabled')

    def _setup_state_panel(self):
        state_frame = ttk.LabelFrame(self.right_panel, text="Estado del Sistema")
        state_frame.pack(fill='x', padx=5, pady=5)
        
        # Lista de qubits activos (selección múltiple)
        ttk.Label(state_frame, text="Qubits Activos:").pack(pady=2)
        self.qubit_list = tk.Listbox(state_frame, height=5, selectmode=tk.EXTENDED)
        self.qubit_list.pack(fill='x', padx=5, pady=2)
        
        # Lista de bits activos (selección múltiple)
        ttk.Label(state_frame, text="Bits Activos:").pack(pady=2)
        self.bit_list = tk.Listbox(state_frame, height=5, selectmode=tk.EXTENDED)
        self.bit_list.pack(fill='x', padx=5, pady=2)
        
        # Historial de operaciones
        ttk.Label(state_frame, text="Operaciones Recientes:").pack(pady=2)
        self.history_list = tk.Listbox(state_frame, height=8)
        self.history_list.pack(fill='x', padx=5, pady=2)
        
        # Botones de control
        ttk.Button(state_frame, text="Medir Seleccionado", 
                  command=self._measure_selected).pack(fill='x', padx=5, pady=2)
        ttk.Button(state_frame, text="Ver Estado", 
                  command=self._show_selected_state).pack(fill='x', padx=5, pady=2)

    def _setup_quantum_tab(self):
        # Frame principal con scroll
        canvas = tk.Canvas(self.quantum_frame)
        scrollbar = ttk.Scrollbar(self.quantum_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame para crear qubits con diseño mejorado
        qubit_frame = ttk.LabelFrame(scrollable_frame, text="Gestión de Qubits")
        qubit_frame.pack(fill='x', padx=5, pady=5)
        
        input_frame = ttk.Frame(qubit_frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Nombre del qubit:").pack(side='left', padx=5)
        self.qubit_name = ttk.Entry(input_frame, width=10)
        self.qubit_name.pack(side='left', padx=5)
        
        btn_frame = ttk.Frame(qubit_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Crear Qubit", 
                  command=self._create_qubit).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.ELIMINAR_QUBIT_LABEL, 
                  command=self._delete_qubit).pack(side='left', padx=5)
        
        # Puertas cuánticas mejoradas
        gates_frame = ttk.LabelFrame(scrollable_frame, text="Puertas Cuánticas")
        gates_frame.pack(fill='x', padx=5, pady=5)
        
        # Puertas de un qubit con tooltips
        single_gates_frame = ttk.LabelFrame(gates_frame, text="Puertas de Un Qubit")
        single_gates_frame.pack(fill='x', padx=5, pady=5)
        
        gates_info = {
            'H': 'Puerta Hadamard - Crea superposición. Aplica H para poner el qubit en (|0⟩+|1⟩)/√2.',
            'X': 'Puerta NOT (Pauli-X) - Invierte |0⟩ y |1⟩.',
            'Y': 'Puerta Y (Pauli-Y) - Rotación en eje Y, introduce fase imaginaria.',
            'Z': 'Puerta Z (Pauli-Z) - Cambia la fase de |1⟩.',
            'RHW': 'Puerta RHW - Rotación personalizada en la esfera de Bloch.'
        }
        
        row = 0
        col = 0
        for gate, desc in gates_info.items():
            btn = ttk.Button(single_gates_frame, text=gate, 
                           command=lambda g=gate: self._apply_quantum_gate(g))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self._create_tooltip(btn, desc)
            col += 1
            if col > 4:
                col = 0
                row += 1
        
        # Puertas de dos qubits mejoradas
        two_qubit_frame = ttk.LabelFrame(gates_frame, text="Puertas de Dos Qubits")
        two_qubit_frame.pack(fill='x', padx=5, pady=5)
        
        control_frame = ttk.Frame(two_qubit_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="Control:").pack(side='left', padx=2)
        self.control_qubit = ttk.Combobox(control_frame, width=5)
        self.control_qubit.pack(side='left', padx=2)
        
        ttk.Label(control_frame, text="Target:").pack(side='left', padx=2)
        self.target_qubit = ttk.Combobox(control_frame, width=5)
        self.target_qubit.pack(side='left', padx=2)
        
        gates_frame = ttk.Frame(two_qubit_frame)
        gates_frame.pack(fill='x', padx=5, pady=5)
        
        two_gates_info = {
            'CNOT': 'Control-NOT - Si el control es |1⟩, invierte el target. Fundamental para entrelazamiento.',
            'CZ': 'Control-Z - Aplica Z al target si el control es |1⟩.',
            'SWAP': 'SWAP - Intercambia los estados de dos qubits.'
        }
        
        for gate, desc in two_gates_info.items():
            btn = ttk.Button(gates_frame, text=gate,
                           command=lambda g=gate: self._apply_two_qubit_gate(g))
            btn.pack(side='left', padx=2)
            self._create_tooltip(btn, desc)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _setup_classical_tab(self):
        # Frame para crear bits
        bit_frame = ttk.LabelFrame(self.classical_frame, text="Gestión de Bits")
        bit_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(bit_frame, text="Nombre del bit:").pack(side='left', padx=5)
        self.bit_name = ttk.Entry(bit_frame, width=10)
        self.bit_name.pack(side='left', padx=5)
        ttk.Button(bit_frame, text="Crear Bit", 
                  command=self._create_bit).pack(side='left', padx=5)
        
        # Frame para valor del bit
        value_frame = ttk.Frame(bit_frame)
        value_frame.pack(side='left', padx=20)
        ttk.Label(value_frame, text="Valor:").pack(side='left', padx=5)
        self.bit_value = ttk.Entry(value_frame, width=2)
        self.bit_value.pack(side='left', padx=5)
        ttk.Button(value_frame, text="Set", 
                  command=self._set_bit).pack(side='left', padx=5)
        
        # Frame para puertas clásicas
        gates_frame = ttk.LabelFrame(self.classical_frame, text="Puertas Clásicas")
        gates_frame.pack(fill='x', padx=5, pady=5)
        
        # NOT gate
        not_frame = ttk.Frame(gates_frame)
        not_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(not_frame, text="NOT Gate - Bit:").pack(side='left', padx=5)
        self.not_bit = ttk.Entry(not_frame, width=5)
        self.not_bit.pack(side='left', padx=5)
        ttk.Button(not_frame, text="Apply NOT", 
                  command=lambda: self._apply_classical_gate("NOT")).pack(side='left', padx=5)
        
        # Two-bit gates
        two_bit_frame = ttk.Frame(gates_frame)
        two_bit_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(two_bit_frame, text="Bit 1:").pack(side='left', padx=2)
        self.bit1 = ttk.Entry(two_bit_frame, width=5)
        self.bit1.pack(side='left', padx=2)
        
        ttk.Label(two_bit_frame, text="Bit 2:").pack(side='left', padx=2)
        self.bit2 = ttk.Entry(two_bit_frame, width=5)
        self.bit2.pack(side='left', padx=2)
        
        for gate in ['AND', 'OR', 'XOR', 'NAND', 'NOR']:
            btn = ttk.Button(two_bit_frame, text=gate,
                           command=lambda g=gate: self._apply_classical_gate(g))
            btn.pack(side='left', padx=2)

    def _setup_visual_tab(self):
        btn_frame = ttk.Frame(self.visual_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        # Bloch sphere
        bloch_frame = ttk.Frame(btn_frame)
        bloch_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(bloch_frame, text="Qubit:").pack(side='left', padx=5)
        self.bloch_qubit = ttk.Entry(bloch_frame, width=5)
        self.bloch_qubit.pack(side='left', padx=5)
        ttk.Button(bloch_frame, text="Mostrar Esfera de Bloch",
                  command=self._show_bloch).pack(side='left', padx=5)
        
        # Circuit
        ttk.Button(btn_frame, text="Mostrar Circuito",
                  command=self._show_circuit).pack(fill='x', padx=5, pady=5)
        
        # QASM
        ttk.Button(btn_frame, text="Mostrar QASM",
                  command=self._show_qasm).pack(fill='x', padx=5, pady=5)

        # Estadísticas
        ttk.Button(btn_frame, text="Mostrar Estadísticas",
                  command=self._show_statistics).pack(fill='x', padx=5, pady=5)

        # Fidelidad
        ttk.Button(btn_frame, text="Mostrar Fidelidad",
                  command=self._show_fidelity).pack(fill='x', padx=5, pady=5)

        # Matriz de Densidad
        ttk.Button(btn_frame, text="Mostrar Matriz de Densidad",
                  command=self._show_density_matrix).pack(fill='x', padx=5, pady=5)

        # Mapa de Fidelidad
        ttk.Button(btn_frame, text="Mostrar Mapa de Fidelidad",
                  command=self._show_fidelity_heatmap).pack(fill='x', padx=5, pady=5)

        # Entrelazamiento
        ttk.Button(btn_frame, text="Mostrar Entrelazamiento",
                  command=self._show_entanglement).pack(fill='x', padx=5, pady=5)

    def _setup_console(self):
        console_frame = ttk.LabelFrame(self.root, text="Consola")
        console_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=10)
        self.console.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Redirigir la salida estándar a la consola
        import sys
        class ConsoleRedirector:
            def __init__(self, widget):
                self.widget = widget
            
            def write(self, text):
                self.widget.insert('end', text)
                self.widget.see('end')
            
            def flush(self):
                # Método requerido para la compatibilidad con sys.stdout
                pass
        
        sys.stdout = ConsoleRedirector(self.console)

    def _create_tooltip(self, widget, text):
        # Tooltip mejorado con fondo y borde
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert") if hasattr(widget, 'bbox') else (0,0,0,0)
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = ttk.Label(self.tooltip, text=text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, font=("Segoe UI", 11))
            label.pack(ipadx=6, ipady=3)
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def _setup_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self._new_circuit())
        self.root.bind('<Control-s>', lambda e: self._save_circuit())
        self.root.bind('<Control-o>', lambda e: self._load_circuit())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F1>', lambda e: self._show_tutorial())

    def _new_circuit(self):
        if messagebox.askyesno("Nuevo Circuito", 
                             "¿Desea crear un nuevo circuito? Se perderán los cambios no guardados."):
            self._clear_all()
            self.add_to_history("Nuevo circuito creado")

    def _save_circuit(self):
        # Implementar guardado de circuito
        self.add_to_history("Circuito guardado")
        messagebox.showinfo("Guardar", "Circuito guardado exitosamente")

    def _load_circuit(self):
        # Implementar carga de circuito
        self.add_to_history("Circuito cargado")
        messagebox.showinfo("Cargar", "Circuito cargado exitosamente")

    def _show_tutorial(self):
        tutorial = tk.Toplevel(self.root)
        tutorial.title("Tutorial Interactivo")
        tutorial.geometry("700x500")
        steps = [
            ("Bienvenido", "Este tutorial te guiará por las funciones principales del simulador cuántico-clásico."),
            ("Crear Qubits", "En la pestaña 'Computación Cuántica', ingresa un nombre y haz clic en 'Crear Qubit'."),
            ("Aplicar Puertas", "Selecciona un qubit y aplica puertas cuánticas usando los botones. Usa tooltips para aprender sobre cada puerta."),
            ("Visualización", "En la pestaña 'Visualización', explora la esfera de Bloch, el circuito, QASM y estadísticas."),
            ("Entrelazamiento y Fidelidad", "Utiliza las opciones de 'Ver' para analizar entrelazamiento, matriz de densidad y fidelidad entre qubits."),
            ("Ayuda y Educación", "Consulta el menú 'Educación' para explicaciones, ejercicios y glosario cuántico."),
            ("¡Listo!", "Ahora puedes explorar el simulador por tu cuenta. ¡Diviértete aprendiendo computación cuántica!")
        ]
        idx = tk.IntVar(value=0)
        def update_step():
            title, msg = steps[idx.get()]
            step_label.config(text=f"Paso {idx.get()+1} de {len(steps)}: {title}")
            text_area.config(state='normal')
            text_area.delete('1.0', 'end')
            text_area.insert('1.0', msg)
            text_area.config(state='disabled')
            prev_btn.config(state='normal' if idx.get() > 0 else 'disabled')
            next_btn.config(state='normal' if idx.get() < len(steps)-1 else 'disabled')
        step_label = ttk.Label(tutorial, font=("Arial", 14, "bold"))
        step_label.pack(pady=10)
        text_area = scrolledtext.ScrolledText(tutorial, height=10, font=("Arial", 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=10)
        btn_frame = ttk.Frame(tutorial)
        btn_frame.pack(pady=10)
        prev_btn = ttk.Button(btn_frame, text="Anterior", command=lambda: (idx.set(idx.get()-1), update_step()))
        prev_btn.pack(side='left', padx=10)
        next_btn = ttk.Button(btn_frame, text="Siguiente", command=lambda: (idx.set(idx.get()+1), update_step()))
        next_btn.pack(side='left', padx=10)
        close_btn = ttk.Button(btn_frame, text="Cerrar", command=tutorial.destroy)
        close_btn.pack(side='left', padx=10)
        update_step()

    def _show_about(self):
        messagebox.showinfo("Acerca de", 
                          "Simulador Cuántico-Clásico v3.0\n"
                          "Desarrollado para simular computación cuántica y clásica\n"
                          "©2025")

    def add_to_history(self, operation):
        self.recent_ops.append(operation)
        self.history_list.insert(0, operation)
        if self.history_list.size() > 50:  # Mantener solo las últimas 50 operaciones
            self.history_list.delete(50)
        # Guardar snapshot del circuito para historial avanzado
        try:
            from interpreter.qlang_interpreter import circuit_operations
            if not hasattr(self, '_circuit_snapshots'):
                self._circuit_snapshots = []
            import copy
            self._circuit_snapshots.append(copy.deepcopy(circuit_operations))
            if len(self._circuit_snapshots) > 10:
                self._circuit_snapshots.pop(0)
        except Exception:
            pass

    def _measure_selected(self):
        selections = self.qubit_list.curselection()
        if not selections:
            messagebox.showwarning("Medir", "Por favor seleccione uno o más qubits para medir")
            return
            
        # Crear ventana de resultados
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultados de Medición")
        result_window.geometry("400x350")
        
        # Área de resultados
        result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, height=10)
        result_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Medir cada qubit seleccionado
        results = []
        for idx in selections:
            qubit_name = self.qubit_list.get(idx)
            try:
                interpret(f"MEASURE {qubit_name}")
                result = qubits[qubit_name].measure()
                results.append((qubit_name, result))
                result_text.insert('end', f"Qubit {qubit_name}: |{result}⟩\n")
            except Exception as e:
                result_text.insert('end', f"Error midiendo {qubit_name}: {str(e)}\n")
        
        # Hacer el texto de solo lectura
        result_text.configure(state='disabled')
        
        # Botones de acción
        btn_frame = ttk.Frame(result_window)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        def save_results():
            # Implementar guardado de resultados
            messagebox.showinfo("Guardar", "Resultados guardados")
            
        ttk.Button(btn_frame, text="Guardar Resultados", 
                  command=save_results).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cerrar", 
                  command=result_window.destroy).pack(side='right', padx=5)
        
        # Explicación automática
        exp = self._explain_measurement(results)
        ttk.Label(result_window, text=exp, wraplength=350, foreground='blue').pack(pady=3)
        
        self.add_to_history(f"Medición realizada en {len(selections)} qubit(s)")

    def _explain_measurement(self, results):
        if not results:
            return "No se pudo medir ningún qubit."
        if all(r[1] == 0 for r in results):
            return "Todos los qubits colapsaron a |0⟩. Probablemente estaban en ese estado."
        if all(r[1] == 1 for r in results):
            return "Todos los qubits colapsaron a |1⟩. Probablemente estaban en ese estado."
        return "Los resultados muestran la naturaleza probabilística de la medición cuántica."

    def _show_selected_state(self):
        from interpreter.qlang_interpreter import qubits
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import math
        selections = self.qubit_list.curselection()
        if not selections:
            messagebox.showwarning("Ver Estado", "Por favor seleccione uno o más qubits")
            return
        state_window = tk.Toplevel(self.root)
        state_window.title("Análisis Avanzado de Estado Cuántico")
        state_window.geometry("1200x900")
        header_frame = ttk.Frame(state_window)
        header_frame.pack(fill='x', padx=10, pady=5)
        qubit_name = self.qubit_list.get(selections[0])
        ttk.Label(header_frame, text=f"Análisis del Qubit: {qubit_name}", font=("Arial", 16, "bold"), foreground="#0072bd").pack(side='left', pady=10)
        notebook = ttk.Notebook(state_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        # Estado vectorial y amplitudes
        vector_frame = ttk.Frame(notebook)
        notebook.add(vector_frame, text='Estado Vectorial')
        state = qubits[qubit_name].state
        vector_text = f"|ψ⟩ = {state[0]:.4f}|0⟩ + {state[1]:.4f}|1⟩"
        ttk.Label(vector_frame, text="Representación Vectorial:", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(vector_frame, text=vector_text, font=("Consolas", 14)).pack(pady=5)
        # Visualización polar
        fig_polar = plt.Figure(figsize=(6, 6))
        ax_polar = fig_polar.add_subplot(111, projection='polar')
        amplitudes = [abs(state[0]), abs(state[1])]
        phases = [np.angle(state[0]), np.angle(state[1])]
        ax_polar.scatter(phases, amplitudes, c=['#0072bd', '#d95319'], s=100)
        ax_polar.set_title('Representación Polar de Amplitudes')
        canvas_polar = FigureCanvasTkAgg(fig_polar, master=vector_frame)
        canvas_polar.draw()
        canvas_polar.get_tk_widget().pack(pady=10)
        # Bloch 3D interactivo
        bloch_frame = ttk.Frame(notebook)
        notebook.add(bloch_frame, text='Esfera de Bloch 3D')
        fig_bloch = plt.Figure(figsize=(6, 6))
        ax_bloch = fig_bloch.add_subplot(111, projection='3d')
        coords = qubits[qubit_name].get_bloch_coords()
        # Esfera
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax_bloch.plot_surface(x, y, z, color='c', alpha=0.1)
        # Ejes
        ax_bloch.quiver(0, 0, 0, 1, 0, 0, color='r', linewidth=2)
        ax_bloch.quiver(0, 0, 0, 0, 1, 0, color='g', linewidth=2)
        ax_bloch.quiver(0, 0, 0, 0, 0, 1, color='b', linewidth=2)
        # Vector estado
        ax_bloch.quiver(0, 0, 0, coords['x'], coords['y'], coords['z'], color='#e74c3c', linewidth=4)
        ax_bloch.set_title('Esfera de Bloch')
        ax_bloch.set_xlim([-1, 1])
        ax_bloch.set_ylim([-1, 1])
        ax_bloch.set_zlim([-1, 1])
        canvas_bloch = FigureCanvasTkAgg(fig_bloch, master=bloch_frame)
        canvas_bloch.draw()
        canvas_bloch.get_tk_widget().pack(pady=10)
        # Evolución temporal (simulada)
        evolution_frame = ttk.Frame(notebook)
        notebook.add(evolution_frame, text='Evolución Temporal')
        fig_evo = plt.Figure(figsize=(7, 5))
        ax_evo = fig_evo.add_subplot(111)
        # Simula una evolución simple (Hadamard repetido)
        H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
        states = [state.copy()]
        for _ in range(12):
            new_state = H @ states[-1]
            new_state /= np.linalg.norm(new_state)
            states.append(new_state)
        probs_0 = [abs(s[0])**2 for s in states]
        probs_1 = [abs(s[1])**2 for s in states]
        ax_evo.plot(probs_0, 'b.-', label='|0⟩')
        ax_evo.plot(probs_1, 'r.-', label='|1⟩')
        ax_evo.set_title('Evolución de Probabilidades (Hadamard)')
        ax_evo.set_xlabel('Paso')
        ax_evo.set_ylabel('Probabilidad')
        ax_evo.legend()
        canvas_evo = FigureCanvasTkAgg(fig_evo, master=evolution_frame)
        canvas_evo.draw()
        canvas_evo.get_tk_widget().pack(pady=10)
        # Métricas avanzadas
        metrics_frame = ttk.Frame(notebook)
        notebook.add(metrics_frame, text='Métricas')
        metrics_text = scrolledtext.ScrolledText(metrics_frame, height=18, font=("Consolas", 12))
        metrics_text.pack(fill='both', expand=True, padx=10, pady=10)
        purity = qubits[qubit_name].get_purity()
        coherence = qubits[qubit_name].get_coherence()
        coords = qubits[qubit_name].get_bloch_coords()
        # Entropía de von Neumann
        rho = np.outer(state, state.conj())
        eigs = np.linalg.eigvalsh(rho)
        entropy = -sum(e*np.log2(e) for e in eigs if e > 1e-10)
        # Fidelidad con otros qubits
        fidelities = []
        for q in qubits:
            if q != qubit_name:
                f = abs(np.vdot(state, qubits[q].state)) ** 2
                fidelities.append(f"{q}: {f:.4f}")
        metrics_info = f"""
        MÉTRICAS DEL ESTADO CUÁNTICO
        ============================
        Pureza: {purity:.6f}
        Coherencia: {coherence:.6f}
        Entropía von Neumann: {entropy:.6f}
        Coordenadas de Bloch: X={coords['x']:.4f}, Y={coords['y']:.4f}, Z={coords['z']:.4f}
        Fidelidad con otros qubits: {'; '.join(fidelities) if fidelities else 'N/A'}
        Ángulos Esféricos: θ={math.acos(coords['z']):.4f} rad, φ={math.atan2(coords['y'], coords['x']):.4f} rad
        """
        metrics_text.insert('1.0', metrics_info)
        metrics_text.configure(state='disabled')
        # Historial
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text='Historial')
        history_text = scrolledtext.ScrolledText(history_frame, height=15, font=("Consolas", 12))
        history_text.pack(fill='both', expand=True, padx=10, pady=10)
        history = qubits[qubit_name].get_history()
        for entry in history:
            if entry['type'] == 'state_change':
                history_text.insert('end', "Cambio de Estado:\n")
                history_text.insert('end', f"  Estado: {entry['state']}\n")
                history_text.insert('end', f"  Probabilidades: {entry['probabilities']}\n")
            elif entry['type'] == 'gate':
                history_text.insert('end', "Aplicación de Puerta:\n")
                history_text.insert('end', f"  Estado resultante: {entry['resulting_state']}\n")
            elif entry['type'] == 'measurement':
                history_text.insert('end', "Medición:\n")
                history_text.insert('end', f"  Resultado: {entry['outcome']}\n")
                history_text.insert('end', f"  Estado previo: {entry['state_before']}\n")
            history_text.insert('end', "\n")
        history_text.configure(state='disabled')
        # Panel de acciones
        action_frame = ttk.Frame(state_window)
        action_frame.pack(fill='x', padx=10, pady=5)
        def export_data():
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt"), ("Todos los archivos", "*.*")], title="Guardar análisis de estado")
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Análisis de Estado - Qubit {qubit_name}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Estado Vectorial:\n{vector_text}\n\n")
                    f.write(f"Métricas Avanzadas:\n{metrics_info}\n\n")
                messagebox.showinfo("Exportar", f"Datos guardados en {filename}")
        def reset_qubit():
            if messagebox.askyesno("Reset", "¿Desea reiniciar el qubit a |0⟩?"):
                qubits[qubit_name].reset()
                self._show_selected_state()
                state_window.destroy()
        def apply_hadamard():
            H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
            qubits[qubit_name].apply_gate(H)
            self._show_selected_state()
            state_window.destroy()
        ttk.Button(action_frame, text="Exportar Datos", command=export_data).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Reset a |0⟩", command=reset_qubit).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Aplicar Hadamard", command=apply_hadamard).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Cerrar", command=state_window.destroy).pack(side='right', padx=5)
        # Sugerencia IA (demo)
        ia_frame = ttk.Frame(state_window)
        ia_frame.pack(fill='x', padx=10, pady=5)
        ia_text = scrolledtext.ScrolledText(ia_frame, height=4, font=("Consolas", 11))
        ia_text.pack(fill='x', expand=True)
        ia_text.insert('1.0', "Sugerencia IA: "
            "\n- Si la pureza < 1, el estado está mezclado.\n"
            "- Si la coherencia es baja, hay decoherencia.\n"
            "- Si la fidelidad con otros qubits es alta, hay posible entrelazamiento.\n"
            "- Usa la evolución temporal para analizar estabilidad.")
        ia_text.configure(state='disabled')

    def _clear_all(self):
        global qubits, bits, circuit_operations
        qubits.clear()
        bits.clear()
        circuit_operations.clear()
        self.qubit_list.delete(0, tk.END)
        self.bit_list.delete(0, tk.END)
        self.history_list.delete(0, tk.END)
        self.console.delete('1.0', tk.END)

    def _update_qubit_lists(self):
        self.qubit_list.delete(0, tk.END)
        self.control_qubit['values'] = list(qubits.keys())
        self.target_qubit['values'] = list(qubits.keys())
        for qubit in qubits:
            self.qubit_list.insert(tk.END, qubit)

    def _update_bit_lists(self):
        self.bit_list.delete(0, tk.END)
        for bit in bits:
            self.bit_list.insert(tk.END, bit)

    def _create_qubit(self):
        name = self.qubit_name.get()
        if name:
            interpret(f"QUBIT {name}")
            self.qubit_name.delete(0, 'end')
            self._update_qubit_lists()
            self.add_to_history(f"Qubit {name} creado")
            # Show Bloch sphere for new qubit
            self._show_bloch(name)

    def _delete_qubit(self):
        selection = self.qubit_list.curselection()
        if not selection:
            messagebox.showwarning(self.ELIMINAR_QUBIT_LABEL, "Por favor seleccione un qubit para eliminar.")
            return
        qubit_name = self.qubit_list.get(selection[0])
        if qubit_name in qubits:
            # Eliminar qubit del diccionario
            del qubits[qubit_name]
            # Eliminar operaciones del circuito asociadas a ese qubit
            try:
                from interpreter.qlang_interpreter import circuit_operations
                circuit_operations[:] = [op for op in circuit_operations if op.get('target') != qubit_name and op.get('control', None) != qubit_name]
            except Exception:
                pass
            self._update_qubit_lists()
            self.add_to_history(f"Qubit {qubit_name} eliminado")
        else:
            messagebox.showerror(self.ELIMINAR_QUBIT_LABEL, f"El qubit '{qubit_name}' no existe.")

    def _create_bit(self):
        name = self.bit_name.get()
        if name:
            interpret(f"BIT {name}")
            self.bit_name.delete(0, 'end')
            self._update_bit_lists()
            self.add_to_history(f"Bit {name} creado")

    def _set_bit(self):
        name = self.bit_name.get()
        value = self.bit_value.get()
        if name and value in ['0', '1']:
            interpret(f"SET {name} {value}")
            self.bit_value.delete(0, 'end')
            self._update_bit_lists()
            self.add_to_history(f"Bit {name} establecido a {value}")

    def _apply_quantum_gate(self, gate):
        target = self.qubit_name.get()
        if target:
            interpret(f"GATE {gate} {target}")

    def _apply_two_qubit_gate(self, gate):
        control = self.control_qubit.get()
        target = self.target_qubit.get()
        if control and target:
            interpret(f"GATE {gate} {control} {target}")

    def _apply_classical_gate(self, gate):
        if gate == "NOT":
            bit = self.not_bit.get()
            if bit:
                interpret(f"GATE NOT {bit}")
                self.add_to_history(f"Puerta NOT aplicada a {bit}")
                self.not_bit.delete(0, 'end')
                self._update_bit_lists()
        else:
            bit1 = self.bit1.get()
            bit2 = self.bit2.get()
            if bit1 and bit2:
                interpret(f"GATE {gate} {bit1} {bit2}")
                self.add_to_history(f"Puerta {gate} aplicada entre {bit1} y {bit2}")
                self.bit1.delete(0, 'end')
                self.bit2.delete(0, 'end')
                self._update_bit_lists()
                
    def _show_bloch(self, qubit=None):
        """Muestra la esfera de Bloch para un qubit.
        Args:
            qubit: Opcional, nombre del qubit. Si no se proporciona, se usa el valor del campo bloch_qubit.
        """
        if qubit is None:
            qubit = self.bloch_qubit.get()
        if not qubit:
            return
        if qubit not in qubits:
            messagebox.showerror("Error", f"El qubit {qubit} no existe")
            return
            
        # Crear una nueva ventana para la esfera de Bloch o reusar una existente
        if hasattr(self, 'bloch_window') and tk.Toplevel.winfo_exists(self.bloch_window):
            self.bloch_window.lift()
            self.bloch_window.focus_force()
        else:
            self.bloch_window = tk.Toplevel(self.root)
            self.bloch_window.title(f"Esfera de Bloch - Qubit {qubit}")
            self.bloch_window.geometry("800x900")
        
        # Crear figura de matplotlib
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Dibujar la esfera
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, alpha=0.13, color='#1f77b4', edgecolor='w', linewidth=0.2, zorder=1)
        
        # Dibujar los ejes
        ax.plot([-1,1], [0,0], [0,0], color='#333', alpha=0.7, lw=2, zorder=2)
        ax.plot([0,0], [-1,1], [0,0], color='#333', alpha=0.7, lw=2, zorder=2)
        ax.plot([0,0], [0,0], [-1,1], color='#333', alpha=0.7, lw=2, zorder=2)
        
        # Etiquetas
        ax.text(1.18, 0, 0, "|+⟩", fontsize=15, color='#0072bd', weight='bold')
        ax.text(-1.18, 0, 0, "|-⟩", fontsize=15, color='#0072bd', weight='bold')
        ax.text(0, 1.18, 0, "|i⟩", fontsize=15, color='#d95319', weight='bold')
        ax.text(0, -1.18, 0, "|-i⟩", fontsize=15, color='#d95319', weight='bold')
        ax.text(0, 0, 1.22, "|0⟩", fontsize=16, color='#228B22', weight='bold')
        ax.text(0, 0, -1.22, "|1⟩", fontsize=16, color='#a2142f', weight='bold')
        
        # Puntos en polos y ejes
        ax.scatter([0,0,0,0,1,-1], [0,1,-1,0,0,0], [1,-1,0,0,0,0],
                   color=['#228B22','#d95319','#d95319','#0072bd','#0072bd','#a2142f'],
                   s=70, alpha=0.7, zorder=4)
          # Dibujar el estado del qubit
        coords = qubits[qubit].get_bloch_coords()
        ax.quiver(0, 0, 0, coords['x'], coords['y'], coords['z'],
                 color='#e74c3c', arrow_length_ratio=0.13, linewidth=3, zorder=5)
          # Mostrar valores numéricos
        state = qubits[qubit].state
        prob_0 = abs(state[0])**2
        prob_1 = abs(state[1])**2
        theta = np.arccos(coords['z'])
        phi = np.arctan2(coords['y'], coords['x'])
        
        # Mejorar visualización
        ax.set_box_aspect([1,1,1])
        ax.set_xlabel('X', fontsize=13, labelpad=10)
        ax.set_ylabel('Y', fontsize=13, labelpad=10)
        ax.set_zlabel('Z', fontsize=13, labelpad=10)
        ax.set_title(f'Esfera de Bloch - Estado de {qubit}', fontsize=17, pad=22)
        ax.set_xlim([-1.25, 1.25])
        ax.set_ylim([-1.25, 1.25])
        ax.set_zlim([-1.25, 1.25])
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.view_init(elev=25, azim=35)
        
        # Integrar la figura con Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.bloch_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Añadir barra de herramientas de Matplotlib
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.bloch_window)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Interactividad personalizada: arrastrar para rotar y zoom con rueda
        class DragRotateZoom:
            def __init__(self, ax, canvas):
                self.ax = ax
                self.canvas = canvas
                self.press = None
                self.elev = ax.elev
                self.azim = ax.azim
                canvas.mpl_connect('button_press_event', self.on_press)
                canvas.mpl_connect('button_release_event', self.on_release)
                canvas.mpl_connect('motion_notify_event', self.on_motion)
                canvas.mpl_connect('scroll_event', self.on_scroll)
            def on_press(self, event):
                if event.inaxes != self.ax:
                    return
                self.press = (event.x, event.y, self.ax.elev, self.ax.azim)
            def on_release(self, event):
                self.press = None
            def on_motion(self, event):
                if self.press is None or event.inaxes != self.ax:
                    return
                x0, y0, elev0, azim0 = self.press
                dx = event.x - x0
                dy = event.y - y0
                self.ax.view_init(elev=elev0 - dy * 0.5, azim=azim0 - dx * 0.5)
                self.canvas.draw_idle()
            def on_scroll(self, event):
                # Zoom in/out
                scale = 1.1 if event.button == 'up' else 0.9
                xlim = self.ax.get_xlim3d()
                ylim = self.ax.get_ylim3d()
                zlim = self.ax.get_zlim3d()
                self.ax.set_xlim3d([v*scale for v in xlim])
                self.ax.set_ylim3d([v*scale for v in ylim])
                self.ax.set_zlim3d([v*scale for v in zlim])
                self.canvas.draw_idle()
                
        DragRotateZoom(ax, canvas)
        
        # Botón para resetear la vista
        def reset_view():
            ax.set_xlim([-1.25, 1.25])
            ax.set_ylim([-1.25, 1.25])
            ax.set_zlim([-1.25, 1.25])
            ax.view_init(elev=25, azim=35)
            canvas.draw_idle()
            
        reset_btn = ttk.Button(self.bloch_window, text="Reset Vista", command=reset_view)
        reset_btn.pack(side=tk.BOTTOM, pady=5)
        
        # Botón para exportar imagen
        def export_img():
            from tkinter import filedialog
            file = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG','*.png'),('All files','*.*')])
            if file:
                fig.savefig(file, dpi=200)
                messagebox.showinfo("Exportar Imagen", f"Imagen guardada en:\n{file}")
                
        export_btn = ttk.Button(self.bloch_window, text="Exportar Imagen", command=export_img)
        export_btn.pack(side=tk.BOTTOM, pady=5)
        
        # Panel de información detallada
        info_frame = ttk.LabelFrame(self.bloch_window, text="Información del Qubit")
        info_frame.pack(fill='x', padx=10, pady=10)
        info_text = (
            f"Estado vectorial:\n"
            f"  |ψ⟩ = {state[0]:.4f} |0⟩ + {state[1]:.4f} |1⟩\n"
            f"Probabilidades:\n"
            f"  P(|0⟩) = {prob_0:.4f}\n"
            f"  P(|1⟩) = {prob_1:.4f}\n"
            f"Coordenadas de Bloch:\n"
            f"  x = {coords[0]:.4f}, y = {coords[1]:.4f}, z = {coords[2]:.4f}\n"
            f"Ángulos esfera de Bloch:\n"
            f"  θ = {theta:.4f} rad\n"
            f"  φ = {phi:.4f} rad\n"
        )
        label = tk.Label(info_frame, text=info_text, font=("Consolas", 13), justify='left', anchor='w')
        label.pack(fill='x', padx=10, pady=10)
        
        # Panel de ayuda
        help_frame = ttk.LabelFrame(self.bloch_window, text="Ayuda Esfera de Bloch")
        help_frame.pack(fill='x', padx=10, pady=5)
        help_text = (
            "- Arrastra con el mouse para rotar la esfera.\n"
            "- Usa la rueda del mouse para hacer zoom.\n"
            "- Haz clic en 'Reset Vista' para restaurar la orientación.\n"
            "- Haz clic en 'Exportar Imagen' para guardar la visualización.\n"
        )
        help_label = tk.Label(help_frame, text=help_text, font=("Arial", 11), justify='left', anchor='w')
        help_label.pack(fill='x', padx=10, pady=5)
        
        self.add_to_history(f"Visualización de esfera de Bloch para {qubit}")

    def _show_circuit(self):
        circuit_window = tk.Toplevel(self.root)
        circuit_window.title("Visualización Avanzada del Circuito")
        circuit_window.geometry("1000x700")
        
        # Marco principal
        main_frame = ttk.Frame(circuit_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel superior con controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles de Visualización")
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Opciones de visualización
        display_frame = ttk.Frame(control_frame)
        display_frame.pack(fill='x', padx=5, pady=5)
        
        # Escala de zoom
        ttk.Label(display_frame, text="Zoom:").pack(side='left', padx=5)
        zoom_scale = ttk.Scale(display_frame, from_=0.5, to=2.0, length=200,
                             orient='horizontal')
        zoom_scale.set(1.0)
        zoom_scale.pack(side='left', padx=5)
        
        # Estilo de visualización
        ttk.Label(display_frame, text="Estilo:").pack(side='left', padx=15)
        style_var = tk.StringVar(value="modern")
        ttk.Radiobutton(display_frame, text="Moderno", variable=style_var,
                       value="modern").pack(side='left', padx=5)
        ttk.Radiobutton(display_frame, text="Clásico", variable=style_var,
                       value="classic").pack(side='left', padx=5)
        
        # Panel de visualización
        vis_frame = ttk.Frame(main_frame)
        vis_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 8))
        canvas = FigureCanvasTkAgg(fig, vis_frame)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        def draw_circuit():
            ax.clear()
            from interpreter.qlang_interpreter import circuit_operations
            
            if not circuit_operations:
                ax.text(0.5, 0.5, "Circuito vacío", ha='center', va='center',
                       fontsize=12, color='gray')
                canvas.draw()
                return
            
            # Obtener todos los qubits usados
            qubit_indices = set()
            for op in circuit_operations:
                qubit_indices.add(op['target'])
                if 'control' in op:
                    qubit_indices.add(op['control'])
            qubit_indices = sorted(qubit_indices)
            qubit_map = {q: i for i, q in enumerate(qubit_indices)}
            num_qubits = len(qubit_indices)
            
            # Ajustar dimensiones
            zoom = zoom_scale.get()
            ax.set_xlim(-1, max(8, len(circuit_operations)))
            ax.set_ylim(-0.5, num_qubits - 0.5)
            
            # Estilo moderno o clásico
            if style_var.get() == "modern":
                # Fondo y grid modernos
                ax.set_facecolor('#f8f9fa')
                ax.grid(True, linestyle='--', alpha=0.3)
                gate_colors = {
                    'H': '#3498db',  # Azul
                    'X': '#e74c3c',  # Rojo
                    'Y': '#2ecc71',  # Verde
                    'Z': '#f1c40f',  # Amarillo
                    'CNOT': '#9b59b6', # Morado
                    'CZ': '#34495e',  # Gris oscuro
                    'SWAP': '#1abc9c' # Turquesa
                }
            else:
                # Estilo clásico
                ax.set_facecolor('white')
                ax.grid(False)
                gate_colors = {k: 'white' for k in ['H','X','Y','Z','CNOT','CZ','SWAP']}
            
            # Dibujar líneas de qubits
            for i, q in enumerate(qubit_indices):
                ax.plot([0, len(circuit_operations)], [i, i], 'k-', lw=1.5)
                ax.text(-0.5, i, f'q{q}', ha='right', va='center',
                       fontsize=12*zoom, fontweight='bold')
                
            # Dibujar puertas
            for i, op in circuit_operations:
                if op['type'] == 'single':
                    y = qubit_map[op['target']]
                    gate = op['gate']
                    color = gate_colors.get(gate, '#95a5a6')
                    
                    if style_var.get() == "modern":
                        # Diseño moderno con sombras y gradientes
                        rect = plt.Rectangle((i-0.3, y-0.3), 0.6, 0.6,
                                          facecolor=color, edgecolor='black',
                                          alpha=0.8, zorder=2)
                        ax.add_patch(rect)
                        # Añadir efecto de sombra
                        shadow = plt.Rectangle((i-0.28, y-0.28), 0.6, 0.6,
                                            facecolor='gray', alpha=0.1, zorder=1)
                        ax.add_patch(shadow)
                    else:
                        # Diseño clásico
                        rect = plt.Rectangle((i-0.2, y-0.2), 0.4, 0.4,
                                          facecolor='white', edgecolor='black',
                                          zorder=2)
                        ax.add_patch(rect)
                    
                    ax.text(i, y, gate, ha='center', va='center',
                           fontsize=11*zoom, fontweight='bold',
                           color='white' if style_var.get() == "modern" else 'black')
                
                else:  # Puertas de dos qubits
                    y1 = qubit_map[op['control']]
                    y2 = qubit_map[op['target']]
                    
                    if style_var.get() == "modern":
                        # Línea de control moderna
                        ax.plot([i, i], [y1, y2], '-', color='#2c3e50',
                               lw=2.5, zorder=1)
                        # Punto de control con gradiente
                        ax.plot(i, y1, 'o', color='#2c3e50',
                               markersize=10*zoom, zorder=3)
                    else:
                        # Estilo clásico
                        ax.plot([i, i], [y1, y2], 'k-', lw=2, zorder=1)
                        ax.plot(i, y1, 'ko', markersize=8*zoom, zorder=3)
                    
                    if op['gate'] == 'CNOT':
                        if style_var.get() == "modern":
                            circle = plt.Circle((i, y2), 0.2*zoom,
                                             facecolor='white',
                                             edgecolor='#2c3e50', lw=2, zorder=3)
                        else:
                            circle = plt.Circle((i, y2), 0.15*zoom,
                                             facecolor='white',
                                             edgecolor='black', lw=1.5, zorder=3)
                        ax.add_patch(circle)
                        ax.plot([i-0.2*zoom, i+0.2*zoom], [y2, y2], 'k-',
                               lw=1.5, zorder=4)
                    else:
                        # Otras puertas de dos qubits
                        if style_var.get() == "modern":
                            rect = plt.Rectangle((i-0.3, y2-0.3), 0.6, 0.6,
                                              facecolor=gate_colors.get(op['gate'], '#95a5a6'),
                                              edgecolor='black', alpha=0.8, zorder=2)
                        else:
                            rect = plt.Rectangle((i-0.2, y2-0.2), 0.4, 0.4,
                                              facecolor='white',
                                              edgecolor='black', zorder=2)
                        ax.add_patch(rect)
                        ax.text(i, y2, op['gate'], ha='center', va='center',
                               fontsize=11*zoom, fontweight='bold',
                               color='white' if style_var.get() == "modern" else 'black')
            
            ax.set_title("Circuito Cuántico", pad=20, fontsize=14*zoom,
                        fontweight='bold', color='#2c3e50')
            ax.axis('off')
            canvas.draw()
        
        # Barra de herramientas
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(toolbar, text="Actualizar",
                  command=draw_circuit).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Exportar",
                  command=lambda: self._export_circuit(fig)).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Cerrar",
                  command=circuit_window.destroy).pack(side='right', padx=5)
        
        # Inicializar visualización
        draw_circuit()
        
        # Configurar callbacks
        style_var.trace('w', lambda *args: draw_circuit())
        zoom_scale.config(command=lambda *args: draw_circuit())

    def _show_qasm(self):
        # Obtener el QASM del circuito
        try:
            from interpreter.qlang_interpreter import circuit_operations
            from gates.quantum_gates import get_circuit_qasm
            qasm = get_circuit_qasm(circuit_operations)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el código QASM:\n{e}")
            return
        # Crear una nueva ventana para el código QASM
        qasm_window = tk.Toplevel(self.root)
        qasm_window.title("Código QASM")
        qasm_window.geometry("700x500")
        # Área de texto con scroll
        text_area = scrolledtext.ScrolledText(qasm_window, wrap=tk.WORD, font=("Consolas", 12))
        text_area.pack(expand=True, fill='both', padx=10, pady=10)
        # Insertar el código QASM
        text_area.insert('1.0', qasm)
        text_area.configure(state='disabled')
        # Botón para copiar al portapapeles
        def copy_to_clipboard():
            qasm_window.clipboard_clear()
            qasm_window.clipboard_append(qasm)
            messagebox.showinfo("Copiado", "Código QASM copiado al portapapeles")
        copy_btn = ttk.Button(qasm_window, text="Copiar al Portapapeles", 
                            command=copy_to_clipboard)
        copy_btn.pack(pady=5)
        self.add_to_history("Código QASM mostrado")

    def _show_statistics(self):
        win = tk.Toplevel(self.root)
        win.title("Estadísticas del Circuito")
        win.geometry("600x500")
        try:
            from interpreter.qlang_interpreter import circuit_operations, qubits, bits
        except ImportError:
            messagebox.showerror("Error", "No se pudo importar el estado del circuito.")
            return
        gate_count = len(circuit_operations)
        qubit_count = len(qubits)
        bit_count = len(bits)
        entangled = sum(1 for q in qubits if getattr(qubits[q], 'entangled_with', set()))
        # Contar tipos de puertas
        from collections import Counter
        gate_types = Counter(op['gate'] for op in circuit_operations if 'gate' in op)
        # Estadísticas de estados
        prob_0 = {q: abs(qubits[q].state[0])**2 for q in qubits}
        prob_1 = {q: abs(qubits[q].state[1])**2 for q in qubits}
        text = scrolledtext.ScrolledText(win, height=25, font=("Consolas", 11))
        text.pack(expand=True, fill='both')
        text.insert('end', f"Qubits activos: {qubit_count}\n")
        text.insert('end', f"Bits clásicos activos: {bit_count}\n")
        text.insert('end', f"Operaciones en el circuito: {gate_count}\n")
        text.insert('end', f"Qubits entrelazados: {entangled}\n\n")
        text.insert('end', "Tipos de puertas aplicadas:\n")
        for g, c in gate_types.items():
            text.insert('end', f"  {g}: {c}\n")
        text.insert('end', "\nProbabilidades de medición de qubits:\n")
        for q in qubits:
            text.insert('end', f"  {q}: P(|0⟩)={prob_0[q]:.4f}, P(|1⟩)={prob_1[q]:.4f}\n")
        text.insert('end', "\nEstados de bits clásicos:\n")
        for b in bits:
            text.insert('end', f"  {b}: {bits[b].get_state()}\n")
        text.insert('end', "\n(Más estadísticas próximamente: profundidad de circuito, entrelazamiento global, etc.)\n")
        text.configure(state='disabled')

    def _show_fidelity(self):
        win = tk.Toplevel(self.root)
        win.title("Fidelidad entre Qubits")
        win.geometry("400x200")
        if self.qubit_list.size() < 2:
            ttk.Label(win, text="Se requieren al menos dos qubits.").pack(pady=20)
            return
        selections = self.qubit_list.curselection()
        if len(selections) != 2:
            ttk.Label(win, text="Seleccione exactamente dos qubits para comparar.").pack(pady=20)
            return
        q1 = self.qubit_list.get(selections[0])
        q2 = self.qubit_list.get(selections[1])
        from interpreter.qlang_interpreter import qubits
        state1 = qubits[q1].state
        state2 = qubits[q2].state
        import numpy as np
        fidelity = abs(np.vdot(state1, state2)) ** 2
        ttk.Label(win, text=f"Fidelidad entre {q1} y {q2}:", font=("Arial", 14)).pack(pady=20)
        ttk.Label(win, text=f"F = {fidelity:.6f}", font=("Arial", 18, "bold")).pack(pady=10)

    def _show_density_matrix(self):
        win = tk.Toplevel(self.root)
        win.title("Matriz de Densidad")
        win.geometry("600x400")
        selections = self.qubit_list.curselection()
        if not selections:
            ttk.Label(win, text="Por favor seleccione uno o más qubits para mostrar la matriz de densidad.", foreground='red').pack(pady=20)
            return
        text = scrolledtext.ScrolledText(win, height=15)
        text.pack(expand=True, fill='both')
        for idx in selections:
            qubit_name = self.qubit_list.get(idx)
            qubit = qubits[qubit_name]
            # Calcular matriz de densidad para qubit puro
            state = qubit.state.reshape(-1, 1)
            rho = np.dot(state, state.conj().T)
            text.insert('end', f"Qubit {qubit_name} (matriz de densidad):\n{np.array2string(rho, precision=4)}\n\n")
        text.configure(state='disabled')

    def _show_fidelity_heatmap(self):
        win = tk.Toplevel(self.root)
        win.title("Mapa de Fidelidad entre Qubits")
        win.geometry("700x600")
        qubit_names = list(qubits.keys())
        n = len(qubit_names)
        if n < 2:
            ttk.Label(win, text="Se requieren al menos dos qubits para el mapa de fidelidad.", foreground='red').pack(pady=30)
            return
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        fidelity_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                state1 = qubits[qubit_names[i]].state
                state2 = qubits[qubit_names[j]].state
                fidelity_matrix[i, j] = abs(np.vdot(state1, state2)) ** 2
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 6))
        cax = ax.imshow(fidelity_matrix, cmap='viridis', vmin=0, vmax=1)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(qubit_names)
        ax.set_yticklabels(qubit_names)
        ax.set_title("Mapa de Fidelidad entre Qubits")
        fig.colorbar(cax, ax=ax, label='Fidelidad')
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _show_entanglement(self):
        win = tk.Toplevel(self.root)
        win.title("Entrelazamiento Global")
        win.geometry("500x250")
        # Métrica simple: contar pares de qubits entrelazados
        entangled_pairs = set()
        for q in qubits:
            ent_set = getattr(qubits[q], 'entangled_with', set())
            for other in ent_set:
                pair = tuple(sorted([q, other]))
                entangled_pairs.add(pair)
        total_pairs = len(entangled_pairs)
        total_qubits = len(qubits)
        ttk.Label(win, text=f"Pares de qubits entrelazados: {total_pairs}", font=("Arial", 14)).pack(pady=10)
        ttk.Label(win, text=f"Total de qubits: {total_qubits}", font=("Arial", 12)).pack(pady=5)
        if total_pairs == 0:
            ttk.Label(win, text="No hay entrelazamiento detectado.", foreground='red').pack(pady=10)
        else:
            ttk.Label(win, text="Pares entrelazados:", font=("Arial", 12, "bold")).pack(pady=5)
            for pair in entangled_pairs:
                ttk.Label(win, text=f"{pair[0]} ↔ {pair[1]}").pack()

    def _show_more_quantum_info(self):
        win = tk.Toplevel(self.root)
        win.title("Más sobre Computación Cuántica")
        win.geometry("850x650")
        scrolledtext.ScrolledText(win, wrap=tk.WORD).pack_forget()  # Remove unused variable
        text_widget = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text_widget.pack(expand=True, fill='both', padx=10, pady=10)
        more_info = """
        Más sobre Computación Cuántica:

        - Principio de Superposición:
          Un qubit puede estar en una combinación lineal de |0⟩ y |1⟩, lo que permite procesar información de manera paralela.

        - Entrelazamiento Cuántico:
          Dos o más qubits pueden compartir un estado conjunto, de modo que la medición de uno afecta instantáneamente al otro, sin importar la distancia.

        - Puertas Cuánticas Universales:
          Un conjunto pequeño de puertas (como Hadamard, CNOT y Pauli) puede construir cualquier operación cuántica.

        - Medición y Colapso:
          Medir un qubit lo fuerza a tomar un valor clásico (|0⟩ o |1⟩), colapsando su estado de superposición.

        - Algoritmos Cuánticos Famosos:
          * Algoritmo de Shor: Factoriza números grandes eficientemente.
          * Algoritmo de Grover: Búsqueda en una base de datos no ordenada en raíz cuadrada del tiempo clásico.
          * Teleportación Cuántica: Transfiere el estado de un qubit a otro distante usando entrelazamiento.

        - Decoherencia y Ruido:
          Los sistemas cuánticos son sensibles al entorno, lo que puede destruir la información cuántica. Por eso, la corrección de errores cuánticos es un área activa de investigación.

        - Computadoras Cuánticas Actuales:
          Los dispositivos actuales (IBM, Google, IonQ, Rigetti) tienen decenas a cientos de qubits, pero aún son ruidosos y limitados.

        - Simulación Cuántica:
          Simular sistemas cuánticos en computadoras clásicas es costoso, pero esencial para el desarrollo de nuevos algoritmos y materiales.

        - Aplicaciones:
          * Criptografía post-cuántica
          * Optimización
          * Simulación de materiales y moléculas
          * Machine Learning cuántico

        ¡Sigue explorando y experimentando con el simulador para aprender más!
        """
        text_widget.insert('1.0', more_info)
        text_widget.configure(state='disabled')

    def _plot_qubit_probability(self):
        selections = self.qubit_list.curselection()
        if not selections:
            messagebox.showwarning("Probabilidad Qubit", "Seleccione al menos un qubit para graficar.")
            return
        _, ax = plt.subplots(figsize=(6, 4))
        labels = []
        probs_0 = []
        probs_1 = []
        for idx in selections:
            qubit_name = self.qubit_list.get(idx)
            p0 = abs(qubits[qubit_name].state[0])**2
            p1 = abs(qubits[qubit_name].state[1])**2
            labels.append(qubit_name)
            probs_0.append(p0)
            probs_1.append(p1)
        x = np.arange(len(labels))
        ax.bar(x-0.15, probs_0, width=0.3, label='P(|0⟩)')
        ax.bar(x+0.15, probs_1, width=0.3, label='P(|1⟩)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1)
        ax.set_ylabel('Probabilidad')
        ax.set_title('Probabilidades de Medición de Qubits')
        ax.legend()
        plt.tight_layout()
        plt.show()

    def _plot_bit_state(self):
        bit_names = list(bits.keys())
        if not bit_names:
            messagebox.showwarning("Bits", "No hay bits para graficar.")
            return
        states = [bits[b].get_state() for b in bit_names]
        _, ax = plt.subplots(figsize=(6, 3))
        ax.bar(bit_names, states, color='skyblue')
        ax.set_ylim(-0.1, 1.1)
        ax.set_ylabel('Estado')
        ax.set_title('Estados de Bits Clásicos')
        plt.tight_layout()
        plt.show()

    def _sum_qubit_amplitudes(self):
        selections = self.qubit_list.curselection()
        if not selections:
            messagebox.showwarning("Suma de Amplitudes", "Seleccione al menos un qubit.")
            return
        total = sum(qubits[self.qubit_list.get(idx)].state[0] + qubits[self.qubit_list.get(idx)].state[1] for idx in selections)
        messagebox.showinfo("Suma de Amplitudes", f"Suma total de amplitudes: {total}")

    def _show_bell_state_equation(self):
        win = tk.Toplevel(self.root)
        win.title(self.BELL_LABEL)
        win.geometry("600x200")
        eq = "|Φ+⟩ = (|00⟩ + |11⟩)/√2\n|Φ-⟩ = (|00⟩ - |11⟩)/√2\n|Ψ+⟩ = (|01⟩ + |10⟩)/√2\n|Ψ-⟩ = (|01⟩ - |10⟩)/√2"
        label = tk.Label(win, text=eq, font=("Consolas", 16), justify='left')
        label.pack(padx=20, pady=30)

    def _show_bloch_equation(self):
        win = tk.Toplevel(self.root)
        win.title(self.BLOCH_LABEL)
        win.geometry("600x200")
        eq = "|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩\nθ ∈ [0, π], φ ∈ [0, 2π]"
        label = tk.Label(win, text=eq, font=("Consolas", 16), justify='left')
        label.pack(padx=20, pady=30)

    def _show_grover_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Algoritmo de Grover")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Algoritmo de Grover

        1. Inicializa n qubits en |0⟩
        2. Aplica Hadamard a todos los qubits
        3. Aplica el oráculo (marca el estado buscado)
        4. Aplica el operador de difusión
        5. Repite pasos 3-4 √N veces
        6. Mide los qubits: obtendrás el estado buscado con alta probabilidad
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_shor_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Algoritmo de Shor")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Algoritmo de Shor

        1. Escoge un número N a factorizar.
        2. Escoge un número a < N, coprimo con N.
        3. Usa un registro cuántico para encontrar el período r de la función f(x) = a^x mod N.
        4. Si r es par y a^(r/2) ≠ -1 mod N, entonces los factores de N son gcd(a^(r/2)±1, N).
        5. Si no, repite con otro a.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_ghz_state_equation(self):
        win = tk.Toplevel(self.root)
        win.title("Ecuación Estado GHZ")
        win.geometry("600x200")
        eq = "|GHZ⟩ = (|000⟩ + |111⟩)/√2"
        label = tk.Label(win, text=eq, font=("Consolas", 18), justify='left')
        label.pack(padx=20, pady=30)

    def _show_pauli_matrices(self):
        win = tk.Toplevel(self.root)
        win.title("Matrices de Pauli")
        win.geometry("700x300")
        eq = (
            "X = σₓ = [[0, 1], [1, 0]]\n"
            "Y = σᵧ = [[0, -i], [i, 0]]\n"
            "Z = σ_z = [[1, 0], [0, -1]]\n"
            "\nDonde i = raíz de -1.\nLas matrices de Pauli son fundamentales en la computación cuántica."
        )
        label = tk.Label(win, text=eq, font=("Consolas", 15), justify='left')
        label.pack(padx=20, pady=30)

    def _show_hadamard_matrix(self):
        win = tk.Toplevel(self.root)
        win.title("Matriz de Hadamard")
        win.geometry("600x200")
        eq = (
            "H = (1/√2) * [[1, 1], [1, -1]]\n"
            "\nLa puerta Hadamard crea superposición entre |0⟩ y |1⟩."
        )
        label = tk.Label(win, text=eq, font=("Consolas", 16), justify='left')
        label.pack(padx=20, pady=30)

    def _show_sum_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Suma de Bits Clásicos")
        win.geometry("600x300")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Suma de Bits Clásicos

        1. Crea dos bits clásicos: a y b.
        2. Aplica la puerta XOR para obtener la suma (sin acarreo): SUM = a XOR b
        3. Aplica la puerta AND para obtener el acarreo: CARRY = a AND b
        4. Resultado: Suma binaria de dos bits.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_teleportation_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Teleportación Cuántica")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Teleportación Cuántica

        1. Alice y Bob comparten un par de qubits entrelazados (estado Bell).
        2. Alice tiene un qubit en un estado desconocido |ψ⟩.
        3. Alice aplica puertas CNOT y Hadamard a sus qubits y mide ambos.
        4. Alice envía los resultados clásicos a Bob.
        5. Bob aplica puertas X y/o Z según los resultados y recupera |ψ⟩.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_w_state_equation(self):
        win = tk.Toplevel(self.root)
        win.title("Ecuación Estado W")
        win.geometry("600x200")
        eq = "|W⟩ = (|001⟩ + |010⟩ + |100⟩)/√3"
        label = tk.Label(win, text=eq, font=("Consolas", 18), justify='left')
        label.pack(padx=20, pady=30)

    def _show_toffoli_matrix(self):
        win = tk.Toplevel(self.root)
        win.title("Matriz de Toffoli (CCNOT)")
        win.geometry("700x250")
        eq = (
            "Toffoli (CCNOT):\n"
            "Matriz 8x8 donde solo los estados |110⟩ y |111⟩ se intercambian.\n"
            "\nEs una puerta universal para computación reversible y clásica."
        )
        label = tk.Label(win, text=eq, font=("Consolas", 15), justify='left')
        label.pack(padx=20, pady=30)

    def _show_deutsch_jozsa_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Algoritmo de Deutsch-Jozsa")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Algoritmo de Deutsch-Jozsa

        1. Inicializa n qubits en |0⟩ y un qubit auxiliar en |1⟩.
        2. Aplica Hadamard a todos los qubits.
        3. Aplica el oráculo Uf correspondiente a la función f(x).
        4. Aplica Hadamard a los primeros n qubits.
        5. Mide los primeros n qubits:
           - Si el resultado es todo ceros, f(x) es constante.
           - Si no, f(x) es balanceada.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_simon_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Algoritmo de Simon")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Algoritmo de Simon

        1. Inicializa n qubits en |0⟩ y un qubit auxiliar en |0⟩.
        2. Aplica Hadamard a los primeros n qubits.
        3. Aplica el oráculo Uf correspondiente a la función f(x).
        4. Mide el registro auxiliar y repite el proceso para obtener ecuaciones lineales.
        5. Resuelve el sistema para encontrar el string secreto s.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_cluster_state_equation(self):
        win = tk.Toplevel(self.root)
        win.title("Ecuación Estado Cluster")
        win.geometry("700x200")
        eq = "|Cluster⟩ = (|0000⟩ + |0011⟩ + |1100⟩ - |1111⟩)/2"
        label = tk.Label(win, text=eq, font=("Consolas", 16), justify='left')
        label.pack(padx=20, pady=30)

    def _show_fredkin_matrix(self):
        win = tk.Toplevel(self.root)
        win.title("Matriz de Fredkin (CSWAP)")
        win.geometry("700x250")
        eq = (
            "Fredkin (CSWAP):\n"
            "Matriz 8x8 donde los estados |110⟩ y |101⟩ se intercambian.\n"
            "\nEs una puerta universal para computación reversible."
        )
        label = tk.Label(win, text=eq, font=("Consolas", 15), justify='left')
        label.pack(padx=20, pady=30)

    def _show_bernstein_vazirani_example(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplo: Bernstein-Vazirani")
        win.geometry("700x400")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Algoritmo de Bernstein-Vazirani

        1. Inicializa n qubits en |0⟩ y un qubit auxiliar en |1⟩.
        2. Aplica Hadamard a todos los qubits.
        3. Aplica el oráculo Uf correspondiente a la función f(x) = s·x.
        4. Aplica Hadamard a los primeros n qubits.
        5. Mide los primeros n qubits: el resultado es el string secreto s.
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def _show_plot_menu(self):
        win = tk.Toplevel(self.root)
        win.title("Herramientas de Graficación y Ejemplos")
        win.geometry("400x500")
        ttk.Button(win, text="Graficar Probabilidad Qubit", command=self._plot_qubit_probability).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text="Graficar Estados de Bits", command=self._plot_bit_state).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text="Suma de Amplitudes de Qubits", command=self._sum_qubit_amplitudes).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text=self.BELL_LABEL, command=self._show_bell_state_equation).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text=self.BLOCH_LABEL, command=self._show_bloch_equation).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text="Ejemplo: Grover", command=self._show_grover_example).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text="Ejemplo: Shor", command=self._show_shor_example).pack(fill='x', padx=10, pady=10)
        ttk.Button(win, text="Ecuación Estado GHZ", command=self._show_ghz_state_equation).pack(fill='x', padx=10, pady=10)

    def _show_translator(self):
        import tkinter as tk
        from tkinter import ttk, scrolledtext, messagebox
        win = tk.Toplevel(self.root)
        win.title(self.TRANSLATOR_LABEL)
        win.geometry("900x600")
        # Selección de lenguajes
        lang_options = ["QASM", "QLang", "MiBN", "TLang"]
        frm = ttk.Frame(win)
        frm.pack(fill='x', pady=10)
        ttk.Label(frm, text="De:").pack(side='left', padx=5)
        src_lang = tk.StringVar(value=lang_options[0])
        src_combo = ttk.Combobox(frm, values=lang_options, textvariable=src_lang, width=8, state='readonly')
        src_combo.pack(side='left', padx=5)
        ttk.Label(frm, text="a").pack(side='left', padx=5)
        tgt_lang = tk.StringVar(value=lang_options[1])
        tgt_combo = ttk.Combobox(frm, values=lang_options, textvariable=tgt_lang, width=8, state='readonly')
        tgt_combo.pack(side='left', padx=5)
        # Área de texto de entrada
        input_area = scrolledtext.ScrolledText(win, height=15, font=("Consolas", 11))
        input_area.pack(fill='both', expand=True, padx=10, pady=5)
        # Botón traducir
        def translate():
            src = src_lang.get()
            tgt = tgt_lang.get()
            code = input_area.get('1.0', 'end').strip()
            if not code:
                messagebox.showwarning("Sin código", "Por favor ingrese el código fuente a traducir.")
                return
            try:
                result = self._translate_code(src, tgt, code)
            except Exception as e:
                result = f"Error en la traducción: {e}"
            output_area.config(state='normal')
            output_area.delete('1.0', 'end')
            output_area.insert('1.0', result)
            output_area.config(state='disabled')
        ttk.Button(win, text="Traducir", command=translate).pack(pady=5)
        # Área de texto de salida
        output_area = scrolledtext.ScrolledText(win, height=15, font=("Consolas", 11), state='disabled')
        output_area.pack(fill='both', expand=True, padx=10, pady=5)
        # Botón copiar
        def copy_result():
            win.clipboard_clear()
            win.clipboard_append(output_area.get('1.0', 'end').strip())
            messagebox.showinfo("Copiado", "Resultado copiado al portapapeles.")
        ttk.Button(win, text="Copiar resultado", command=copy_result).pack(pady=5)

    def _translate_code(self, src, tgt, code):
        # Traducción entre lenguajes cuánticos
        # QASM <-> QLang <-> MiBN <-> TLang
        # Se asume que los módulos de traducción existen y exponen funciones apropiadas
        if src == tgt:
            return code
        # QASM <-> QLang
        if src == "QASM" and tgt == "QLang":
            from gates.quantum_gates import qasm_to_qlang
            return qasm_to_qlang(code)
        if src == "QLang" and tgt == "QASM":
            from gates.quantum_gates import qlang_to_qasm
            return qlang_to_qasm(code)
        # QLang <-> MiBN
        if src == "QLang" and tgt == "MiBN":
            from microbin.microbinary_engine import qlang_to_mibn
            return qlang_to_mibn(code)
        if src == "MiBN" and tgt == "QLang":
            from microbin.microbinary_engine import mibn_to_qlang
            return mibn_to_qlang(code)
        # QLang <-> TLang
        if src == "QLang" and tgt == "TLang":
            from tlang.tlang_translator import qlang_to_tlang
            return qlang_to_tlang(code)
        if src == "TLang" and tgt == "QLang":
            from tlang.tlang_translator import tlang_to_qlang
            return tlang_to_qlang(code)
        # QASM <-> MiBN
        if src == "QASM" and tgt == "MiBN":
            from gates.quantum_gates import qasm_to_qlang
            from microbin.microbinary_engine import qlang_to_mibn
            return qlang_to_mibn(qasm_to_qlang(code))
        if src == "MiBN" and tgt == "QASM":
            from microbin.microbinary_engine import mibn_to_qlang
            from gates.quantum_gates import qlang_to_qasm
            return qlang_to_qasm(mibn_to_qlang(code))
        # QASM <-> TLang
        if src == "QASM" and tgt == "TLang":
            from gates.quantum_gates import qasm_to_qlang
            from tlang.tlang_translator import qlang_to_tlang
            return qlang_to_tlang(qasm_to_qlang(code))
        if src == "TLang" and tgt == "QASM":
            from tlang.tlang_translator import tlang_to_qlang
            from gates.quantum_gates import qlang_to_qasm
            return qlang_to_qasm(tlang_to_qlang(code))
        # MiBN <-> TLang
        if src == "MiBN" and tgt == "TLang":
            from microbin.microbinary_engine import mibn_to_qlang
            from tlang.tlang_translator import qlang_to_tlang
            return qlang_to_tlang(mibn_to_qlang(code))
        if src == "TLang" and tgt == "MiBN":
            from tlang.tlang_translator import tlang_to_qlang
            from microbin.microbinary_engine import qlang_to_mibn
            return qlang_to_mibn(tlang_to_qlang(code))
        return "Traducción no soportada para esta combinación."

    def _show_noise_simulation(self):
        win = tk.Toplevel(self.root)
        win.title("Simulación Avanzada de Ruido Cuántico")
        win.geometry("900x700")
        
        # Configuración del marco principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel de control
        control_frame = ttk.LabelFrame(main_frame, text="Configuración de Ruido")
        control_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # Selección de qubits
        ttk.Label(control_frame, text="Qubits Objetivo:").pack(pady=5)
        qubit_list = tk.Listbox(control_frame, selectmode=tk.MULTIPLE, height=6)
        qubit_list.pack(fill='x', padx=5, pady=5)
        for q in qubits:
            qubit_list.insert('end', q)
            
        # Tipo de ruido
        ttk.Label(control_frame, text="Canal de Ruido:").pack(pady=5)
        noise_type = tk.StringVar(value="Depolarizante")
        noise_types = {
            "Depolarizante": "Mezcla el estado con el estado máximamente mezclado",
            "Bit-flip": "Invierte el estado del qubit con probabilidad p",
            "Phase-flip": "Cambia la fase del qubit con probabilidad p",
            "Amplitude Damping": "Simula pérdida de energía al ambiente",
            "Phase Damping": "Simula pérdida de coherencia de fase"
        }
        
        for noise, desc in noise_types.items():
            frame = ttk.Frame(control_frame)
            frame.pack(fill='x', padx=5)
            rb = ttk.Radiobutton(frame, text=noise, variable=noise_type, value=noise)
            rb.pack(side='left')
            self._create_tooltip(rb, desc)
            
        # Intensidad del ruido
        ttk.Label(control_frame, text="Intensidad (p):").pack(pady=5)
        p_scale = ttk.Scale(control_frame, from_=0, to=1, length=200, orient='horizontal')
        p_scale.set(0.1)
        p_scale.pack(padx=5, pady=5)
        p_label = ttk.Label(control_frame, text="0.10")
        p_label.pack()
        
        def update_p_label(*args):
            p_label.config(text=f"{p_scale.get():.2f}")
        p_scale.config(command=update_p_label)
        
        # Panel de visualización
        vis_frame = ttk.LabelFrame(main_frame, text="Visualización del Efecto")
        vis_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Figura para la esfera de Bloch
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.Figure(figsize=(6, 6))
        canvas = FigureCanvasTkAgg(fig, vis_frame)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        ax = fig.add_subplot(111, projection='3d')
        
        def draw_bloch_sphere():
            ax.clear()
            # Dibujar esfera de Bloch base
            u = np.linspace(0, 2*np.pi, 100)
            v = np.linspace(0, np.pi, 100)
            x = np.outer(np.cos(u), np.sin(v))
            y = np.outer(np.sin(u), np.sin(v))
            z = np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_surface(x, y, z, alpha=0.1, color='b')
            
            # Ejes y etiquetas
            ax.plot([-1,1], [0,0], [0,0], 'k-', alpha=0.5, label='x')
            ax.plot([0,0], [-1,1], [0,0], 'k-', alpha=0.5, label='y')
            ax.plot([0,0], [0,0], [-1,1], 'k-', alpha=0.5, label='z')
            ax.text(1.1, 0, 0, '|+⟩')
            ax.text(-1.1, 0, 0, '|-⟩')
            ax.text(0, 0, 1.1, '|0⟩')
            ax.text(0, 0, -1.1, '|1⟩')
            
            # Configuración de la vista
            ax.set_box_aspect([1,1,1])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.view_init(elev=20, azim=45)
            
            canvas.draw()
            
        def update_visualization(*args):
            selection = qubit_list.curselection()
            if not selection:
                return
                
            ax.clear()
            draw_bloch_sphere()
            
            # Dibujar estados antes y después del ruido
            for idx in selection:
                qubit_name = qubit_list.get(idx)
                # Estado original
                coords = qubits[qubit_name].get_bloch_coords()
                ax.quiver(0, 0, 0, coords['x'], coords['y'], coords['z'],
                         color='g', arrow_length_ratio=0.15, label='Original')
                
                # Estado con ruido
                noisy_coords = self._simulate_noise_bloch(qubit_name, 
                                                        noise_type.get(),
                                                        p_scale.get())
                ax.quiver(0, 0, 0, noisy_coords[0], noisy_coords[1], noisy_coords[2],
                         color='r', arrow_length_ratio=0.15, label='Con ruido')
            
            ax.legend()
            canvas.draw()
        
        # Controles de simulación
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x', padx=5, pady=10)
        
        def apply_noise():
            selection = qubit_list.curselection()
            if not selection:
                messagebox.showwarning("Ruido", "Seleccione al menos un qubit.")
                return
                
            p = p_scale.get()
            noise = noise_type.get()
            
            for idx in selection:
                q = qubit_list.get(idx)
                state = qubits[q].state
                
                if noise == "Depolarizante":
                    # Canal depolarizante: ρ' = (1-p)ρ + p*I/2
                    rho = np.outer(state, state.conj())
                    rho = (1-p)*rho + p*np.eye(2)/2
                    vals, vecs = np.linalg.eigh(rho)
                    new_state = vecs[:, np.argmax(vals)]
                    qubits[q].state = new_state / np.linalg.norm(new_state)
                    
                elif noise == "Bit-flip":
                    # Canal bit-flip: ρ' = (1-p)ρ + p*XρX
                    rho = np.outer(state, state.conj())
                    X = np.array([[0,1],[1,0]])
                    rho = (1-p)*rho + p*X@rho@X
                    vals, vecs = np.linalg.eigh(rho)
                    new_state = vecs[:, np.argmax(vals)]
                    qubits[q].state = new_state / np.linalg.norm(new_state)
                    
                elif noise == "Phase-flip":
                    # Canal de fase: ρ' = (1-p)ρ + p*ZρZ
                    rho = np.outer(state, state.conj())
                    Z = np.array([[1,0],[0,-1]])
                    rho = (1-p)*rho + p*Z@rho@Z
                    vals, vecs = np.linalg.eigh(rho)
                    new_state = vecs[:, np.argmax(vals)]
                    qubits[q].state = new_state / np.linalg.norm(new_state)
                    
                elif noise == "Amplitude Damping":
                    # Canal de amortiguamiento: Kraus operators
                    K0 = np.array([[1,0],[0,np.sqrt(1-p)]])
                    K1 = np.array([[0,np.sqrt(p)],[0,0]])
                    rho = np.outer(state, state.conj())
                    rho = K0@rho@K0.conj().T + K1@rho@K1.conj().T
                    vals, vecs = np.linalg.eigh(rho)
                    new_state = vecs[:, np.argmax(vals)]
                    qubits[q].state = new_state / np.linalg.norm(new_state)
                    
                elif noise == "Phase Damping":
                    # Canal de decoherencia de fase: Kraus operators
                    K0 = np.array([[1,0],[0,np.sqrt(1-p)]])
                    K1 = np.array([[0,0],[0,np.sqrt(p)]])
                    rho = np.outer(state, state.conj())
                    rho = K0@rho@K0.conj().T + K1@rho@K1.conj().T
                    vals, vecs = np.linalg.eigh(rho)
                    new_state = vecs[:, np.argmax(vals)]
                    qubits[q].state = new_state / np.linalg.norm(new_state)
            
            messagebox.showinfo("Ruido", f"Canal de ruido {noise} aplicado con p={p:.2f}")
            self._update_qubit_lists()
            update_visualization()
        
        ttk.Button(btn_frame, text="Aplicar Ruido",
                  command=apply_noise).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Vista",
                  command=update_visualization).pack(side='left', padx=5)
        
        # Inicializar visualización
        draw_bloch_sphere()
        
        # Configurar callbacks
        noise_type.trace('w', update_visualization)
        p_scale.config(command=lambda x: [update_p_label(), update_visualization()])

    def _show_diagnostic(self):
        win = tk.Toplevel(self.root)
        win.title(self.DIAGNOSTIC_LABEL)
        win.geometry("900x700")
        ttk.Label(win, text="Diagnóstico Avanzado del Sistema Cuántico", 
                 font=("Arial", 16, "bold"), foreground="#0072bd").pack(pady=10)
        
        # Marco principal con diseño de 2 columnas
        main_frame = ttk.Frame(win)
        main_frame.pack(fill='both', expand=True, padx=10)
        
        # Panel izquierdo con métricas
        metrics_frame = ttk.LabelFrame(main_frame, text="Métricas del Sistema")
        metrics_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        text = scrolledtext.ScrolledText(metrics_frame, height=30, 
                                       font=("Consolas", 11), background="#f7faff")
        text.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Análisis del circuito
        from collections import Counter
        import numpy as np
        from interpreter.qlang_interpreter import qubits, circuit_operations
        
        text.insert('end', "🔍 ANÁLISIS DEL CIRCUITO\n", 'header')
        text.insert('end', "-" * 50 + "\n\n")
        
        # Estadísticas básicas
        gate_count = len(circuit_operations)
        qubit_count = len(qubits)
        text.insert('end', f"• Qubits activos: {qubit_count}\n")
        text.insert('end', f"• Profundidad del circuito: {gate_count}\n")
        
        # Distribución de puertas
        gate_types = Counter(op['gate'] for op in circuit_operations if 'gate' in op)
        text.insert('end', "\n📊 DISTRIBUCIÓN DE PUERTAS\n", 'header')
        text.insert('end', "-" * 30 + "\n")
        for g, c in gate_types.items():
            text.insert('end', f"  {g}: {c}\n")
            
        # Análisis de entrelazamiento
        text.insert('end', "\n🔗 ANÁLISIS DE ENTRELAZAMIENTO\n", 'header')
        text.insert('end', "-" * 30 + "\n")
        entangled_pairs = set()
        for q in qubits:
            ent_set = getattr(qubits[q], 'entangled_with', set())
            if ent_set:
                text.insert('end', f"  • {q} entrelazado con: {', '.join(ent_set)}\n")
                for other in ent_set:
                    pair = tuple(sorted([q, other]))
                    entangled_pairs.add(pair)
        
        # Pureza y coherencia
        text.insert('end', "\n📈 MÉTRICAS DE COHERENCIA\n", 'header')
        text.insert('end', "-" * 30 + "\n")
        for q in qubits:
            state = qubits[q].state
            rho = np.outer(state, state.conj())
            purity = np.trace(rho @ rho).real
            # Coherencia l1-norm
            coherence = np.sum(np.abs(rho - np.diag(np.diag(rho))))
            text.insert('end', f"  {q}:\n")
            text.insert('end', f"    Pureza: {purity:.4f}\n")
            text.insert('end', f"    Coherencia: {coherence:.4f}\n")
        
        # Panel derecho con recomendaciones
        rec_frame = ttk.LabelFrame(main_frame, text="Recomendaciones")
        rec_frame.pack(side='right', fill='both', padx=5, pady=5)
        
        rec_text = scrolledtext.ScrolledText(rec_frame, height=30, width=40,
                                           font=("Segoe UI", 10), background="#fff7e6")
        rec_text.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Generar recomendaciones basadas en métricas
        rec_text.insert('end', "🎯 RECOMENDACIONES\n\n", 'header')
        
        if gate_count > 20:
            rec_text.insert('end', "⚠️ Circuito Profundo:\n")
            rec_text.insert('end', "• Considere optimizar el circuito\n")
            rec_text.insert('end', "• Evalúe usar puertas compuestas\n\n")
            
        if not entangled_pairs and gate_count > 5:
            rec_text.insert('end', "💡 Entrelazamiento:\n")
            rec_text.insert('end', "• El circuito no muestra entrelazamiento\n")
            rec_text.insert('end', "• Evalúe usar puertas CNOT o CZ\n\n")
            
        # Evaluar coherencia general
        avg_coherence = np.mean([np.sum(np.abs(np.outer(qubits[q].state, qubits[q].state.conj()) 
                                             - np.diag(np.diag(np.outer(qubits[q].state, qubits[q].state.conj())))))
                               for q in qubits])
        if avg_coherence < 0.5:
            rec_text.insert('end', "📉 Baja Coherencia:\n")
            rec_text.insert('end', "• Revise fuentes de decoherencia\n")
            rec_text.insert('end', "• Considere técnicas de corrección\n\n")
        
        # Configurar tags para estilos
        text.tag_configure('header', foreground='#0072bd', font=("Segoe UI", 11, "bold"))
        rec_text.tag_configure('header', foreground='#d95319', font=("Segoe UI", 11, "bold"))
        
        # Barra de herramientas
        toolbar = ttk.Frame(win)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="Exportar Diagnóstico",
                  command=lambda: self._export_diagnostic(text.get('1.0', 'end'))).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Actualizar",
                  command=lambda: self._show_diagnostic()).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Cerrar",
                  command=win.destroy).pack(side='right', padx=5)

    def _show_optimizer(self):
        win = tk.Toplevel(self.root)
        win.title(self.OPTIMIZER_LABEL)
        win.geometry("850x550")
        ttk.Label(win, text="Optimización de Circuito Cuántico", font=("Arial", 16, "bold"), foreground="#0072bd").pack(pady=10)
        from interpreter.qlang_interpreter import circuit_operations
        from gates.quantum_gates import optimize_circuit
        import copy
        orig_ops = copy.deepcopy(circuit_operations)
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        text = scrolledtext.ScrolledText(frame, height=18, font=("Consolas", 12), background="#f7faff")
        text.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        sidebar = ttk.Frame(frame)
        sidebar.pack(side='right', fill='y', padx=5)
        ttk.Label(sidebar, text="Opciones", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(sidebar, text="Optimizar Ahora", style="Accent.TButton", command=lambda: run_optimization()).pack(pady=10, fill='x')
        ttk.Button(sidebar, text="Cerrar", command=win.destroy).pack(pady=10, fill='x')
        def run_optimization():
            optimized, report = optimize_circuit(orig_ops)
            text.delete('1.0', 'end')
            text.insert('end', "Reporte de Optimización:\n\n")
            text.insert('end', report)
            text.insert('end', f"\n\nAntes: {len(orig_ops)} puertas\nDespués: {len(optimized)} puertas\n")
            if len(optimized) < len(orig_ops):
                text.insert('end', f"Reducción: {len(orig_ops)-len(optimized)} puertas\n")
            else:
                text.insert('end', "No se logró reducir el circuito.\n")
        # Ayuda contextual
        help_frame = ttk.LabelFrame(win, text="¿Cómo funciona la optimización?")
        help_frame.pack(fill='x', padx=10, pady=5)
        help_text = "El optimizador busca puertas redundantes, reduce la profundidad y mejora la robustez del circuito.\nRevisa el reporte para ver los cambios y sugerencias."
        ttk.Label(help_frame, text=help_text, font=("Arial", 10), foreground="#555").pack(anchor='w', padx=5, pady=2)

    def _show_hardware_sim(self):
        win = tk.Toplevel(self.root)
        win.title(self.HARDWARE_LABEL)
        win.geometry("800x600")
        ttk.Label(win, text="Simulación de Hardware Real", font=("Arial", 16, "bold"), foreground="#a2142f").pack(pady=10)
        ttk.Label(win, text="Selecciona backend simulado:").pack(pady=5)
        backends = ["IBM Q Falcon", "IonQ Harmony", "Rigetti Aspen", "Google Sycamore"]
        backend_var = tk.StringVar(value=backends[0])
        ttk.Combobox(win, values=backends, textvariable=backend_var, state='readonly').pack(pady=5)
        ttk.Label(win, text="Restricciones y errores típicos:").pack(pady=5)
        info = scrolledtext.ScrolledText(win, height=7, font=("Consolas", 11), background="#fff7f7")
        info.pack(fill='x', padx=10, pady=5)
        def show_backend_info(*args):
            b = backend_var.get()
            if "IBM" in b:
                msg = "Conectividad limitada, error de puerta ~0.01, decoherencia T1~100us."
            elif "IonQ" in b:
                msg = "Conectividad total, error de puerta ~0.02, tiempos de puerta más lentos."
            elif "Rigetti" in b:
                msg = "Conectividad parcial, error de puerta ~0.03, decoherencia T1~80us."
            elif "Google" in b:
                msg = "Conectividad cuadrícula, error de puerta ~0.005, decoherencia T1~120us."
            else:
                msg = "Backend no reconocido."
            info.delete('1.0', 'end')
            info.insert('end', msg)
        backend_var.trace('w', show_backend_info)
        show_backend_info()
        ttk.Button(win, text="Simular", style="Accent.TButton", command=lambda: messagebox.showinfo("Hardware", f"Simulación de hardware '{backend_var.get()}' aplicada.\nSe mostrarán restricciones y errores típicos.")).pack(pady=10)
        # Topología visual
        topo_frame = ttk.LabelFrame(win, text="Topología del Hardware")
        topo_frame.pack(fill='both', expand=True, padx=10, pady=10)
        canvas = tk.Canvas(topo_frame, bg="#f9f9f9", height=200)
        canvas.pack(fill='both', expand=True)
        def draw_topology():
            canvas.delete('all')
            b = backend_var.get()
            if "IBM" in b or "Rigetti" in b:
                # Lineal
                for i in range(5):
                    x = 60 + i*120
                    y = 100
                    canvas.create_oval(x-20, y-20, x+20, y+20, fill="#0072bd", outline="#333", width=2)
                    canvas.create_text(x, y, text=f"Q{i}", fill="white", font=("Arial", 12, "bold"))
                    if i > 0:
                        canvas.create_line(x-100, y, x-20, y, fill="#a2142f", width=3)
            elif "IonQ" in b:
                # Totalmente conectado
                coords = [(120,100),(240,60),(360,100),(240,140)]
                for i, (x,y) in enumerate(coords):
                    canvas.create_oval(x-20, y-20, x+20, y+20, fill="#0072bd", outline="#333", width=2)
                    canvas.create_text(x, y, text=f"Q{i}", fill="white", font=("Arial", 12, "bold"))
                for i in range(4):
                    for j in range(i+1,4):
                        x1,y1 = coords[i]
                        x2,y2 = coords[j]
                        canvas.create_line(x1, y1, x2, y2, fill="#a2142f", width=2)
            elif "Google" in b:
                # Cuadrícula
                for i in range(2):
                    for j in range(3):
                        x = 120 + j*120
                        y = 70 + i*100
                        canvas.create_oval(x-20, y-20, x+20, y+20, fill="#0072bd", outline="#333", width=2)
                        canvas.create_text(x, y, text=f"Q{i*3+j}", fill="white", font=("Arial", 12, "bold"))
                for i in range(2):
                    for j in range(2):
                        x1 = 120 + j*120
                        y1 = 70 + i*100
                        x2 = x1 + 120
                        y2 = y1
                        canvas.create_line(x1, y1, x2, y2, fill="#a2142f", width=2)
                for j in range(3):
                    x = 120 + j*120
                    y1 = 70
                    y2 = 170
                    canvas.create_line(x, y1, x, y2, fill="#a2142f", width=2)
        backend_var.trace('w', lambda *a: draw_topology())
        draw_topology()
        # Ayuda contextual
        help_frame = ttk.LabelFrame(win, text="¿Qué simula este panel?")
        help_frame.pack(fill='x', padx=10, pady=5)
        help_text = "Simula restricciones reales de hardware, topología y errores típicos. Útil para preparar circuitos para hardware físico."
        ttk.Label(help_frame, text=help_text, font=("Arial", 10), foreground="#555").pack(anchor='w', padx=5, pady=2)

    def _show_advanced_metrics(self):
        win = tk.Toplevel(self.root)
        win.title(self.ADV_METRICS_LABEL)
        win.geometry("900x700")
        ttk.Label(win, text="Métricas Avanzadas Cuánticas", font=("Arial", 16, "bold"), foreground="#228B22").pack(pady=10)
        from interpreter.qlang_interpreter import qubits
        import numpy as np
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        text = scrolledtext.ScrolledText(frame, height=25, font=("Consolas", 12), background="#f7fff7")
        text.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        sidebar = ttk.Frame(frame)
        sidebar.pack(side='right', fill='y', padx=5)
        ttk.Label(sidebar, text="Opciones", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(sidebar, text="Cerrar", command=win.destroy).pack(pady=10, fill='x')
        qubit_names = list(qubits.keys())
        # Entrelazamiento (simple: pares con correlación)
        text.insert('end', "Entrelazamiento Global:\n")
        entangled_pairs = set()
        for q in qubit_names:
            ent_set = getattr(qubits[q], 'entangled_with', set())
            for other in ent_set:
                pair = tuple(sorted([q, other]))
                entangled_pairs.add(pair)
        text.insert('end', f"  Pares entrelazados: {len(entangled_pairs)}\n")
        # Entropía de von Neumann
        text.insert('end', "\nEntropía de von Neumann (por qubit):\n")
        for q in qubit_names:
            state = qubits[q].state
            rho = np.outer(state, state.conj())
            eigs = np.linalg.eigvalsh(rho)
            entropy = -sum(e*np.log2(e) for e in eigs if e > 1e-10)
            text.insert('end', f"  {q}: {entropy:.4f}\n")
        # Coherencia l1
        text.insert('end', "\nCoherencia l1 (por qubit):\n")
        for q in qubit_names:
            state = qubits[q].state
            rho = np.outer(state, state.conj())
            coh = np.sum(np.abs(rho - np.diag(np.diag(rho))))
            text.insert('end', f"  {q}: {coh:.4f}\n")
        # Evolución temporal (demo: muestra estado actual)
        text.insert('end', "\nEvolución temporal (estado actual):\n")
        for q in qubit_names:
            state = qubits[q].state
            text.insert('end', f"  {q}: |0⟩={state[0]:.3f}, |1⟩={state[1]:.3f}\n")
        text.configure(state='disabled')
        # Ayuda contextual
        help_frame = ttk.LabelFrame(win, text="¿Qué muestran estas métricas?")
        help_frame.pack(fill='x', padx=10, pady=5)
        help_text = "Incluye métricas de entrelazamiento, entropía, coherencia y evolución temporal. Útil para análisis avanzado de circuitos."
        ttk.Label(help_frame, text=help_text, font=("Arial", 10), foreground="#555").pack(anchor='w', padx=5, pady=2)

    def _show_quantum_assistant(self):
        win = tk.Toplevel(self.root)
        win.title(self.ASSISTANT_LABEL)
        win.geometry("700x500")
        ttk.Label(win, text="Asistente Cuántico (IA)", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(win, text="Haz preguntas sobre tu circuito, recibe sugerencias y explicaciones (demo)", foreground='gray').pack(pady=10)
        question = tk.StringVar()
        ttk.Entry(win, textvariable=question, width=60).pack(pady=10)
        ttk.Button(win, text="Preguntar", command=lambda: messagebox.showinfo("Asistente", "Respuesta inteligente generada (demo).")) .pack(pady=10)

    def _show_circuit_history(self):
        win = tk.Toplevel(self.root)
        win.title("Historial de Circuitos")
        win.geometry("700x500")
        if not hasattr(self, '_circuit_snapshots') or not self._circuit_snapshots:
            ttk.Label(win, text="No hay historial disponible.").pack(pady=20)
            return
        from interpreter.qlang_interpreter import circuit_operations
        listbox = tk.Listbox(win, height=10)
        for i, snap in enumerate(self._circuit_snapshots):
            listbox.insert(tk.END, f"Versión {i+1} ({len(snap)} operaciones)")
        listbox.pack(pady=10, fill='x')
        def restore():
            idx = listbox.curselection()
            if not idx:
                return
            circuit_operations[:] = self._circuit_snapshots[idx[0]]
            self.add_to_history(f"Circuito restaurado a versión {idx[0]+1}")
            messagebox.showinfo("Restaurado", f"Circuito restaurado a versión {idx[0]+1}")
        ttk.Button(win, text="Restaurar Versión", command=restore).pack(pady=5)

    def _show_decoherence_sim(self):
        win = tk.Toplevel(self.root)
        win.title("Simulación de Decoherencia Temporal")
        win.geometry("700x500")
        ttk.Label(win, text="Visualiza cómo el estado de los qubits se degrada con el tiempo.", font=("Arial", 12)).pack(pady=10)
        ttk.Label(win, text="(Demo: la lógica avanzada puede conectarse aquí)", foreground='gray').pack(pady=5)
        # Aquí se puede agregar una animación temporal de la esfera de Bloch

    def _show_ask_simulator(self):
        win = tk.Toplevel(self.root)
        win.title("Pregúntale al Simulador")
        win.geometry("700x400")
        ttk.Label(win, text="Escribe una pregunta sobre tu circuito:").pack(pady=5)
        question = tk.StringVar()
        ttk.Entry(win, textvariable=question, width=60).pack(pady=10)
        def answer():
            q = question.get().lower()
            if "entrelazamiento" in q:
                msg = "El entrelazamiento es una correlación cuántica. Puedes analizarlo en el menú 'Ver > Entrelazamiento'."
            elif "fidelidad" in q:
                msg = "La fidelidad mide la similitud entre dos estados cuánticos."
            elif "optimizar" in q:
                msg = "Puedes optimizar el circuito desde el menú Exclusivo PRO."
            else:
                msg = "Consulta la documentación o el tutorial para más información."
            messagebox.showinfo("Respuesta del Simulador", msg)
        ttk.Button(win, text="Preguntar", command=answer).pack(pady=10)

    def _show_premium_export(self):
        win = tk.Toplevel(self.root)
        win.title(self.PREMIUM_EXPORT_LABEL)
        win.geometry("700x500")
        ttk.Label(win, text="Exportación Premium de Circuitos", font=("Arial", 15, "bold"), foreground="#0072bd").pack(pady=10)
        ttk.Label(win, text="Exporta tu circuito a formatos avanzados:").pack(pady=5)
        formats = ["Q#", "OpenQASM 3.0", "QuTiP (Python)", "PDF (visual)"]
        format_var = tk.StringVar(value=formats[0])
        ttk.Combobox(win, values=formats, textvariable=format_var, state='readonly').pack(pady=5)
        ttk.Label(win, text="Nombre de archivo:").pack(pady=5)
        filename_entry = ttk.Entry(win, width=40)
        filename_entry.insert(0, "circuit_export")
        filename_entry.pack(pady=5)
        result_text = scrolledtext.ScrolledText(win, height=15, font=("Consolas", 11), background="#f7faff")
        result_text.pack(expand=True, fill='both', padx=10, pady=10)
        def do_export():
            fmt = format_var.get()
            fname = filename_entry.get()
            from interpreter.qlang_interpreter import circuit_operations
            try:
                if fmt == "Q#":
                    from gates.quantum_gates import export_qsharp
                    code = export_qsharp(circuit_operations)
                    ext = ".qs"
                elif fmt == "OpenQASM 3.0":
                    from gates.quantum_gates import get_circuit_qasm3
                    code = get_circuit_qasm3(circuit_operations)
                    ext = ".qasm"
                elif fmt == "QuTiP (Python)":
                    from gates.quantum_gates import export_qutip
                    code = export_qutip(circuit_operations)
                    ext = ".py"
                elif fmt == "PDF (visual)":
                    from visualizer.circuit_visualizer import save_circuit_pdf
                    path = fname + ".pdf"
                    save_circuit_pdf(circuit_operations, path)
                    result_text.delete('1.0', 'end')
                    result_text.insert('end', f"Circuito exportado como PDF en: {path}\n")
                    return
                else:
                    code = "Formato no soportado."
                    ext = ""
                path = fname + ext
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                result_text.delete('1.0', 'end')
                result_text.insert('end', f"Circuito exportado en: {path}\n\n---\n{code[:1000]}\n...")
            except Exception as e:
                result_text.delete('1.0', 'end')
                result_text.insert('end', f"Error al exportar: {e}\n")
        ttk.Button(win, text="Exportar", style="Accent.TButton", command=do_export).pack(pady=10)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)
        # Ayuda contextual
        help_frame = ttk.LabelFrame(win, text="¿Qué hace la exportación premium?")
        help_frame.pack(fill='x', padx=10, pady=5)
        help_text = "Permite exportar el circuito a lenguajes y formatos profesionales para simuladores, hardware real o documentación."
        ttk.Label(help_frame, text=help_text, font=("Arial", 10), foreground="#555").pack(anchor='w', padx=5, pady=2)

    def _show_dynamic_decoherence(self):
        import time
        win = tk.Toplevel(self.root)
        win.title("Decoherencia Dinámica")
        win.geometry("700x600")
        ttk.Label(win, text="Animación de decoherencia en la esfera de Bloch", font=("Arial", 13)).pack(pady=10)
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        import numpy as np
        fig = plt.Figure(figsize=(5, 5))
        ax = fig.add_subplot(111, projection='3d')
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        qubit_names = list(qubits.keys())
        if not qubit_names:
            ttk.Label(win, text="No hay qubits para simular.").pack(pady=20)
            return
        q = qubit_names[0]
        state = qubits[q].state.copy()
        steps = 30
        for t in range(steps):
            ax.clear()
            # Esfera
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 100)
            x = np.outer(np.cos(u), np.sin(v))
            y = np.outer(np.sin(u), np.sin(v))
            z = np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_surface(x, y, z, alpha=0.1, color='b')
            # Estado con decoherencia
            p = t / steps
            rho = np.outer(state, state.conj())
            K0 = np.array([[1,0],[0,np.sqrt(1-p)]])
            K1 = np.array([[0,np.sqrt(p)],[0,0]])
            rho = K0@rho@K0.conj().T + K1@rho@K1.conj().T
            vals, vecs = np.linalg.eigh(rho)
            new_state = vecs[:, np.argmax(vals)]
            coords = {
                'x': float(np.real(new_state.conj().T @ np.array([[0,1],[1,0]]) @ new_state)),
                'y': float(np.real(new_state.conj().T @ np.array([[0,-1j],[1j,0]]) @ new_state)),
                'z': float(np.real(new_state.conj().T @ np.array([[1,0],[0,-1]]) @ new_state)),
            }
            ax.quiver(0, 0, 0, coords['x'], coords['y'], coords['z'], color='r', linewidth=3)
            ax.set_xlim([-1,1])
            ax.set_ylim([-1,1])
            ax.set_zlim([-1,1])
            ax.set_title(f"Decoherencia t={t}")
            canvas.draw()
            win.update()
            time.sleep(0.08)
        ttk.Label(win, text="Fin de la animación.").pack(pady=10)

    def _show_global_metrics(self):
        win = tk.Toplevel(self.root)
        win.title("Métricas Globales Avanzadas")
        win.geometry("700x500")
        from interpreter.qlang_interpreter import qubits
        import numpy as np
        text = scrolledtext.ScrolledText(win, height=25, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        qubit_names = list(qubits.keys())
        if len(qubit_names) < 2:
            text.insert('end', "Se requieren al menos dos qubits para métricas globales.\n")
            return
        # Distancia de traza entre todos los pares
        text.insert('end', "Distancia de Traza entre pares:\n")
        for i in range(len(qubit_names)):
            for j in range(i+1, len(qubit_names)):
                q1, q2 = qubit_names[i], qubit_names[j]
                rho1 = np.outer(qubits[q1].state, qubits[q1].state.conj())
                rho2 = np.outer(qubits[q2].state, qubits[q2].state.conj())
                diff = rho1 - rho2
                tr_dist = 0.5 * np.trace(np.sqrt(diff.conj().T @ diff)).real
                text.insert('end', f"{q1} vs {q2}: {tr_dist:.4f}\n")
        # Participación cuántica (IPR)
        text.insert('end', "\nÍndice de Participación Cuántica (IPR):\n")
        for q in qubit_names:
            state = qubits[q].state
            ipr = 1.0 / np.sum(np.abs(state)**4)
            text.insert('end', f"{q}: {ipr:.4f}\n")
        text.configure(state='disabled')

    def show_multi_qubit_visualization(self):
        # ...código de multi_qubit_visualization...
        from interpreter.qlang_interpreter import qubits
        import matplotlib.pyplot as plt
        import numpy as np
        win = tk.Toplevel(self.root)
        win.title("Visualización Multi-Qubit")
        win.geometry("900x700")
        qubit_names = list(qubits.keys())
        if len(qubit_names) < 2:
            ttk.Label(win, text="Se requieren al menos dos qubits.", foreground='red').pack(pady=30)
            return
        text = scrolledtext.ScrolledText(win, height=6)
        text.pack(fill='x', padx=10, pady=5)
        text.insert('end', f"Qubits activos: {', '.join(qubit_names)}\n")
        text.configure(state='disabled')
        states = [qubits[q].state for q in qubit_names]
        state = states[0]
        for s in states[1:]:
            state = np.kron(state, s)
        rho = np.outer(state, state.conj())
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(np.real(rho), cmap='RdYlBu')
        fig.colorbar(im)
        ax.set_title('Matriz de Densidad Global (parte real)')
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def show_temporal_evolution(self):
        # ...código de temporal_evolution...
        from interpreter.qlang_interpreter import qubits
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.animation import FuncAnimation
        win = tk.Toplevel(self.root)
        win.title("Evolución Temporal del Estado")
        win.geometry("800x700")
        qubit_names = list(qubits.keys())
        if not qubit_names:
            ttk.Label(win, text="No hay qubits para animar.", foreground='red').pack(pady=30)
            return
        q = qubit_names[0]
        states = [qubits[q].state.copy()]
        H = 1/np.sqrt(2) * np.array([[1, 1], [1, -1]])
        for _ in range(10):
            new_state = H @ states[-1]
            new_state /= np.linalg.norm(new_state)
            states.append(new_state)
        fig = plt.Figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        def update(i):
            ax.clear()
            coords = [np.real(states[i][0]), np.imag(states[i][0]), np.real(states[i][1])]
            ax.bar3d([0], [0], [0], [1], [1], [coords[0]], color='#0072bd')
            ax.set_title(f'Paso {i}')
        FuncAnimation(fig, update, frames=len(states), interval=700, repeat=False)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        ttk.Label(win, text="(Demo: animación de evolución en la esfera de Bloch)").pack(pady=5)

    def show_hardware_simulation(self):
        self._show_hardware_sim()

    def show_quantum_algorithms(self):
        win = tk.Toplevel(self.root)
        win.title("Panel de Algoritmos Cuánticos")
        win.geometry("700x500")
        notebook = ttk.Notebook(win)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        frame_grover = ttk.Frame(notebook)
        notebook.add(frame_grover, text="Grover")
        self._show_grover_example = getattr(self, '_show_grover_example', None)
        if self._show_grover_example:
            btn = ttk.Button(frame_grover, text="Ver Ejemplo Grover", command=self._show_grover_example)
            btn.pack(pady=20)
        frame_shor = ttk.Frame(notebook)
        notebook.add(frame_shor, text="Shor")
        self._show_shor_example = getattr(self, '_show_shor_example', None)
        if self._show_shor_example:
            btn = ttk.Button(frame_shor, text="Ver Ejemplo Shor", command=self._show_shor_example)
            btn.pack(pady=20)
        frame_tele = ttk.Frame(notebook)
        notebook.add(frame_tele, text="Teleportación")
        self._show_teleportation_example = getattr(self, '_show_teleportation_example', None)
        if self._show_teleportation_example:
            btn = ttk.Button(frame_tele, text="Ver Ejemplo Teleportación", command=self._show_teleportation_example)
            btn.pack(pady=20)

    def show_qiskit_integration(self):
        win = tk.Toplevel(self.root)
        win.title("Integración con Qiskit")
        win.geometry("800x600")
        try:
            from interpreter.qlang_interpreter import circuit_operations
            from gates.quantum_gates import get_circuit_qiskit
            code = get_circuit_qiskit(circuit_operations)
        except Exception as e:
            code = f"Error al generar código Qiskit:\n{e}"
        text = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        text.insert('1.0', code)
        text.configure(state='normal')
        ttk.Button(win, text="Copiar Código", command=lambda: self.root.clipboard_append(code)).pack(pady=10)

    def show_state_comparison(self):
        from interpreter.qlang_interpreter import qubits
        import numpy as np
        win = tk.Toplevel(self.root)
        win.title("Comparación de Estados Cuánticos")
        win.geometry("600x400")
        qubit_names = list(qubits.keys())
        if len(qubit_names) < 2:
            ttk.Label(win, text="Se requieren al menos dos qubits.", foreground='red').pack(pady=30)
            return
        var1 = tk.StringVar(value=qubit_names[0])
        var2 = tk.StringVar(value=qubit_names[1])
        frame = ttk.Frame(win)
        frame.pack(pady=20)
        ttk.Label(frame, text="Qubit 1:").grid(row=0, column=0, padx=5)
        ttk.Combobox(frame, values=qubit_names, textvariable=var1, state='readonly').grid(row=0, column=1)
        ttk.Label(frame, text="Qubit 2:").grid(row=1, column=0, padx=5)
        ttk.Combobox(frame, values=qubit_names, textvariable=var2, state='readonly').grid(row=1, column=1)
        result = tk.StringVar()
        def compare():
            q1, q2 = var1.get(), var2.get()
            state1, state2 = qubits[q1].state, qubits[q2].state
            fidelity = abs(np.vdot(state1, state2)) ** 2
            diff = np.linalg.norm(state1 - state2)
            result.set(f"Fidelidad: {fidelity:.4f}\nDiferencia Euclídea: {diff:.4f}")
        ttk.Button(frame, text="Comparar", command=compare).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Label(frame, textvariable=result, font=("Consolas", 12)).grid(row=3, column=0, columnspan=2, pady=10)

    def show_quantum_ml_examples(self):
        win = tk.Toplevel(self.root)
        win.title("Ejemplos de Machine Learning Cuántico")
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Clasificador Cuántico (Quantum SVM)

        1. Codifica datos clásicos en estados cuánticos usando puertas parametrizadas.
        2. Aplica un circuito variacional para separar clases.
        3. Mide los qubits y asigna la clase según el resultado.
        4. Optimiza los parámetros usando un optimizador clásico.

        (Demo: la integración con Qiskit/QuTiP puede agregarse aquí)
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def show_hybrid_circuits(self):
        win = tk.Toplevel(self.root)
        win.title("Circuitos Híbridos Cuántico-Clásicos")
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        example = """
        Ejemplo: Circuito Híbrido

        1. Un circuito cuántico calcula una función f(x).
        2. El resultado se pasa a un algoritmo clásico para post-procesamiento.
        3. El resultado clásico puede modificar el circuito cuántico en un ciclo iterativo.

        (Demo: integración con microbin/microbinary_engine)
        """
        text.insert('1.0', example)
        text.configure(state='disabled')

    def show_ai_explanations(self):
        win = tk.Toplevel(self.root)
        win.title("Explicaciones con IA")
        win.geometry("700x500")
        text = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        explanation = """
        Explicación Automática (IA):

        El simulador puede analizar el circuito y explicar:
        - ¿Qué hace el circuito?
        - ¿Qué tipo de entrelazamiento hay?
        - ¿Qué algoritmos cuánticos se están usando?
        - ¿Qué errores o mejoras se pueden sugerir?

        (Demo: integración futura con modelos de lenguaje)
        """
        text.insert('1.0', explanation)
        text.configure(state='disabled')

    def show_collaborative_mode(self):
        win = tk.Toplevel(self.root)
        win.title("Modo Colaborativo (Demo)")
        win.geometry("600x400")
        text = scrolledtext.ScrolledText(win, font=("Consolas", 12))
        text.pack(expand=True, fill='both', padx=10, pady=10)
        demo = """
        Modo Colaborativo (Demo):

        - Varios usuarios pueden editar el circuito en tiempo real.
        - Se pueden compartir estados y resultados.
        - (Demo: integración futura con sockets o servicios en la nube)
        """
        text.insert('1.0', demo)
        text.configure(state='disabled')

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        # Advanced Quantum Menu
        advanced_menu = tk.Menu(menu_bar, tearoff=0)
        advanced_menu.add_command(label=self.MULTI_QUBIT_VISUALIZATION, command=self.show_multi_qubit_visualization)
        advanced_menu.add_command(label=self.TEMPORAL_EVOLUTION, command=self.show_temporal_evolution)
        advanced_menu.add_command(label=self.HARDWARE_SIMULATION, command=self.show_hardware_simulation)
        advanced_menu.add_command(label=self.QUANTUM_ALGORITHMS, command=self.show_quantum_algorithms)
        advanced_menu.add_command(label=self.QISKIT_INTEGRATION, command=self.show_qiskit_integration)
        advanced_menu.add_command(label=self.STATE_COMPARISON, command=self.show_state_comparison)
        advanced_menu.add_command(label=self.QUANTUM_ML, command=self.show_quantum_ml_examples)
        advanced_menu.add_command(label=self.HYBRID_CIRCUITS, command=self.show_hybrid_circuits)
        advanced_menu.add_command(label=self.AI_EXPLANATIONS, command=self.show_ai_explanations)
        advanced_menu.add_command(label=self.COLLABORATIVE_MODE, command=self.show_collaborative_mode)
        menu_bar.add_cascade(label=self.ADVANCED_QUANTUM_LABEL, menu=advanced_menu)
        self.root.config(menu=menu_bar)

def main():
    root = tk.Tk()
    QuantumGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()