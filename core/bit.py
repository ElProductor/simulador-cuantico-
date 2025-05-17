from typing import List, Dict, Union
from dataclasses import dataclass, field
import time

@dataclass
class BitState:
    """Estado de un bit con metadatos."""
    value: int
    timestamp: float = field(default_factory=time.time)
    source: str = "manual"
    description: str = ""

class Bit:
    """
    Representa un bit clásico con estado y operaciones.
    Incluye registro de cambios y estadísticas.
    """
    
    def __init__(self, name: str, initial_state: int = 0):
        """
        Inicializa un bit.
        
        Args:
            name: Nombre del bit
            initial_state: Estado inicial (0 o 1)
        """
        if initial_state not in [0, 1]:
            raise ValueError("El estado debe ser 0 o 1")
            
        self.name = name
        self._history: List[BitState] = []
        self._state = BitState(initial_state)
        self._record_state("initialization")
        
    def set_state(self, value: int, source: str = "manual") -> None:
        """
        Establece el estado del bit.
        
        Args:
            value: Nuevo estado (0 o 1)
            source: Fuente del cambio
        """
        if value not in [0, 1]:
            raise ValueError("El estado debe ser 0 o 1")
            
        self._state = BitState(value, time.time(), source)
        self._record_state(f"set to {value}")
        
    def get_state(self) -> int:
        """
        Obtiene el estado actual.
        
        Returns:
            int: Estado actual (0 o 1)
        """
        return self._state.value
        
    def toggle(self) -> None:
        """Invierte el estado del bit."""
        new_value = 1 - self._state.value
        self.set_state(new_value, "toggle")
        
    def get_history(self) -> List[BitState]:
        """
        Obtiene el historial de estados.
        
        Returns:
            List[BitState]: Historial completo
        """
        return self._history.copy()
        
    def get_statistics(self) -> Dict[str, Union[int, float]]:
        """
        Calcula estadísticas del bit.
        
        Returns:
            Dict: Estadísticas de uso
        """
        if not self._history:
            return {}
            
        # Conteo de estados
        zeros = sum(1 for state in self._history if state.value == 0)
        ones = sum(1 for state in self._history if state.value == 1)
        
        # Duración total y promedio en cada estado
        total_time = self._history[-1].timestamp - self._history[0].timestamp
        time_in_zero = 0
        time_in_one = 0
        
        for i in range(len(self._history) - 1):
            duration = self._history[i+1].timestamp - self._history[i].timestamp
            if self._history[i].value == 0:
                time_in_zero += duration
            else:
                time_in_one += duration
                
        return {
            'total_changes': len(self._history) - 1,
            'zero_count': zeros,
            'one_count': ones,
            'total_time': total_time,
            'time_in_zero': time_in_zero,
            'time_in_one': time_in_one,
            'average_time_zero': time_in_zero/zeros if zeros > 0 else 0,
            'average_time_one': time_in_one/ones if ones > 0 else 0
        }
        
    def get_transition_counts(self) -> Dict[str, int]:
        """
        Cuenta las transiciones entre estados.
        
        Returns:
            Dict: Conteo de transiciones
        """
        transitions = {'0->0': 0, '0->1': 0, '1->0': 0, '1->1': 0}
        
        for i in range(len(self._history) - 1):
            prev = str(self._history[i].value)
            curr = str(self._history[i+1].value)
            transitions[f'{prev}->{curr}'] += 1
            
        return transitions
        
    def get_stability_metric(self) -> float:
        """
        Calcula una métrica de estabilidad.
        
        Returns:
            float: Métrica entre 0 (inestable) y 1 (estable)
        """
        if len(self._history) < 2:
            return 1.0
            
        changes = sum(1 for i in range(len(self._history)-1)
                     if self._history[i].value != self._history[i+1].value)
        return 1 - (changes / (len(self._history) - 1))
        
    def get_state_summary(self) -> str:
        """
        Genera un resumen del estado actual.
        
        Returns:
            str: Resumen formateado
        """
        stats = self.get_statistics()
        if not stats:
            return f"Bit '{self.name}' en estado {self._state.value}"
            
        return (
            f"Bit '{self.name}':\n"
            f"  Estado actual: {self._state.value}\n"
            f"  Cambios totales: {stats['total_changes']}\n"
            f"  Tiempo en 0: {stats['time_in_zero']:.2f}s\n"
            f"  Tiempo en 1: {stats['time_in_one']:.2f}s\n"
            f"  Estabilidad: {self.get_stability_metric():.2%}"
        )
        
    def _record_state(self, description: str) -> None:
        """
        Registra un cambio de estado.
        
        Args:
            description: Descripción del cambio
        """
        state = BitState(
            value=self._state.value,
            timestamp=self._state.timestamp,
            source=self._state.source,
            description=description
        )
        self._history.append(state)