import numpy as np
from typing import List, Set, Dict, Optional
import random

class Qubit:
    """Representa un qubit con estado y operaciones cuánticas."""
    
    def __init__(self, name: str):
        """
        Inicializa un qubit en estado |0⟩.
        
        Args:
            name: Nombre del qubit
        """
        self.name = name
        self._state = np.array([1, 0], dtype=complex)
        self.entangled_with: Set[str] = set()
        self._history: List[Dict] = []
        
    @property
    def state(self) -> np.ndarray:
        """Estado actual del qubit."""
        return self._state
        
    @state.setter
    def state(self, new_state: np.ndarray):
        """
        Actualiza el estado del qubit.
        
        Args:
            new_state: Nuevo estado
        
        Raises:
            ValueError: Si el estado no es válido
        """
        if not isinstance(new_state, np.ndarray):
            raise ValueError("El estado debe ser un array numpy")
            
        if new_state.shape != (2,):
            raise ValueError("El estado debe tener dimensión 2")
            
        # Verificar normalización
        if not np.isclose(np.linalg.norm(new_state), 1):
            raise ValueError("El estado debe estar normalizado")
            
        self._state = new_state.astype(complex)
        self._log_state_change()
        
    def apply_gate(self, gate: np.ndarray) -> None:
        """
        Aplica una puerta cuántica al qubit.
        
        Args:
            gate: Matriz de la puerta
            
        Raises:
            ValueError: Si la puerta no es válida
        """
        if not isinstance(gate, np.ndarray):
            raise ValueError("La puerta debe ser un array numpy")
            
        if gate.shape != (2, 2):
            raise ValueError("La puerta debe ser 2x2")
            
        # Verificar unitariedad
        if not np.allclose(gate @ gate.conj().T, np.eye(2)):
            raise ValueError("La puerta debe ser unitaria")
            
        self._state = gate @ self._state
        # Asegurar normalización después de la operación
        self._state = self._state / np.linalg.norm(self._state)
        self._log_gate_application(gate)
        
    def measure(self) -> int:
        """
        Mide el qubit en la base computacional.
        
        Returns:
            int: Resultado de la medición (0 o 1)
        """
        prob_0 = abs(self._state[0])**2
        outcome = 0 if random.random() < prob_0 else 1
        
        # Colapsar estado
        self._state = np.array([1, 0], dtype=complex) if outcome == 0 \
                     else np.array([0, 1], dtype=complex)
                     
        self._log_measurement(outcome)
        return outcome
        
    def get_bloch_coords(self) -> Dict[str, float]:
        """
        Calcula las coordenadas en la esfera de Bloch.
        
        Returns:
            Dict[str, float]: Coordenadas x, y, z
        """
        # Calcular matrices de Pauli
        sigma_x = np.array([[0, 1], [1, 0]])
        sigma_y = np.array([[0, -1j], [1j, 0]])
        sigma_z = np.array([[1, 0], [0, -1]])
        
        # Calcular valores esperados
        x = float(np.real(self._state.conj() @ sigma_x @ self._state))
        y = float(np.real(self._state.conj() @ sigma_y @ self._state))
        z = float(np.real(self._state.conj() @ sigma_z @ self._state))
        
        return {'x': x, 'y': y, 'z': z}
        
    def get_density_matrix(self) -> np.ndarray:
        """
        Calcula la matriz de densidad.
        
        Returns:
            np.ndarray: Matriz de densidad
        """
        return np.outer(self._state, self._state.conj())
        
    def get_probabilities(self) -> Dict[str, float]:
        """
        Calcula probabilidades de los estados base.
        
        Returns:
            Dict[str, float]: Probabilidades de |0⟩ y |1⟩
        """
        return {
            '|0⟩': float(abs(self._state[0])**2),
            '|1⟩': float(abs(self._state[1])**2)
        }
        
    def get_phase(self) -> Dict[str, float]:
        """
        Calcula las fases relativas.
        
        Returns:
            Dict[str, float]: Fases de las amplitudes
        """
        return {
            '|0⟩': float(np.angle(self._state[0])),
            '|1⟩': float(np.angle(self._state[1]))
        }
        
    def get_purity(self) -> float:
        """
        Calcula la pureza del estado.
        
        Returns:
            float: Pureza entre 0.5 y 1
        """
        rho = self.get_density_matrix()
        return float(np.real(np.trace(rho @ rho)))
        
    def get_coherence(self) -> float:
        """
        Calcula la coherencia cuántica.
        
        Returns:
            float: Medida de coherencia
        """
        rho = self.get_density_matrix()
        # Usar norma l1 de elementos no diagonales
        return float(np.sum(np.abs(rho - np.diag(np.diag(rho)))))
        
    def get_fidelity(self, other: 'Qubit') -> float:
        """
        Calcula la fidelidad con otro estado.
        
        Args:
            other: Otro qubit
            
        Returns:
            float: Fidelidad entre 0 y 1
        """
        return float(abs(np.vdot(self._state, other.state))**2)
        
    def get_history(self) -> List[Dict]:
        """
        Obtiene el historial de operaciones.
        
        Returns:
            List[Dict]: Lista de operaciones realizadas
        """
        return self._history.copy()
        
    def reset(self) -> None:
        """Reinicia el qubit al estado |0⟩."""
        self._state = np.array([1, 0], dtype=complex)
        self.entangled_with.clear()
        self._history.clear()
        self._log_state_change()
        
    def _log_state_change(self) -> None:
        """Registra un cambio de estado."""
        self._history.append({
            'type': 'state_change',
            'state': self._state.copy(),
            'probabilities': self.get_probabilities(),
            'bloch_coords': self.get_bloch_coords()
        })
        
    def _log_gate_application(self, gate: np.ndarray) -> None:
        """
        Registra la aplicación de una puerta.
        
        Args:
            gate: Matriz de la puerta aplicada
        """
        self._history.append({
            'type': 'gate',
            'matrix': gate.copy(),
            'resulting_state': self._state.copy()
        })
        
    def _log_measurement(self, outcome: int) -> None:
        """
        Registra una medición.
        
        Args:
             outcome: Resultado de la medición
        """
        self._history.append({
            'type': 'measurement',
            'outcome': outcome,
            'state_before': self._state.copy()
        })
