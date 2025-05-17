import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

class QuantumVisualizer:
    """
    Visualizador avanzado de circuitos cuánticos con múltiples vistas
    y animaciones interactivas.
    """
    
    def __init__(self):
        self.operations = []
        self.fig = None
        self.ax = None
        self.style = {
            'modern': {
                'single_gate_color': '#3498db',
                'control_color': '#2c3e50',
                'line_color': '#95a5a6',
                'text_color': '#2c3e50',
                'background': '#f8f9fa'
            },
            'classic': {
                'single_gate_color': 'white',
                'control_color': 'black',
                'line_color': 'black',
                'text_color': 'black',
                'background': 'white'
            }
        }
        self.current_style = 'modern'
        
    def set_style(self, style_name: str) -> None:
        """
        Configura el estilo de visualización.
        
        Args:
            style_name: Nombre del estilo ('modern' o 'classic')
        """
        if style_name in self.style:
            self.current_style = style_name
            
    def add_operation(self, gate: str, target: int, 
                     control: Optional[int] = None) -> None:
        """
        Añade una operación al circuito.
        
        Args:
            gate: Nombre de la puerta
            target: Qubit objetivo
            control: Qubit de control (opcional)
        """
        op = {
            'gate': gate,
            'target': target,
            'type': 'two' if control is not None else 'single'
        }
        if control is not None:
            op['control'] = control
        self.operations.append(op)
        
    def draw_circuit(self, figsize=(12, 8), style='modern', 
                    show_annotations=True) -> None:
        """
        Dibuja el circuito cuántico.
        
        Args:
            figsize: Tamaño de la figura
            style: Estilo de visualización ('modern' o 'classic')
            show_annotations: Mostrar anotaciones y tooltips
        """
        self.set_style(style)
        
        if not self.operations:
            return
            
        # Encontrar qubits
        qubits = set()
        for op in self.operations:
            qubits.add(op['target'])
            if 'control' in op:
                qubits.add(op['control'])
                
        qubit_list = sorted(list(qubits))
        qubit_map = {q: i for i, q in enumerate(qubit_list)}
        
        self.fig, self.ax = plt.subplots(figsize=figsize)
        style_dict = self.style[self.current_style]
        
        # Configurar estilo
        self.ax.set_facecolor(style_dict['background'])
        self.fig.patch.set_facecolor(style_dict['background'])
        
        # Dibujar líneas de qubits
        for i in range(len(qubit_list)):
            self.ax.plot([0, len(self.operations)], [i, i],
                        color=style_dict['line_color'],
                        linewidth=1.5,
                        linestyle='--',
                        alpha=0.5)
            self.ax.text(-0.5, i, f'q{qubit_list[i]}',
                        ha='right', va='center',
                        color=style_dict['text_color'],
                        fontsize=12,
                        fontweight='bold')
            
        # Dibujar puertas
        for i, op in enumerate(self.operations):
            if op['type'] == 'single':
                self._draw_single_gate(i, qubit_map[op['target']], 
                                    op['gate'],
                                    show_annotations)
            else:
                self._draw_two_qubit_gate(i,
                                        qubit_map[op['control']],
                                        qubit_map[op['target']],
                                        op['gate'],
                                        show_annotations)
                
        # Configuración final
        self.ax.set_xlim(-1, len(self.operations))
        self.ax.set_ylim(-0.5, len(qubit_list) - 0.5)
        self.ax.axis('off')
        
        title = "Circuito Cuántico"
        if show_annotations:
            title += " (con anotaciones)"
        self.ax.set_title(title,
                         pad=20,
                         color=style_dict['text_color'],
                         fontsize=14,
                         fontweight='bold')
        
        plt.tight_layout()
        
    def _draw_single_gate(self, x: float, y: float, gate: str,
                         show_annotations: bool) -> None:
        """
        Dibuja una puerta de un qubit.
        
        Args:
            x: Posición x
            y: Posición y
            gate: Nombre de la puerta
            show_annotations: Mostrar anotaciones
        """
        style_dict = self.style[self.current_style]
        
        if self.current_style == 'modern':
            # Sombra
            shadow = patches.Rectangle((x-0.18, y-0.18), 0.36, 0.36,
                                    facecolor='gray',
                                    alpha=0.2)
            self.ax.add_patch(shadow)
            
            # Puerta con gradiente
            gate_color = style_dict['single_gate_color']
            rect = patches.Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                                  facecolor=gate_color,
                                  edgecolor='none',
                                  alpha=0.8)
            self.ax.add_patch(rect)
            
            # Borde superior más claro
            highlight = patches.Rectangle((x-0.2, y+0.15), 0.4, 0.05,
                                       facecolor='white',
                                       alpha=0.3)
            self.ax.add_patch(highlight)
        else:
            # Estilo clásico
            rect = patches.Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                                  facecolor=style_dict['single_gate_color'],
                                  edgecolor=style_dict['control_color'])
            self.ax.add_patch(rect)
            
        # Texto de la puerta
        self.ax.text(x, y, gate,
                    ha='center', va='center',
                    color='white' if self.current_style == 'modern' else 'black',
                    fontweight='bold')
                    
        if show_annotations:
            # Tooltip con descripción
            descriptions = {
                'H': 'Puerta Hadamard\nCrea superposición',
                'X': 'NOT Cuántico\nInvierte estados',
                'Y': 'Puerta Pauli-Y\nRotación en Y',
                'Z': 'Puerta Pauli-Z\nCambio de fase',
                'T': 'Puerta T\nRotación de π/4',
                'S': 'Puerta S\nRotación de π/2'
            }
            if gate in descriptions:
                self.ax.annotate(descriptions[gate],
                               xy=(x, y),
                               xytext=(10, 10),
                               textcoords='offset points',
                               bbox=dict(boxstyle='round,pad=0.5',
                                       fc='yellow',
                                       alpha=0.3),
                               arrowprops=dict(arrowstyle='->'))
                
    def _draw_two_qubit_gate(self, x: float, control_y: float,
                            target_y: float, gate: str,
                            show_annotations: bool) -> None:
        """
        Dibuja una puerta de dos qubits.
        
        Args:
            x: Posición x
            control_y: Posición y del control
            target_y: Posición y del objetivo
            gate: Nombre de la puerta
            show_annotations: Mostrar anotaciones
        """
        style_dict = self.style[self.current_style]
        
        # Línea de control
        if self.current_style == 'modern':
            # Línea con gradiente
            gradient = np.linspace(0, 1, 100)
            points = np.array([[x, y] for y in np.linspace(control_y, target_y, 100)])
            segments = np.array([[points[i], points[i+1]] 
                               for i in range(len(points)-1)])
            
            for segment, alpha in zip(segments, gradient):
                self.ax.plot(segment[:,0], segment[:,1],
                           color=style_dict['control_color'],
                           alpha=0.5 + 0.5*alpha,
                           linewidth=2)
        else:
            self.ax.plot([x, x], [control_y, target_y],
                        color=style_dict['control_color'],
                        linewidth=2)
            
        # Punto de control
        if self.current_style == 'modern':
            # Punto con brillo
            control = plt.Circle((x, control_y), 0.1,
                               facecolor=style_dict['control_color'])
            self.ax.add_patch(control)
            highlight = plt.Circle((x-0.03, control_y+0.03), 0.03,
                                 facecolor='white',
                                 alpha=0.6)
            self.ax.add_patch(highlight)
        else:
            control = plt.Circle((x, control_y), 0.1,
                               facecolor=style_dict['control_color'])
            self.ax.add_patch(control)
            
        # Puerta objetivo
        if gate == 'CNOT':
            if self.current_style == 'modern':
                # Círculo con efecto 3D
                outer = plt.Circle((x, target_y), 0.2,
                                 facecolor='none',
                                 edgecolor=style_dict['control_color'],
                                 linewidth=2)
                self.ax.add_patch(outer)
                inner = plt.Circle((x, target_y), 0.18,
                                 facecolor='white',
                                 alpha=0.6)
                self.ax.add_patch(inner)
                
                # Cruz
                self.ax.plot([x-0.2, x+0.2], [target_y, target_y],
                           color=style_dict['control_color'],
                           linewidth=2)
            else:
                circle = plt.Circle((x, target_y), 0.2,
                                  facecolor='none',
                                  edgecolor=style_dict['control_color'])
                self.ax.add_patch(circle)
                self.ax.plot([x-0.2, x+0.2], [target_y, target_y],
                           color=style_dict['control_color'])
        else:
            # Otras puertas de dos qubits
            self._draw_single_gate(x, target_y, gate, show_annotations)
            
        if show_annotations:
            # Tooltips para puertas de dos qubits
            descriptions = {
                'CNOT': 'NOT Controlado\nInvierte el objetivo si control es |1⟩',
                'CZ': 'Z Controlado\nCambio de fase condicional',
                'SWAP': 'Intercambia estados\nEntre dos qubits'
            }
            if gate in descriptions:
                self.ax.annotate(descriptions[gate],
                               xy=(x, (control_y + target_y)/2),
                               xytext=(10, 10),
                               textcoords='offset points',
                               bbox=dict(boxstyle='round,pad=0.5',
                                       fc='yellow',
                                       alpha=0.3),
                               arrowprops=dict(arrowstyle='->'))
                               
    def create_animation(self, states: List[np.ndarray],
                        interval: int = 100) -> FuncAnimation:
        """
        Crea una animación de la evolución del estado en la esfera de Bloch.
        
        Args:
            states: Lista de estados cuánticos
            interval: Intervalo entre frames en ms
            
        Returns:
            FuncAnimation: Animación del estado
        """
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Superficie de la esfera
        u = np.linspace(0, 2*np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        def update(frame):
            ax.clear()
            
            # Dibujar esfera
            ax.plot_surface(x, y, z,
                          alpha=0.1,
                          color='b',
                          shade=True)
            
            # Ejes
            ax.plot([-1,1], [0,0], [0,0], 'k-', alpha=0.5, label='x')
            ax.plot([0,0], [-1,1], [0,0], 'k-', alpha=0.5, label='y')
            ax.plot([0,0], [0,0], [-1,1], 'k-', alpha=0.5, label='z')
            
            # Etiquetas
            ax.text(1.1, 0, 0, '|+⟩', color='red')
            ax.text(-1.1, 0, 0, '|-⟩', color='red')
            ax.text(0, 0, 1.1, '|0⟩', color='blue')
            ax.text(0, 0, -1.1, '|1⟩', color='blue')
            
            # Estado actual
            state = states[frame]
            theta = 2 * np.angle(state[1] * np.conj(state[0]))
            phi = 2 * np.arccos(abs(state[0]))
            
            # Vector de Bloch
            x_coord = np.sin(phi) * np.cos(theta)
            y_coord = np.sin(phi) * np.sin(theta)
            z_coord = np.cos(phi)
            
            ax.quiver(0, 0, 0, x_coord, y_coord, z_coord,
                     color='r',
                     arrow_length_ratio=0.15,
                     linewidth=2)
            
            # Proyecciones
            ax.plot([x_coord,x_coord], [y_coord,y_coord], [0,z_coord],
                   'r--', alpha=0.3)
            ax.plot([x_coord,x_coord], [0,y_coord], [0,0],
                   'r--', alpha=0.3)
            ax.plot([0,x_coord], [0,0], [0,0],
                   'r--', alpha=0.3)
            
            # Configuración de la vista
            ax.set_box_aspect([1,1,1])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.view_init(elev=20, azim=frame)
            
        anim = FuncAnimation(fig, update,
                           frames=len(states),
                           interval=interval,
                           blit=False)
        return anim
        
    def plot_state_evolution(self, states: List[np.ndarray],
                           figsize=(10, 6)) -> None:
        """
        Grafica la evolución de las amplitudes del estado.
        
        Args:
            states: Lista de estados cuánticos
            figsize: Tamaño de la figura
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        steps = range(len(states))
        
        # Amplitudes
        amplitudes_0 = [abs(state[0])**2 for state in states]
        amplitudes_1 = [abs(state[1])**2 for state in states]
        
        ax1.plot(steps, amplitudes_0, 'b.-', label='|0⟩')
        ax1.plot(steps, amplitudes_1, 'r.-', label='|1⟩')
        ax1.set_ylabel('Probabilidad')
        ax1.set_title('Evolución de Probabilidades')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Fases
        phases_0 = [np.angle(state[0]) for state in states]
        phases_1 = [np.angle(state[1]) for state in states]
        
        ax2.plot(steps, phases_0, 'b.-', label='|0⟩')
        ax2.plot(steps, phases_1, 'r.-', label='|1⟩')
        ax2.set_xlabel('Paso')
        ax2.set_ylabel('Fase (radianes)')
        ax2.set_title('Evolución de Fases')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()