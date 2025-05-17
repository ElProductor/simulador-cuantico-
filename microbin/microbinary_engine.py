import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from core.qubit import Qubit
from core.bit import Bit
import json
import logging

MICRO_BIN_TABLE ={
    "INIT_TEMP":"0001",
    "READ_TEMP":"0010",
    "ACTIVATE_COOLER":"0100",
}

def encode_micro(command):
    MICRO_BIN_TABLE = {
        "INIT_TEMP": "0001",
        "READ_TEMP": "0010",
        "ACTIVATE_COOLER": "0100",
    }
    return MICRO_BIN_TABLE.get(command, "0000")  # return 0000 for unknown commands

class MicrobinaryEngine:
    """
    Motor avanzado para manejar operaciones cuánticas y clásicas híbridas.
    Provee funcionalidades de optimización, tracking y análisis.
    """
    
    def __init__(self):
        self.qubits = {}  # Dict[str, Qubit]
        self.bits = {}    # Dict[str, Bit]
        self.operations = []  # List[Dict]
        self.history = []     # List[Dict]
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura el sistema de logging."""
        self.logger = logging.getLogger('MicrobinaryEngine')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo
        fh = logging.FileHandler('microbinary.log')
        fh.setLevel(logging.DEBUG)
        
        # Handler para consola
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def create_qubit(self, name: str) -> bool:
        """
        Crea un nuevo qubit.
        
        Args:
            name: Nombre del qubit
            
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            if name in self.qubits:
                self.logger.warning(f"Qubit {name} ya existe")
                return False
            self.qubits[name] = Qubit(name)
            self._log_operation('create_qubit', {'name': name})
            return True
        except Exception as e:
            self.logger.error(f"Error al crear qubit {name}: {str(e)}")
            return False

    def create_bit(self, name: str) -> bool:
        """
        Crea un nuevo bit clásico.
        
        Args:
            name: Nombre del bit
            
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            if name in self.bits:
                self.logger.warning(f"Bit {name} ya existe")
                return False
            self.bits[name] = Bit(name)
            self._log_operation('create_bit', {'name': name})
            return True
        except Exception as e:
            self.logger.error(f"Error al crear bit {name}: {str(e)}")
            return False

    def apply_gate(self, gate: str, targets: List[str], 
                  controls: Optional[List[str]] = None) -> bool:
        """
        Aplica una puerta cuántica o clásica.
        
        Args:
            gate: Nombre de la puerta
            targets: Lista de qubits/bits objetivo
            controls: Lista opcional de qubits/bits de control
            
        Returns:
            bool: True si se aplicó exitosamente
        """
        try:
            if gate in ['H', 'X', 'Y', 'Z', 'RHW']:
                # Puertas cuánticas de un qubit
                if len(targets) != 1:
                    raise ValueError("Puertas de un qubit requieren un target")
                target = targets[0]
                if target not in self.qubits:
                    raise ValueError(f"Qubit {target} no existe")
                    
                matrix = self._get_gate_matrix(gate)
                self.qubits[target].apply_gate(matrix)
                self._log_operation('single_gate', {
                    'gate': gate,
                    'target': target
                })
                
            elif gate in ['CNOT', 'CZ', 'SWAP']:
                # Puertas cuánticas de dos qubits
                if not controls or len(controls) != 1:
                    raise ValueError("Puertas controladas requieren un control")
                if len(targets) != 1:
                    raise ValueError("Puertas controladas requieren un target")
                    
                control, target = controls[0], targets[0]
                if control not in self.qubits or target not in self.qubits:
                    raise ValueError("Control o target no existen")
                    
                matrix = self._get_gate_matrix(gate)
                self._apply_controlled_gate(matrix, control, target)
                self._log_operation('controlled_gate', {
                    'gate': gate,
                    'control': control,
                    'target': target
                })
                
            elif gate in ['AND', 'OR', 'XOR', 'NAND', 'NOR', 'NOT']:
                # Puertas clásicas
                if gate == 'NOT':
                    if len(targets) != 1:
                        raise ValueError("NOT requiere un target")
                    target = targets[0]
                    if target not in self.bits:
                        raise ValueError(f"Bit {target} no existe")
                        
                    result = not self.bits[target].get_state()
                    self.bits[target].set_state(result)
                    self._log_operation('classical_not', {
                        'target': target,
                        'result': result
                    })
                else:
                    if len(targets) != 2:
                        raise ValueError(f"{gate} requiere dos targets")
                    bit1, bit2 = targets
                    if bit1 not in self.bits or bit2 not in self.bits:
                        raise ValueError("Uno o ambos bits no existen")
                        
                    result = self._apply_classical_gate(gate, bit1, bit2)
                    self._log_operation('classical_gate', {
                        'gate': gate,
                        'bit1': bit1,
                        'bit2': bit2,
                        'result': result
                    })
                    
            else:
                raise ValueError(f"Puerta {gate} no reconocida")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error al aplicar puerta {gate}: {str(e)}")
            return False

    def measure(self, target: str) -> Optional[int]:
        """
        Mide un qubit o lee un bit.
        
        Args:
            target: Nombre del qubit/bit
            
        Returns:
            Optional[int]: Resultado de la medición o None si hay error
        """
        try:
            if target in self.qubits:
                result = self.qubits[target].measure()
                self._log_operation('measure_qubit', {
                    'target': target,
                    'result': result
                })
                return result
            elif target in self.bits:
                result = self.bits[target].get_state()
                self._log_operation('read_bit', {
                    'target': target,
                    'result': result
                })
                return result
            else:
                raise ValueError(f"{target} no existe")
                
        except Exception as e:
            self.logger.error(f"Error al medir {target}: {str(e)}")
            return None

    def get_state(self, target: str) -> Optional[Any]:
        """
        Obtiene el estado de un qubit/bit sin medirlo.
        
        Args:
            target: Nombre del qubit/bit
            
        Returns:
            Optional[Any]: Estado actual o None si hay error
        """
        try:
            if target in self.qubits:
                return self.qubits[target].state
            elif target in self.bits:
                return self.bits[target].get_state()
            else:
                raise ValueError(f"{target} no existe")
                
        except Exception as e:
            self.logger.error(f"Error al obtener estado de {target}: {str(e)}")
            return None

    def get_density_matrix(self, qubit: str) -> Optional[np.ndarray]:
        """
        Calcula la matriz de densidad de un qubit.
        
        Args:
            qubit: Nombre del qubit
            
        Returns:
            Optional[np.ndarray]: Matriz de densidad o None si hay error
        """
        try:
            if qubit not in self.qubits:
                raise ValueError(f"Qubit {qubit} no existe")
                
            state = self.qubits[qubit].state
            # |ψ⟩⟨ψ|
            return np.outer(state, state.conj())
            
        except Exception as e:
            self.logger.error(f"Error al calcular matriz de densidad: {str(e)}")
            return None

    def get_fidelity(self, qubit1: str, qubit2: str) -> Optional[float]:
        """
        Calcula la fidelidad entre dos estados cuánticos.
        
        Args:
            qubit1: Primer qubit
            qubit2: Segundo qubit
            
        Returns:
            Optional[float]: Fidelidad entre 0 y 1, o None si hay error
        """
        try:
            if qubit1 not in self.qubits or qubit2 not in self.qubits:
                raise ValueError("Uno o ambos qubits no existen")
                
            state1 = self.qubits[qubit1].state
            state2 = self.qubits[qubit2].state
            
            # F = |⟨ψ₁|ψ₂⟩|²
            fidelity = abs(np.vdot(state1, state2))**2
            return float(fidelity)  # Convert from np.float to Python float
            
        except Exception as e:
            self.logger.error(f"Error al calcular fidelidad: {str(e)}")
            return None

    def get_purity(self, qubit: str) -> Optional[float]:
        """
        Calcula la pureza de un estado cuántico.
        
        Args:
            qubit: Nombre del qubit
            
        Returns:
            Optional[float]: Pureza entre 0.5 y 1, o None si hay error
        """
        try:
            if qubit not in self.qubits:
                raise ValueError(f"Qubit {qubit} no existe")
                
            rho = self.get_density_matrix(qubit)
            if rho is None:
                return None
                
            # Tr(ρ²)
            purity = float(np.trace(rho @ rho))
            return purity
            
        except Exception as e:
            self.logger.error(f"Error al calcular pureza: {str(e)}")
            return None

    def get_coherence(self, qubit: str) -> Optional[float]:
        """
        Calcula la coherencia cuántica usando la norma l1.
        
        Args:
            qubit: Nombre del qubit
            
        Returns:
            Optional[float]: Medida de coherencia, o None si hay error
        """
        try:
            if qubit not in self.qubits:
                raise ValueError(f"Qubit {qubit} no existe")
                
            rho = self.get_density_matrix(qubit)
            if rho is None:
                return None
                
            # Suma de elementos no diagonales
            off_diag_sum = np.sum(np.abs(rho - np.diag(np.diag(rho))))
            return float(off_diag_sum)
            
        except Exception as e:
            self.logger.error(f"Error al calcular coherencia: {str(e)}")
            return None

    def get_entanglement_measure(self, qubit1: str, qubit2: str) -> Optional[float]:
        """
        Calcula una medida de entrelazamiento entre dos qubits.
        
        Args:
            qubit1: Primer qubit
            qubit2: Segundo qubit
            
        Returns:
            Optional[float]: Medida de entrelazamiento, o None si hay error
        """
        try:
            if qubit1 not in self.qubits or qubit2 not in self.qubits:
                raise ValueError("Uno o ambos qubits no existen")
                
            state1 = self.qubits[qubit1].state
            state2 = self.qubits[qubit2].state
            
            # Medida simple basada en correlación
            # 0 = no entrelazados, 1 = máximo entrelazamiento
            correlation = abs(np.vdot(state1, state2))
            return float(2 * abs(correlation - 0.5))
            
        except Exception as e:
            self.logger.error(f"Error al calcular entrelazamiento: {str(e)}")
            return None

    def optimize_circuit(self) -> bool:
        """
        Optimiza el circuito actual eliminando operaciones redundantes.
        
        Returns:
            bool: True si se optimizó exitosamente
        """
        try:
            # Lista de optimizaciones a aplicar
            optimizations = [
                self._remove_adjacent_pairs,
                self._combine_rotations,
                self._merge_cnots,
                self._remove_identity
            ]
            
            # Aplicar cada optimización
            for opt in optimizations:
                self.operations = opt(self.operations)
                
            self._log_operation('optimize', {
                'original_length': len(self.operations),
                'optimized_length': len(self.operations)
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Error al optimizar circuito: {str(e)}")
            return False

    def save_state(self, filename: str) -> bool:
        """
        Guarda el estado actual del motor en un archivo JSON.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            state = {
                'qubits': {},
                'bits': {},
                'operations': self.operations,
                'history': self.history
            }
            
            # Convertir estados cuánticos a formato serializable
            for name, qubit in self.qubits.items():
                state['qubits'][name] = {
                    'state': [complex(x) for x in qubit.state],
                    'entangled_with': list(qubit.entangled_with)
                }
                
            # Guardar estados de bits
            for name, bit in self.bits.items():
                state['bits'][name] = bit.get_state()
                
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar estado: {str(e)}")
            return False

    def load_state(self, filename: str) -> bool:
        """
        Carga un estado guardado desde un archivo JSON.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
                
            # Recrear qubits
            self.qubits = {}
            for name, data in state['qubits'].items():
                qubit = Qubit(name)
                qubit.state = np.array([complex(x) for x in data['state']])
                qubit.entangled_with = set(data['entangled_with'])
                self.qubits[name] = qubit
                
            # Recrear bits
            self.bits = {}
            for name, value in state['bits'].items():
                bit = Bit(name)
                bit.set_state(value)
                self.bits[name] = bit
                
            self.operations = state['operations']
            self.history = state['history']
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar estado: {str(e)}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Calcula métricas del circuito actual.
        
        Returns:
            Dict[str, Any]: Diccionario con métricas
        """
        try:
            metrics = {
                'circuit_depth': len(self.operations),
                'qubit_count': len(self.qubits),
                'bit_count': len(self.bits),
                'gate_counts': {}
            }
            
            # Contar tipos de puertas
            for op in self.operations:
                gate = op.get('gate', '')
                metrics['gate_counts'][gate] = \
                    metrics['gate_counts'].get(gate, 0) + 1
                    
            # Calcular métricas cuánticas
            metrics['quantum_metrics'] = {}
            for name in self.qubits:
                metrics['quantum_metrics'][name] = {
                    'purity': self.get_purity(name),
                    'coherence': self.get_coherence(name)
                }
                
            # Calcular entrelazamiento entre pares
            metrics['entanglement'] = {}
            qubit_list = list(self.qubits.keys())
            for i in range(len(qubit_list)):
                for j in range(i+1, len(qubit_list)):
                    q1, q2 = qubit_list[i], qubit_list[j]
                    metrics['entanglement'][f"{q1}-{q2}"] = \
                        self.get_entanglement_measure(q1, q2)
                        
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error al calcular métricas: {str(e)}")
            return {}

    def _log_operation(self, op_type: str, details: Dict[str, Any]) -> None:
        """
        Registra una operación en el historial.
        
        Args:
            op_type: Tipo de operación
            details: Detalles de la operación
        """
        entry = {
            'type': op_type,
            'details': details,
            'timestamp': str(np.datetime64('now'))
        }
        self.history.append(entry)
        self.logger.debug(f"Operación registrada: {entry}")

    def _get_gate_matrix(self, gate: str) -> np.ndarray:
        """
        Obtiene la matriz de una puerta cuántica.
        
        Args:
            gate: Nombre de la puerta
            
        Returns:
            np.ndarray: Matriz de la puerta
        """
        from gates.quantum_gates import H, X, Y, Z, RHW, CNOT, CZ, SWAP
        gates = {
            'H': H, 'X': X, 'Y': Y, 'Z': Z, 'RHW': RHW,
            'CNOT': CNOT, 'CZ': CZ, 'SWAP': SWAP
        }
        return gates[gate]

    def _apply_controlled_gate(self, matrix: np.ndarray,
                             control: str, target: str) -> None:
        """
        Aplica una puerta controlada.
        
        Args:
            matrix: Matriz de la puerta
            control: Qubit de control
            target: Qubit objetivo
        """
        control_qubit = self.qubits[control]
        target_qubit = self.qubits[target]
        control_qubit.entangled_with.add(target)
        target_qubit.entangled_with.add(control)
        
        from gates.quantum_gates import apply_two_qubit_gate
        state1, state2 = apply_two_qubit_gate(
            matrix, control_qubit.state, target_qubit.state)
        control_qubit.state = state1
        target_qubit.state = state2

    def _apply_classical_gate(self, gate: str, bit1: str, bit2: str) -> int:
        """
        Aplica una puerta clásica.
        
        Args:
            gate: Tipo de puerta
            bit1: Primer bit
            bit2: Segundo bit
            
        Returns:
            int: Resultado de la operación
        """
        from gates.classical_gates import (
            and_gate, or_gate, xor_gate, nand_gate, nor_gate
        )
        
        gates = {
            'AND': and_gate,
            'OR': or_gate,
            'XOR': xor_gate,
            'NAND': nand_gate,
            'NOR': nor_gate
        }
        
        return int(gates[gate](self.bits[bit1], self.bits[bit2]))

    def _remove_adjacent_pairs(self, ops: List[Dict]) -> List[Dict]:
        """
        Elimina pares de puertas idénticas adyacentes.
        
        Args:
            ops: Lista de operaciones
            
        Returns:
            List[Dict]: Lista optimizada
        """
        i = 0
        result = []
        while i < len(ops):
            if i + 1 < len(ops) and ops[i] == ops[i+1]:
                i += 2  # Saltar ambas operaciones
            else:
                result.append(ops[i])
                i += 1
        return result

    def _combine_rotations(self, ops: List[Dict]) -> List[Dict]:
        """
        Combina rotaciones consecutivas del mismo tipo.
        
        Args:
            ops: Lista de operaciones
            
        Returns:
            List[Dict]: Lista optimizada
        """
        # TODO: Implementar combinación de rotaciones
        return ops

    def _merge_cnots(self, ops: List[Dict]) -> List[Dict]:
        """
        Fusiona operaciones CNOT que pueden combinarse.
        
        Args:
            ops: Lista de operaciones
            
        Returns:
            List[Dict]: Lista optimizada
        """
        # TODO: Implementar fusión de CNOTs
        return ops

    def _remove_identity(self, ops: List[Dict]) -> List[Dict]:
        """
        Elimina secuencias que equivalen a la identidad.
        
        Args:
            ops: Lista de operaciones
            
        Returns:
            List[Dict]: Lista optimizada
        """
        # Patrones conocidos que dan identidad
        identity_patterns = [
            # H-H
            [{'gate': 'H'}, {'gate': 'H'}],
            # X-X
            [{'gate': 'X'}, {'gate': 'X'}],
            # Z-Z
            [{'gate': 'Z'}, {'gate': 'Z'}],
            # Y-Y
            [{'gate': 'Y'}, {'gate': 'Y'}]
        ]
        
        # Buscar y eliminar patrones
        result = []
        i = 0
        while i < len(ops):
            matched = False
            for pattern in identity_patterns:
                if (i + len(pattern) <= len(ops) and
                    all(ops[i+j]['gate'] == p['gate']
                        for j, p in enumerate(pattern))):
                    i += len(pattern)
                    matched = True
                    break
            if not matched:
                result.append(ops[i])
                i += 1
                
        return result