# Módulo de perfiles de hardware cuántico
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import copy
 import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Definiciones de tipos de hardware cuántico
class QuantumProcessorType(str, Enum):
    SUPERCONDUCTING = "superconducting"  # Procesadores basados en qubits superconductores
    TRAPPED_ION = "trapped_ion"         # Procesadores basados en iones atrapados
    PHOTONIC = "photonic"               # Procesadores basados en fotones
    NEUTRAL_ATOM = "neutral_atom"       # Procesadores basados en átomos neutros
    SPIN_QUBIT = "spin_qubit"           # Procesadores basados en espines
    TOPOLOGICAL = "topological"         # Procesadores basados en qubits topológicos
    DIAMOND_NV = "diamond_nv"           # Centros NV en diamante
    SILICON_QUANTUM_DOT = "silicon_quantum_dot"  # Puntos cuánticos en silicio

@dataclass
class QubitConnectivity:
    """Modelo de conectividad entre qubits"""
    adjacency_matrix: List[List[int]]  # Matriz de adyacencia (1 si hay conexión, 0 si no)
    connection_fidelity: Optional[List[List[float]]] = None  # Fidelidad de cada conexión
    
    def get_neighbors(self, qubit_idx: int) -> List[int]:
        """Obtener índices de qubits vecinos conectados"""
        if qubit_idx >= len(self.adjacency_matrix):
            return []
        return [i for i, connected in enumerate(self.adjacency_matrix[qubit_idx]) if connected == 1]
    
    def get_connection_fidelity(self, qubit1: int, qubit2: int) -> float:
        """Obtener fidelidad de la conexión entre dos qubits"""
        if self.connection_fidelity is None:
            return 1.0  # Valor por defecto si no hay datos de fidelidad
        
        if (qubit1 >= len(self.connection_fidelity) or 
            qubit2 >= len(self.connection_fidelity[0])):
            return 0.0
            
        return self.connection_fidelity[qubit1][qubit2]
    
    def visualize_connectivity(self, title: str = "Conectividad de Qubits", figsize: Tuple[int, int] = (10, 8), 
                              node_size: int = 500, show_fidelity: bool = True) -> plt.Figure:
        """Visualizar la topología de conectividad entre qubits"""
        G = nx.Graph()
        num_qubits = len(self.adjacency_matrix)
        
        # Añadir nodos
        for i in range(num_qubits):
            G.add_node(i)
        
        # Añadir conexiones
        edge_colors = []
        edge_widths = []
        edge_labels = {}
        
        for i in range(num_qubits):
            for j in range(i+1, num_qubits):
                if self.adjacency_matrix[i][j] == 1:
                    G.add_edge(i, j)
                    
                    # Colorear según fidelidad si está disponible
                    if show_fidelity and self.connection_fidelity is not None:
                        fidelity = self.connection_fidelity[i][j]
                        # Escala de colores: rojo (baja fidelidad) a verde (alta fidelidad)
                        color = plt.cm.RdYlGn(fidelity)
                        edge_colors.append(color)
                        edge_widths.append(1 + 3 * fidelity)  # Ancho proporcional a fidelidad
                        edge_labels[(i, j)] = f"{fidelity:.3f}"
                    else:
                        edge_colors.append('black')
                        edge_widths.append(1.5)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=figsize)
        
        # Determinar layout según número de qubits
        if num_qubits <= 11:  # Para pocos qubits, usar layout circular
            pos = nx.circular_layout(G)
        else:  # Para muchos qubits, intentar representar la estructura 2D si existe
            try:
                # Intentar crear un layout de rejilla
                grid_size = int(np.ceil(np.sqrt(num_qubits)))
                pos = {}
                for i in range(num_qubits):
                    row, col = i // grid_size, i % grid_size
                    pos[i] = np.array([col, -row])  # Coordenadas (x, y)
            except:
                # Si falla, usar layout spring
                pos = nx.spring_layout(G, seed=42)
        
        # Dibujar nodos y conexiones
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=node_size, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
        
        # Dibujar conexiones con colores según fidelidad
        edges = list(G.edges())
        if edges:  # Verificar que hay conexiones para dibujar
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=edge_widths, 
                                 edge_color=edge_colors, ax=ax)
            
            # Mostrar etiquetas de fidelidad si se solicita
            if show_fidelity and self.connection_fidelity is not None:
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        
        # Añadir leyenda si se muestra fidelidad
        if show_fidelity and self.connection_fidelity is not None:
            legend_elements = [
                Line2D([0], [0], color=plt.cm.RdYlGn(0.2), lw=2, label='Baja fidelidad'),
                Line2D([0], [0], color=plt.cm.RdYlGn(0.5), lw=2, label='Media fidelidad'),
                Line2D([0], [0], color=plt.cm.RdYlGn(0.8), lw=2, label='Alta fidelidad')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
        
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        
        return fig

@dataclass
class GateParameters:
    """Parámetros de rendimiento de puertas cuánticas"""
    gate_time_ns: float  # Tiempo de ejecución en nanosegundos
    fidelity: float      # Fidelidad de la puerta (0-1)
    error_rate: float    # Tasa de error

@dataclass
class QubitParameters:
    """Parámetros físicos de un qubit"""
    t1_us: float         # Tiempo de relajación T1 en microsegundos
    t2_us: float         # Tiempo de decoherencia T2 en microsegundos
    readout_error: float # Error de lectura
    idle_error: float    # Error en estado de espera

@dataclass
class HardwareProfile:
    """Perfil completo de un procesador cuántico"""
    name: str                                # Nombre del procesador
    processor_type: QuantumProcessorType     # Tipo de procesador
    num_qubits: int                          # Número de qubits
    connectivity: QubitConnectivity           # Modelo de conectividad
    qubit_parameters: List[QubitParameters]   # Parámetros de cada qubit
    gate_parameters: Dict[str, GateParameters] # Parámetros de cada tipo de puerta
    max_circuit_depth: int                   # Profundidad máxima de circuito
    simulator_backend: str = "statevector"   # Backend de simulación por defecto
    custom_noise_model: Optional['NoiseModel'] = None  # Modelo de ruido personalizado
    
    def visualize_profile(self, figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
        """Visualizar características del perfil de hardware"""
        fig = plt.figure(figsize=figsize)
        
        # Crear una disposición de subgráficos
        gs = fig.add_gridspec(2, 2)
        
        # 1. Visualizar topología de conectividad
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_connectivity(ax1)
        
        # 2. Visualizar tiempos de coherencia por qubit
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_coherence_times(ax2)
        
        # 3. Visualizar errores de puerta
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_gate_errors(ax3)
        
        # 4. Visualizar errores de lectura por qubit
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_readout_errors(ax4)
        
        plt.tight_layout()
        plt.suptitle(f"Perfil de Hardware: {self.name} ({self.processor_type.value})", 
                    fontsize=16, y=1.02)
        
        return fig
    
    def _plot_connectivity(self, ax: plt.Axes) -> None:
        """Visualizar topología de conectividad"""
        G = nx.Graph()
        
        # Añadir nodos
        for i in range(self.num_qubits):
            G.add_node(i)
        
        # Añadir conexiones
        for i in range(self.num_qubits):
            for j in range(i+1, self.num_qubits):
                if self.connectivity.adjacency_matrix[i][j] == 1:
                    G.add_edge(i, j)
        
        # Determinar layout según número de qubits
        if self.num_qubits <= 11:
            pos = nx.circular_layout(G)
        else:
            try:
                grid_size = int(np.ceil(np.sqrt(self.num_qubits)))
                pos = {}
                for i in range(self.num_qubits):
                    row, col = i // grid_size, i % grid_size
                    pos[i] = np.array([col, -row])
            except:
                pos = nx.spring_layout(G, seed=42)
        
        # Dibujar nodos y conexiones
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=300, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, ax=ax)
        
        ax.set_title("Topología de Conectividad")
        ax.axis('off')
    
    def _plot_coherence_times(self, ax: plt.Axes) -> None:
        """Visualizar tiempos de coherencia por qubit"""
        qubit_indices = list(range(self.num_qubits))
        t1_values = [q.t1_us for q in self.qubit_parameters]
        t2_values = [q.t2_us for q in self.qubit_parameters]
        
        x = np.arange(len(qubit_indices))
        width = 0.35
        
        ax.bar(x - width/2, t1_values, width, label='T1 (μs)')
        ax.bar(x + width/2, t2_values, width, label='T2 (μs)')
        
        ax.set_xlabel('Qubit')
        ax.set_ylabel('Tiempo (μs)')
        ax.set_title('Tiempos de Coherencia')
        ax.set_xticks(x)
        ax.set_xticklabels(qubit_indices)
        ax.legend()
        
        # Usar escala logarítmica si hay valores muy dispares
        if max(t1_values + t2_values) / min(filter(lambda x: x > 0, t1_values + t2_values)) > 100:
            ax.set_yscale('log')
    
    def _plot_gate_errors(self, ax: plt.Axes) -> None:
        """Visualizar errores de puerta"""
        gates = list(self.gate_parameters.keys())
        error_rates = [self.gate_parameters[gate].error_rate for gate in gates]
        
        # Ordenar por tasa de error
        sorted_indices = np.argsort(error_rates)
        sorted_gates = [gates[i] for i in sorted_indices]
        sorted_errors = [error_rates[i] for i in sorted_indices]
        
        y_pos = np.arange(len(sorted_gates))
        
        ax.barh(y_pos, sorted_errors, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(sorted_gates)
        ax.invert_yaxis()  # Puertas con menor error arriba
        ax.set_xlabel('Tasa de Error')
        ax.set_title('Errores de Puerta')
        
        # Añadir valores en las barras
        for i, v in enumerate(sorted_errors):
            ax.text(v + 0.0001, i, f"{v:.4f}", va='center')
    
    def _plot_readout_errors(self, ax: plt.Axes) -> None:
        """Visualizar errores de lectura por qubit"""
        qubit_indices = list(range(self.num_qubits))
        readout_errors = [q.readout_error for q in self.qubit_parameters]
        
        ax.bar(qubit_indices, readout_errors, color='salmon')
        
        ax.set_xlabel('Qubit')
        ax.set_ylabel('Error de Lectura')
        ax.set_title('Errores de Lectura por Qubit')
        ax.set_xticks(qubit_indices)
        
        # Añadir línea de error promedio
        avg_error = sum(readout_errors) / len(readout_errors)
        ax.axhline(y=avg_error, color='r', linestyle='--', 
                  label=f'Promedio: {avg_error:.4f}')
        ax.legend()
    
    def create_noise_model(self) -> 'NoiseModel':
        """Crear un modelo de ruido basado en los parámetros del hardware"""
        return NoiseModel.from_hardware_profile(self)
    
    def with_custom_noise(self, noise_model: 'NoiseModel') -> 'HardwareProfile':
        """Crear una copia del perfil con un modelo de ruido personalizado"""
        profile_copy = copy.deepcopy(self)
        profile_copy.custom_noise_model = noise_model
        return profile_copy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir perfil a diccionario para serialización"""
        data = {
            "name": self.name,
            "processor_type": self.processor_type.value,
            "num_qubits": self.num_qubits,
            "connectivity": {
                "adjacency_matrix": self.connectivity.adjacency_matrix,
                "connection_fidelity": self.connectivity.connection_fidelity
            },
            "qubit_parameters": [
                {"t1_us": q.t1_us, "t2_us": q.t2_us, 
                 "readout_error": q.readout_error, "idle_error": q.idle_error}
                for q in self.qubit_parameters
            ],
            "gate_parameters": {
                gate: {"gate_time_ns": params.gate_time_ns, 
                       "fidelity": params.fidelity, 
                       "error_rate": params.error_rate}
                for gate, params in self.gate_parameters.items()
            },
            "max_circuit_depth": self.max_circuit_depth,
            "simulator_backend": self.simulator_backend
        }
        
        # Incluir modelo de ruido personalizado si existe
        if self.custom_noise_model:
            data["custom_noise_model"] = {
                "noise_types": {k.value: v for k, v in self.custom_noise_model.noise_types.items()},
                "has_per_qubit_noise": self.custom_noise_model.per_qubit_noise is not None,
                "has_per_gate_noise": self.custom_noise_model.per_gate_noise is not None,
                "has_correlation_matrix": self.custom_noise_model.correlation_matrix is not None
            }
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HardwareProfile':
        """Crear perfil a partir de un diccionario"""
        connectivity = QubitConnectivity(
            adjacency_matrix=data["connectivity"]["adjacency_matrix"],
            connection_fidelity=data["connectivity"].get("connection_fidelity")
        )
        
        qubit_parameters = [
            QubitParameters(
                t1_us=q["t1_us"],
                t2_us=q["t2_us"],
                readout_error=q["readout_error"],
                idle_error=q["idle_error"]
            )
            for q in data["qubit_parameters"]
        ]
        
        gate_parameters = {
            gate: GateParameters(
                gate_time_ns=params["gate_time_ns"],
                fidelity=params["fidelity"],
                error_rate=params["error_rate"]
            )
            for gate, params in data["gate_parameters"].items()
        }
        
        return cls(
            name=data["name"],
            processor_type=QuantumProcessorType(data["processor_type"]),
            num_qubits=data["num_qubits"],
            connectivity=connectivity,
            qubit_parameters=qubit_parameters,
            gate_parameters=gate_parameters,
            max_circuit_depth=data["max_circuit_depth"],
            simulator_backend=data.get("simulator_backend", "statevector")
        )

class HardwareProfileManager:
    """Gestor de perfiles de hardware cuántico"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, HardwareProfile] = {}
        self.load_default_profiles()
        
    def load_default_profiles(self) -> None:
        """Cargar perfiles predeterminados"""
        # Perfiles genéricos
        superconducting = self._create_superconducting_profile()
        self.profiles[superconducting.name] = superconducting
        
        trapped_ion = self._create_trapped_ion_profile()
        self.profiles[trapped_ion.name] = trapped_ion
        
        photonic = self._create_photonic_profile()
        self.profiles[photonic.name] = photonic
        
        # Perfiles de fabricantes específicos
        ibm_profile = self._create_ibm_profile()
        self.profiles[ibm_profile.name] = ibm_profile
        
        rigetti_profile = self._create_rigetti_profile()
        self.profiles[rigetti_profile.name] = rigetti_profile
        
        ionq_profile = self._create_ionq_profile()
        self.profiles[ionq_profile.name] = ionq_profile
    
    def _create_superconducting_profile(self) -> HardwareProfile:
        """Crear perfil para procesador superconductor genérico"""
        num_qubits = 27
        
        # Crear matriz de adyacencia para topología de rejilla 2D
        adj_matrix = [[0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        
        # Conectividad en rejilla
        grid_size = int(np.ceil(np.sqrt(num_qubits)))
        for i in range(num_qubits):
            row, col = i // grid_size, i % grid_size
            
            # Conectar con vecinos (arriba, abajo, izquierda, derecha)
            neighbors = []
            if row > 0:
                neighbors.append((row-1) * grid_size + col)  # Arriba
            if row < grid_size-1 and (row+1) * grid_size + col < num_qubits:
                neighbors.append((row+1) * grid_size + col)  # Abajo
            if col > 0:
                neighbors.append(row * grid_size + (col-1))  # Izquierda
            if col < grid_size-1 and row * grid_size + (col+1) < num_qubits:
                neighbors.append(row * grid_size + (col+1))  # Derecha
            
            for neighbor in neighbors:
                adj_matrix[i][neighbor] = 1
                adj_matrix[neighbor][i] = 1
        
        # Parámetros de qubits (valores típicos para superconductores)
        qubit_params = []
        for _ in range(num_qubits):
            # Añadir variabilidad realista
            t1 = 50.0 + np.random.normal(0, 5.0)  # T1 ~50μs
            t2 = 30.0 + np.random.normal(0, 3.0)  # T2 ~30μs
            readout_err = 0.02 + np.random.normal(0, 0.005)  # ~2% error
            idle_err = 0.001 + np.random.normal(0, 0.0002)  # ~0.1% error
            
            qubit_params.append(QubitParameters(
                t1_us=max(t1, 30.0),  # Asegurar valores mínimos razonables
                t2_us=max(t2, 15.0),
                readout_error=max(min(readout_err, 0.05), 0.005),
                idle_error=max(min(idle_err, 0.005), 0.0001)
            ))
        
        # Parámetros de puertas
        gate_params = {
            "X": GateParameters(gate_time_ns=35.0, fidelity=0.9985, error_rate=0.0015),
            "Y": GateParameters(gate_time_ns=35.0, fidelity=0.9980, error_rate=0.0020),
            "Z": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
            "H": GateParameters(gate_time_ns=45.0, fidelity=0.9975, error_rate=0.0025),
            "CNOT": GateParameters(gate_time_ns=250.0, fidelity=0.9900, error_rate=0.0100),
            "CZ": GateParameters(gate_time_ns=220.0, fidelity=0.9920, error_rate=0.0080),
            "RX": GateParameters(gate_time_ns=40.0, fidelity=0.9980, error_rate=0.0020),
            "RY": GateParameters(gate_time_ns=40.0, fidelity=0.9980, error_rate=0.0020),
            "RZ": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
        }
        
        return HardwareProfile(
            name="Generic-Superconducting-27Q",
            processor_type=QuantumProcessorType.SUPERCONDUCTING,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(adjacency_matrix=adj_matrix),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=100,
            simulator_backend="statevector"
        )
    
    def _create_trapped_ion_profile(self) -> HardwareProfile:
        """Crear perfil para procesador de iones atrapados genérico"""
        num_qubits = 11
        
        # Conectividad completa (todos con todos)
        adj_matrix = [[1 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i in range(num_qubits):
            adj_matrix[i][i] = 0  # No auto-conexión
        
        # Parámetros de qubits (valores típicos para iones atrapados)
        qubit_params = []
        for _ in range(num_qubits):
            # Añadir variabilidad realista
            t1 = 10000.0 + np.random.normal(0, 500.0)  # T1 ~10s (muy largo)
            t2 = 500.0 + np.random.normal(0, 50.0)     # T2 ~500ms
            readout_err = 0.005 + np.random.normal(0, 0.001)  # ~0.5% error
            idle_err = 0.0001 + np.random.normal(0, 0.00005)  # ~0.01% error
            
            qubit_params.append(QubitParameters(
                t1_us=max(t1, 5000.0),
                t2_us=max(t2, 200.0),
                readout_error=max(min(readout_err, 0.01), 0.001),
                idle_error=max(min(idle_err, 0.001), 0.00001)
            ))
        
        # Parámetros de puertas
        gate_params = {
            "X": GateParameters(gate_time_ns=10000.0, fidelity=0.9995, error_rate=0.0005),
            "Y": GateParameters(gate_time_ns=10000.0, fidelity=0.9995, error_rate=0.0005),
            "Z": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
            "H": GateParameters(gate_time_ns=20000.0, fidelity=0.9990, error_rate=0.0010),
            "CNOT": GateParameters(gate_time_ns=200000.0, fidelity=0.9950, error_rate=0.0050),
            "CZ": GateParameters(gate_time_ns=180000.0, fidelity=0.9960, error_rate=0.0040),
            "RX": GateParameters(gate_time_ns=15000.0, fidelity=0.9990, error_rate=0.0010),
            "RY": GateParameters(gate_time_ns=15000.0, fidelity=0.9990, error_rate=0.0010),
            "RZ": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
            "XX": GateParameters(gate_time_ns=150000.0, fidelity=0.9970, error_rate=0.0030),
        }
        
        return HardwareProfile(
            name="Generic-TrappedIon-11Q",
            processor_type=QuantumProcessorType.TRAPPED_ION,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(adjacency_matrix=adj_matrix),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=200,
            simulator_backend="statevector"
        )
    
    def _create_photonic_profile(self) -> HardwareProfile:
        """Crear perfil para procesador fotónico genérico"""
        num_qubits = 8
        
        # Conectividad lineal para fotones
        adj_matrix = [[0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i in range(num_qubits - 1):
            adj_matrix[i][i+1] = 1
            adj_matrix[i+1][i] = 1
        
        # Parámetros de qubits (valores típicos para fotones)
        qubit_params = []
        for _ in range(num_qubits):
            # Fotones tienen tiempos de coherencia muy largos pero pérdidas
            t1 = 1000000.0  # Muy largo (1s)
            t2 = 1000000.0  # Igual a T1 para fotones
            readout_err = 0.10 + np.random.normal(0, 0.02)  # ~10% error (detección)
            idle_err = 0.05 + np.random.normal(0, 0.01)  # ~5% (pérdidas)
            
            qubit_params.append(QubitParameters(
                t1_us=t1,
                t2_us=t2,
                readout_error=max(min(readout_err, 0.20), 0.05),
                idle_error=max(min(idle_err, 0.10), 0.01)
            ))
        
        # Parámetros de puertas
        gate_params = {
            "X": GateParameters(gate_time_ns=100.0, fidelity=0.9950, error_rate=0.0050),
            "Y": GateParameters(gate_time_ns=100.0, fidelity=0.9950, error_rate=0.0050),
            "Z": GateParameters(gate_time_ns=100.0, fidelity=0.9950, error_rate=0.0050),
            "H": GateParameters(gate_time_ns=100.0, fidelity=0.9950, error_rate=0.0050),
            "CNOT": GateParameters(gate_time_ns=5000.0, fidelity=0.9000, error_rate=0.1000),
            "CZ": GateParameters(gate_time_ns=5000.0, fidelity=0.9000, error_rate=0.1000),
            "SWAP": GateParameters(gate_time_ns=10000.0, fidelity=0.8500, error_rate=0.1500),
        }
        
        return HardwareProfile(
            name="Generic-Photonic-8Q",
            processor_type=QuantumProcessorType.PHOTONIC,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(adjacency_matrix=adj_matrix),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=50,
            simulator_backend="statevector"
        )
    
    def _create_ibm_profile(self) -> HardwareProfile:
        """Crear perfil basado en procesador IBM Quantum"""
        # IBM Eagle - 127 qubits (simplificado)
        num_qubits = 27  # Versión reducida para simulación
        
        # Topología de celosía hexagonal (heavy-hexagon)
        adj_matrix = [[0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        
        # Crear una versión simplificada de la topología heavy-hexagon de IBM
        # Esta es una aproximación, la topología real es más compleja
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),  # Hexágono exterior
            (6, 0), (7, 1), (8, 2), (9, 3), (10, 4), (11, 5),  # Conexiones radiales
            (12, 6), (13, 7), (14, 8), (15, 9), (16, 10), (17, 11),  # Segundo anillo
            (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 12),  # Conexiones del segundo anillo
            (18, 12), (19, 13), (20, 14), (21, 15), (22, 16), (23, 17),  # Tercer anillo
            (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 18),  # Conexiones del tercer anillo
            (24, 18), (25, 20), (26, 22)  # Conexiones adicionales
        ]
        
        for i, j in connections:
            if i < num_qubits and j < num_qubits:  # Asegurar que los índices son válidos
                adj_matrix[i][j] = 1
                adj_matrix[j][i] = 1
        
        # Parámetros de qubits (basados en datos publicados de IBM)
        qubit_params = []
        for _ in range(num_qubits):
            # Valores típicos para IBM Quantum (con variabilidad)
            t1 = 100.0 + np.random.normal(0, 10.0)  # T1 ~100μs
            t2 = 70.0 + np.random.normal(0, 7.0)    # T2 ~70μs
            readout_err = 0.015 + np.random.normal(0, 0.003)  # ~1.5% error
            idle_err = 0.0005 + np.random.normal(0, 0.0001)  # ~0.05% error
            
            qubit_params.append(QubitParameters(
                t1_us=max(t1, 70.0),
                t2_us=max(t2, 40.0),
                readout_error=max(min(readout_err, 0.03), 0.005),
                idle_error=max(min(idle_err, 0.001), 0.0001)
            ))
        
        # Parámetros de puertas (basados en datos publicados de IBM)
        gate_params = {
            "X": GateParameters(gate_time_ns=35.0, fidelity=0.9996, error_rate=0.0004),
            "SX": GateParameters(gate_time_ns=35.0, fidelity=0.9996, error_rate=0.0004),  # Puerta √X
            "Y": GateParameters(gate_time_ns=35.0, fidelity=0.9996, error_rate=0.0004),
            "Z": GateParameters(gate_time_ns=0.0, fidelity=1.0000, error_rate=0.0000),  # Virtual
            "H": GateParameters(gate_time_ns=70.0, fidelity=0.9992, error_rate=0.0008),
            "CNOT": GateParameters(gate_time_ns=320.0, fidelity=0.9940, error_rate=0.0060),
            "CZ": GateParameters(gate_time_ns=300.0, fidelity=0.9950, error_rate=0.0050),
            "RZ": GateParameters(gate_time_ns=0.0, fidelity=1.0000, error_rate=0.0000),  # Virtual
            "ECR": GateParameters(gate_time_ns=270.0, fidelity=0.9950, error_rate=0.0050),  # Puerta específica de IBM
        }
        
        # Crear matriz de fidelidad de conexiones
        connection_fidelity = [[0.0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i, j in connections:
            if i < num_qubits and j < num_qubits:
                # Fidelidad base con variabilidad
                fidelity = 0.994 + np.random.normal(0, 0.002)
                connection_fidelity[i][j] = max(min(fidelity, 0.999), 0.985)
                connection_fidelity[j][i] = connection_fidelity[i][j]
        
        return HardwareProfile(
            name="IBM-Eagle-27Q",
            processor_type=QuantumProcessorType.SUPERCONDUCTING,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(
                adjacency_matrix=adj_matrix,
                connection_fidelity=connection_fidelity
            ),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=150,
            simulator_backend="statevector"
        )
    
    def _create_rigetti_profile(self) -> HardwareProfile:
        """Crear perfil basado en procesador Rigetti Quantum"""
        # Rigetti Aspen - versión simplificada
        num_qubits = 20
        
        # Topología de Rigetti (octágonos anidados)
        adj_matrix = [[0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        
        # Crear una versión simplificada de la topología de Rigetti
        # Dos octágonos conectados
        octagon1 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]
        octagon2 = [(8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 8)]
        # Conexiones entre octágonos
        connections = octagon1 + octagon2 + [(0, 8), (4, 12)]
        # Qubits adicionales conectados
        extra = [(16, 2), (17, 6), (18, 10), (19, 14)]
        
        all_connections = connections + extra
        for i, j in all_connections:
            adj_matrix[i][j] = 1
            adj_matrix[j][i] = 1
        
        # Parámetros de qubits (basados en datos publicados de Rigetti)
        qubit_params = []
        for _ in range(num_qubits):
            # Valores típicos para Rigetti (con variabilidad)
            t1 = 20.0 + np.random.normal(0, 3.0)  # T1 ~20μs
            t2 = 15.0 + np.random.normal(0, 2.0)  # T2 ~15μs
            readout_err = 0.03 + np.random.normal(0, 0.005)  # ~3% error
            idle_err = 0.001 + np.random.normal(0, 0.0002)  # ~0.1% error
            
            qubit_params.append(QubitParameters(
                t1_us=max(t1, 15.0),
                t2_us=max(t2, 10.0),
                readout_error=max(min(readout_err, 0.05), 0.01),
                idle_error=max(min(idle_err, 0.002), 0.0005)
            ))
        
        # Parámetros de puertas (basados en datos publicados de Rigetti)
        gate_params = {
            "RX": GateParameters(gate_time_ns=50.0, fidelity=0.9980, error_rate=0.0020),
            "RZ": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
            "CZ": GateParameters(gate_time_ns=200.0, fidelity=0.9850, error_rate=0.0150),
            "XY": GateParameters(gate_time_ns=180.0, fidelity=0.9870, error_rate=0.0130),  # Puerta específica de Rigetti
            "CPHASE": GateParameters(gate_time_ns=220.0, fidelity=0.9830, error_rate=0.0170),
        }
        
        # Crear matriz de fidelidad de conexiones
        connection_fidelity = [[0.0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i, j in all_connections:
            # Fidelidad base con variabilidad
            fidelity = 0.985 + np.random.normal(0, 0.003)
            connection_fidelity[i][j] = max(min(fidelity, 0.995), 0.975)
            connection_fidelity[j][i] = connection_fidelity[i][j]
        
        return HardwareProfile(
            name="Rigetti-Aspen-20Q",
            processor_type=QuantumProcessorType.SUPERCONDUCTING,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(
                adjacency_matrix=adj_matrix,
                connection_fidelity=connection_fidelity
            ),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=100,
            simulator_backend="statevector"
        )
    
    def _create_ionq_profile(self) -> HardwareProfile:
        """Crear perfil basado en procesador IonQ"""
        # IonQ Harmony - 11 qubits
        num_qubits = 11
        
        # Conectividad completa (todos con todos) - característica de iones atrapados
        adj_matrix = [[0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i in range(num_qubits):
            for j in range(num_qubits):
                if i != j:  # No auto-conexión
                    adj_matrix[i][j] = 1
        
        # Parámetros de qubits (basados en datos publicados de IonQ)
        qubit_params = []
        for _ in range(num_qubits):
            # Valores típicos para IonQ (con variabilidad)
            t1 = 10000000.0  # T1 muy largo (10s)
            t2 = 1000000.0 + np.random.normal(0, 100000.0)  # T2 ~1s
            readout_err = 0.005 + np.random.normal(0, 0.001)  # ~0.5% error
            idle_err = 0.0001 + np.random.normal(0, 0.00002)  # ~0.01% error
            
            qubit_params.append(QubitParameters(
                t1_us=t1,
                t2_us=max(t2, 500000.0),
                readout_error=max(min(readout_err, 0.01), 0.002),
                idle_error=max(min(idle_err, 0.0002), 0.00005)
            ))
        
        # Parámetros de puertas (basados en datos publicados de IonQ)
        gate_params = {
            "X": GateParameters(gate_time_ns=10000.0, fidelity=0.9995, error_rate=0.0005),
            "Y": GateParameters(gate_time_ns=10000.0, fidelity=0.9995, error_rate=0.0005),
            "Z": GateParameters(gate_time_ns=0.0, fidelity=0.9999, error_rate=0.0001),  # Virtual
            "H": GateParameters(gate_time_ns=20000.0, fidelity=0.9990, error_rate=0.0010),
            "CNOT": GateParameters(gate_time_ns=200000.0, fidelity=0.9970, error_rate=0.0030),
            "MS": GateParameters(gate_time_ns=180000.0, fidelity=0.9980, error_rate=0.0020),  # Puerta Mølmer-Sørensen
            "R": GateParameters(gate_time_ns=15000.0, fidelity=0.9990, error_rate=0.0010),  # Rotación arbitraria
        }
        
        # Crear matriz de fidelidad de conexiones (alta para todos en IonQ)
        connection_fidelity = [[0.0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i in range(num_qubits):
            for j in range(num_qubits):
                if i != j:
                    # Alta fidelidad con ligera variabilidad según distancia
                    distance_factor = 1.0 - 0.0001 * abs(i - j)  # Ligera degradación con distancia
                    fidelity = 0.997 * distance_factor + np.random.normal(0, 0.001)
                    connection_fidelity[i][j] = max(min(fidelity, 0.999), 0.990)
        
        return HardwareProfile(
            name="IonQ-Harmony-11Q",
            processor_type=QuantumProcessorType.TRAPPED_ION,
            num_qubits=num_qubits,
            connectivity=QubitConnectivity(
                adjacency_matrix=adj_matrix,
                connection_fidelity=connection_fidelity
            ),
            qubit_parameters=qubit_params,
            gate_parameters=gate_params,
            max_circuit_depth=250,
            simulator_backend="statevector"
        )
    
    def get_profile(self, name: str) -> Optional[HardwareProfile]:
        """Obtener un perfil por nombre"""
        return self.profiles.get(name)
    
    def get_all_profiles(self) -> Dict[str, HardwareProfile]:
        """Obtener todos los perfiles disponibles"""
        return self.profiles
    
    def add_profile(self, profile: HardwareProfile) -> None:
        """Añadir un nuevo perfil"""
        self.profiles[profile.name] = profile
    
    def save_profile(self, profile: HardwareProfile, filename: Optional[str] = None) -> str:
        """Guardar un perfil en disco"""
        if filename is None:
            filename = f"{profile.name.lower().replace(' ', '_')}.json"
        
        # Asegurar que existe el directorio
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        filepath = os.path.join(self.profiles_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        
        return filepath
    
    def load_profile(self, filepath: str) -> Optional[HardwareProfile]:
        """Cargar un perfil desde disco"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            profile = HardwareProfile.from_dict(data)
            self.profiles[profile.name] = profile
            return profile
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error al cargar perfil: {e}")
            return None

# Modelos de ruido cuántico
class NoiseType(str, Enum):
    """Tipos de ruido cuántico"""
    AMPLITUDE_DAMPING = "amplitude_damping"  # Relajación de amplitud (T1)
    PHASE_DAMPING = "phase_damping"         # Decoherencia de fase (T2)
    DEPOLARIZING = "depolarizing"           # Despolarización (ruido blanco)
    THERMAL = "thermal"                     # Ruido térmico
    MEASUREMENT = "measurement"             # Error de medición
    CROSSTALK = "crosstalk"                 # Interferencia entre qubits
    LEAKAGE = "leakage"                     # Fuga a estados no computacionales

@dataclass
class NoiseModel:
    """Modelo de ruido cuántico para simulación"""
    noise_types: Dict[NoiseType, float]  # Tipo de ruido y su intensidad
    per_qubit_noise: Optional[Dict[int, Dict[NoiseType, float]]] = None  # Ruido específico por qubit
    per_gate_noise: Optional[Dict[str, Dict[NoiseType, float]]] = None  # Ruido específico por tipo de puerta
    correlation_matrix: Optional[List[List[float]]] = None  # Matriz de correlación de ruido entre qubits
    
    @classmethod
    def from_hardware_profile(cls, profile: HardwareProfile) -> 'NoiseModel':
        """Crear modelo de ruido a partir de un perfil de hardware"""
        # Ruido base para todos los qubits
        noise_types = {
            NoiseType.AMPLITUDE_DAMPING: 0.0,  # Se calculará a partir de T1
            NoiseType.PHASE_DAMPING: 0.0,      # Se calculará a partir de T2
            NoiseType.DEPOLARIZING: 0.0,       # Se calculará a partir de error de puertas
            NoiseType.MEASUREMENT: 0.0,         # Se calculará a partir de error de lectura
        }
        
        # Ruido específico por qubit
        per_qubit_noise = {}
        for i, qubit_params in enumerate(profile.qubit_parameters):
            # Convertir tiempos de coherencia a tasas de error
            t1_error = 1.0 - np.exp(-1.0 / qubit_params.t1_us)
            t2_error = 1.0 - np.exp(-1.0 / qubit_params.t2_us)
            
            per_qubit_noise[i] = {
                NoiseType.AMPLITUDE_DAMPING: t1_error,
                NoiseType.PHASE_DAMPING: max(0, t2_error - t1_error/2),  # T2 <= 2*T1 siempre
                NoiseType.MEASUREMENT: qubit_params.readout_error,
                NoiseType.DEPOLARIZING: qubit_params.idle_error,
            }
        
        # Ruido específico por puerta
        per_gate_noise = {}
        for gate, params in profile.gate_parameters.items():
            per_gate_noise[gate] = {
                NoiseType.DEPOLARIZING: params.error_rate,
            }
        
        # Matriz de correlación (por defecto sin correlación)
        num_qubits = profile.num_qubits
        correlation_matrix = [[0.0 for _ in range(num_qubits)] for _ in range(num_qubits)]
        for i in range(num_qubits):
            correlation_matrix[i][i] = 1.0  # Autocorrelación
        
        return cls(
            noise_types=noise_types,
            per_qubit_noise=per_qubit_noise,
            per_gate_noise=per_gate_noise,
            correlation_matrix=correlation_matrix
        )
    
    def apply_noise_to_circuit(self, circuit: Any) -> Any:
        """Aplicar modelo de ruido a un circuito cuántico"""
        # Esta es una función placeholder que se implementaría
        # según el framework de simulación específico (Qiskit, Cirq, etc.)
        return circuit

@dataclass
class HardwareComparison:
    """Resultados de comparación entre perfiles de hardware"""
    profiles: List[HardwareProfile]
    metrics: Dict[str, Dict[str, float]]
    
    def visualize_comparison(self, metric: str, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """Visualizar comparación de una métrica específica entre perfiles"""
        if metric not in self.metrics:
            raise ValueError(f"Métrica '{metric}' no disponible en la comparación")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        profile_names = [p.name for p in self.profiles]
        metric_values = [self.metrics[metric][p.name] for p in self.profiles]
        
        # Crear gráfico de barras
        bars = ax.bar(profile_names, metric_values)
        
        # Añadir etiquetas y título
        ax.set_xlabel('Perfil de Hardware')
        ax.set_ylabel(metric)
        ax.set_title(f'Comparación de {metric} entre perfiles de hardware')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}', ha='center', va='bottom')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig

# Función para obtener un gestor de perfiles singleton
_profile_manager = None

def get_hardware_profile_manager() -> HardwareProfileManager:
    """Obtener instancia singleton del gestor de perfiles"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = HardwareProfileManager()
    return _profile_manager

# Funciones de utilidad para simulación de hardware
def estimate_circuit_execution_time(circuit_gates: List[str], 
                                   hardware_profile: HardwareProfile) -> float:
    """Estimar tiempo de ejecución de un circuito en nanosegundos"""
    total_time = 0.0
    
    for gate in circuit_gates:
        if gate in hardware_profile.gate_parameters:
            total_time += hardware_profile.gate_parameters[gate].gate_time_ns
        else:
            # Puerta desconocida, usar tiempo promedio
            avg_time = sum(p.gate_time_ns for p in hardware_profile.gate_parameters.values()) / len(hardware_profile.gate_parameters)
            total_time += avg_time
    
    return total_time

def estimate_circuit_success_probability(circuit_gates: List[str],
                                        qubit_mapping: List[int],
                                        hardware_profile: HardwareProfile) -> float:
    """Estimar probabilidad de éxito de un circuito"""
    success_prob = 1.0
    
    # Considerar errores de puertas
    for gate in circuit_gates:
        if gate in hardware_profile.gate_parameters:
            success_prob *= (1.0 - hardware_profile.gate_parameters[gate].error_rate)
        else:
            # Puerta desconocida, usar error promedio
            avg_error = sum(p.error_rate for p in hardware_profile.gate_parameters.values()) / len(hardware_profile.gate_parameters)
            success_prob *= (1.0 - avg_error)
    
    # Considerar errores de lectura
    for logical_qubit, physical_qubit in enumerate(qubit_mapping):
        if physical_qubit < len(hardware_profile.qubit_parameters):
            readout_error = hardware_profile.qubit_parameters[physical_qubit].readout_error
            success_prob *= (1.0 - readout_error)
    
    return success_prob

def optimize_qubit_mapping(circuit: Any, hardware_profile: HardwareProfile) -> List[int]:
    """Optimizar mapeo de qubits lógicos a físicos"""
    # Implementación básica: asignar qubits en orden
    # En una implementación real, esto usaría algoritmos de optimización
    # basados en la topología del hardware y las operaciones del circuito
    return list(range(min(circuit.num_qubits, hardware_profile.num_qubits)))

def optimize_circuit_for_hardware(circuit: Any, hardware_profile: HardwareProfile) -> Any:
    """Optimizar un circuito cuántico para un hardware específico"""
    # Esta función implementaría técnicas como:
    # 1. Transpilación para adaptar a la topología del hardware
    # 2. Fusión de puertas para reducir profundidad
    # 3. Optimización de rutas de SWAP para minimizar operaciones
    # 4. Selección de puertas nativas del hardware
    
    # Por ahora, devolvemos el circuito sin cambios
    # En una implementación real, se integraría con frameworks como Qiskit o Cirq
    return circuit

def create_custom_hardware_profile(base_profile: HardwareProfile, 
                                  custom_params: Dict[str, Any]) -> HardwareProfile:
    """Crear un perfil de hardware personalizado a partir de uno base"""
    # Crear una copia profunda del perfil base
    profile = copy.deepcopy(base_profile)
    
    # Aplicar personalizaciones
    for param, value in custom_params.items():
        if param == "name":
            profile.name = value
        elif param == "num_qubits" and value <= base_profile.num_qubits:
            # Reducir el número de qubits (no se puede aumentar sin más información)
            profile.num_qubits = value
            # Ajustar matrices de conectividad
            profile.connectivity.adjacency_matrix = [
                [profile.connectivity.adjacency_matrix[i][j] for j in range(value)]
                for i in range(value)
            ]
            if profile.connectivity.connection_fidelity:
                profile.connectivity.connection_fidelity = [
                    [profile.connectivity.connection_fidelity[i][j] for j in range(value)]
                    for i in range(value)
                ]
            # Ajustar parámetros de qubits
            profile.qubit_parameters = profile.qubit_parameters[:value]
        elif param == "t1_factor" and isinstance(value, (int, float)) and value > 0:
            # Escalar tiempos T1 por un factor
            for i in range(profile.num_qubits):
                profile.qubit_parameters[i].t1_us *= value
        elif param == "t2_factor" and isinstance(value, (int, float)) and value > 0:
            # Escalar tiempos T2 por un factor
            for i in range(profile.num_qubits):
                profile.qubit_parameters[i].t2_us *= value
        elif param == "error_factor" and isinstance(value, (int, float)) and value > 0:
            # Escalar tasas de error por un factor
            for i in range(profile.num_qubits):
                profile.qubit_parameters[i].readout_error *= value
                profile.qubit_parameters[i].idle_error *= value
            for gate in profile.gate_parameters:
                profile.gate_parameters[gate].error_rate *= value
                # Ajustar fidelidad en consecuencia
                profile.gate_parameters[gate].fidelity = max(0, min(1, 1 - profile.gate_parameters[gate].error_rate))
        elif param == "gate_times_factor" and isinstance(value, (int, float)) and value > 0:
            # Escalar tiempos de puerta por un factor
            for gate in profile.gate_parameters:
                if profile.gate_parameters[gate].gate_time_ns > 0:  # No escalar puertas virtuales
                    profile.gate_parameters[gate].gate_time_ns *= value
        elif param == "max_circuit_depth":
            profile.max_circuit_depth = value
        elif param == "simulator_backend":
            profile.simulator_backend = value
    
    return profile

def simulate_circuit_with_noise(circuit: Any, hardware_profile: HardwareProfile, 
                              shots: int = 1024, custom_noise: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Simular un circuito con modelo de ruido basado en el perfil de hardware"""
    # Esta función implementaría:
    # 1. Creación de modelo de ruido a partir del perfil
    # 2. Aplicación de ruido al circuito
    # 3. Ejecución de la simulación con ruido
    # 4. Recopilación y análisis de resultados
    
    # Crear modelo de ruido base desde el perfil
    noise_model = hardware_profile.create_noise_model()
    
    # Aplicar personalizaciones de ruido si se proporcionan
    if custom_noise:
        # Aquí se modificaría el modelo de ruido según las especificaciones
        # Por ejemplo, aumentar ciertos tipos de ruido, añadir correlaciones, etc.
        pass
    
    # Resultados simulados (placeholder)
    # En una implementación real, esto se integraría con un simulador cuántico
    results = {
        "counts": {"0000": shots // 2, "1111": shots // 2},  # Distribución de resultados
        "success_probability": estimate_circuit_success_probability(
            ["H", "CNOT", "X"], [0, 1, 2], hardware_profile
        ),
        "execution_time_ns": estimate_circuit_execution_time(
            ["H", "CNOT", "X"], hardware_profile
        ),
        "noise_model": str(noise_model)
    }
    
    return results

def create_benchmark_circuits() -> Dict[str, Dict[str, Any]]:
    """Crear circuitos de prueba para evaluar perfiles de hardware"""
    # Esta función crea circuitos estándar para evaluar diferentes aspectos del hardware
    benchmark_circuits = {
        "bell_state": {
            "description": "Circuito de estado Bell (entrelazamiento de 2 qubits)",
            "num_qubits": 2,
            "gates": ["H", "CNOT"],
            "depth": 2,
            "entanglement": "pares",
            "target_state": "Bell"
        },
        "ghz_state": {
            "description": "Estado GHZ (entrelazamiento máximo de N qubits)",
            "num_qubits": 4,
            "gates": ["H", "CNOT", "CNOT", "CNOT"],
            "depth": 4,
            "entanglement": "global",
            "target_state": "GHZ"
        },
        "quantum_fourier_transform": {
            "description": "Transformada cuántica de Fourier de 4 qubits",
            "num_qubits": 4,
            "gates": ["H", "CPHASE", "H", "CPHASE", "CPHASE", "H", "CPHASE", "CPHASE", "CPHASE", "H"],
            "depth": 10,
            "entanglement": "complejo",
            "target_state": "QFT"
        },
        "error_correction": {
            "description": "Código de corrección de errores de 5 qubits",
            "num_qubits": 5,
            "gates": ["H", "CNOT", "CNOT", "CNOT", "CNOT", "X", "Z", "CNOT", "CNOT", "CNOT", "CNOT", "H"],
            "depth": 12,
            "entanglement": "código",
            "target_state": "código_corrección"
        },
        "random_circuit": {
            "description": "Circuito aleatorio de profundidad media",
            "num_qubits": 6,
            "gates": ["H", "X", "CNOT", "Y", "CNOT", "Z", "CNOT", "H", "CNOT", "X", "Y", "CNOT", "Z", "H", "CNOT"],
            "depth": 15,
            "entanglement": "aleatorio",
            "target_state": "complejo"
        },
        "deep_circuit": {
            "description": "Circuito profundo para evaluar decoherencia",
            "num_qubits": 3,
            "gates": ["H", "CNOT", "X", "CNOT", "Y", "CNOT", "Z", "CNOT", "H", "CNOT", "X", "CNOT", "Y", "CNOT", "Z", "CNOT",
                      "H", "CNOT", "X", "CNOT", "Y", "CNOT", "Z", "CNOT", "H", "CNOT", "X", "CNOT", "Y", "CNOT", "Z", "CNOT"],
            "depth": 32,
            "entanglement": "repetitivo",
            "target_state": "decoherente"
        },
        "shor_small": {
            "description": "Versión simplificada del algoritmo de Shor",
            "num_qubits": 7,
            "gates": ["H", "H", "H", "H", "CNOT", "CNOT", "CNOT", "CPHASE", "CPHASE", "H", "H", "H", "H", "SWAP", "CNOT", "CNOT"],
            "depth": 16,
            "entanglement": "estructurado",
            "target_state": "factorización"
        }
    }
    
    return benchmark_circuits

def evaluate_hardware_with_benchmarks(hardware_profile: HardwareProfile, 
                                    shots: int = 1024) -> Dict[str, Dict[str, Any]]:
    """Evaluar un perfil de hardware con circuitos de referencia"""
    benchmark_circuits = create_benchmark_circuits()
    results = {}
    
    for circuit_name, circuit_info in benchmark_circuits.items():
        # Verificar si el circuito es compatible con el hardware
        if circuit_info["num_qubits"] > hardware_profile.num_qubits:
            results[circuit_name] = {
                "status": "incompatible",
                "reason": f"El circuito requiere {circuit_info['num_qubits']} qubits, pero el hardware solo tiene {hardware_profile.num_qubits}"
            }
            continue
            
        if circuit_info["depth"] > hardware_profile.max_circuit_depth:
            results[circuit_name] = {
                "status": "incompatible",
                "reason": f"El circuito tiene profundidad {circuit_info['depth']}, pero el hardware soporta máximo {hardware_profile.max_circuit_depth}"
            }
            continue
        
        # Estimar métricas de rendimiento
        execution_time = estimate_circuit_execution_time(circuit_info["gates"], hardware_profile)
        success_prob = estimate_circuit_success_probability(
            circuit_info["gates"],
            list(range(circuit_info["num_qubits"])),
            hardware_profile
        )
        
        # Calcular puntuación de compatibilidad (0-100)
        # Factores: probabilidad de éxito, tiempo de ejecución relativo, compatibilidad de puertas
        max_expected_time = 5000000  # 5ms como referencia máxima
        time_score = max(0, 100 * (1 - execution_time / max_expected_time))
        success_score = success_prob * 100
        
        # Verificar compatibilidad de puertas
        required_gates = set(circuit_info["gates"])
        available_gates = set(hardware_profile.gate_parameters.keys())
        missing_gates = required_gates - available_gates
        gate_compatibility = 100 * (len(required_gates) - len(missing_gates)) / len(required_gates) if required_gates else 100
        
        # Puntuación final (promedio ponderado)
        final_score = 0.5 * success_score + 0.3 * time_score + 0.2 * gate_compatibility
        
        results[circuit_name] = {
            "status": "compatible",
            "execution_time_ns": execution_time,
            "success_probability": success_prob,
            "missing_gates": list(missing_gates) if missing_gates else None,
            "gate_compatibility_score": gate_compatibility,
            "time_efficiency_score": time_score,
            "success_score": success_score,
            "overall_score": final_score
        }
    
    return results

def compare_hardware_profiles(profiles: List[HardwareProfile], 
                             circuit_gates: Optional[List[str]] = None) -> HardwareComparison:
    """Comparar múltiples perfiles de hardware para un circuito dado"""
    metrics = {
        "Tiempo de ejecución (ns)": {},
        "Fidelidad promedio de puertas": {},
        "Error promedio de lectura": {},
        "Tiempo de coherencia T1 promedio (μs)": {},
        "Tiempo de coherencia T2 promedio (μs)": {},
        "Conectividad (conexiones/qubit)": {},
    }
    
    # Circuito de prueba por defecto si no se proporciona uno
    if circuit_gates is None:
        circuit_gates = ["H", "CNOT", "X", "CNOT", "H", "Z", "CNOT", "X", "Y", "H"]
    
    for profile in profiles:
        # Tiempo de ejecución
        metrics["Tiempo de ejecución (ns)"][profile.name] = estimate_circuit_execution_time(circuit_gates, profile)
        
        # Fidelidad promedio de puertas
        avg_fidelity = sum(p.fidelity for p in profile.gate_parameters.values()) / len(profile.gate_parameters)
        metrics["Fidelidad promedio de puertas"][profile.name] = avg_fidelity
        
        # Error promedio de lectura
        avg_readout_error = sum(q.readout_error for q in profile.qubit_parameters) / len(profile.qubit_parameters)
        metrics["Error promedio de lectura"][profile.name] = avg_readout_error
        
        # Tiempos de coherencia promedio
        avg_t1 = sum(q.t1_us for q in profile.qubit_parameters) / len(profile.qubit_parameters)
        avg_t2 = sum(q.t2_us for q in profile.qubit_parameters) / len(profile.qubit_parameters)
        metrics["Tiempo de coherencia T1 promedio (μs)"][profile.name] = avg_t1
        metrics["Tiempo de coherencia T2 promedio (μs)"][profile.name] = avg_t2
        
        # Conectividad
        total_connections = sum(sum(row) for row in profile.connectivity.adjacency_matrix)
        avg_connections_per_qubit = total_connections / profile.num_qubits
        metrics["Conectividad (conexiones/qubit)"][profile.name] = avg_connections_per_qubit
    
    return HardwareComparison(profiles=profiles, metrics=metrics)