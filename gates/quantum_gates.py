import numpy as np
from typing import List, Dict, Optional, Tuple
from core.qubit import Qubit

# Puertas fundamentales de un qubit
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)  # Hadamard
X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X (NOT)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y 
Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
I = np.array([[1, 0], [0, 1]], dtype=complex)  # Identidad
S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
T = np.array([[1, 0], [0, np.exp(1j * np.pi/4)]], dtype=complex)  # π/8 gate
Sdg = S.conj().T  # S dagger
Tdg = T.conj().T  # T dagger
RHW = np.array([[0, 1j], [1j, 0]], dtype=complex)  # Root of Hadamard-Walsh

# Puertas de dos qubits
CNOT = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0]
], dtype=complex)

CZ = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, -1]
], dtype=complex)

SWAP = np.array([
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1]
], dtype=complex)

# Puertas de rotación
def rx(theta: float) -> np.ndarray:
    """Rotación alrededor del eje X."""
    return np.array([
        [np.cos(theta/2), -1j*np.sin(theta/2)],
        [-1j*np.sin(theta/2), np.cos(theta/2)]
    ], dtype=complex)

def ry(theta: float) -> np.ndarray:
    """Rotación alrededor del eje Y."""
    return np.array([
        [np.cos(theta/2), -np.sin(theta/2)],
        [np.sin(theta/2), np.cos(theta/2)]
    ], dtype=complex)

def rz(theta: float) -> np.ndarray:
    """Rotación alrededor del eje Z."""
    return np.array([
        [np.exp(-1j*theta/2), 0],
        [0, np.exp(1j*theta/2)]
    ], dtype=complex)

def u3(theta: float, phi: float, lambda_: float) -> np.ndarray:
    """Puerta universal U3."""
    return np.array([
        [np.cos(theta/2), -np.exp(1j*lambda_)*np.sin(theta/2)],
        [np.exp(1j*phi)*np.sin(theta/2), np.exp(1j*(phi+lambda_))*np.cos(theta/2)]
    ], dtype=complex)

def controlled_rotation(axis: str, theta: float) -> np.ndarray:
    """
    Genera una puerta de rotación controlada.
    
    Args:
        axis: Eje de rotación ('x', 'y', 'z')
        theta: Ángulo de rotación
        
    Returns:
        np.ndarray: Matriz de la puerta
    """
    rotation = {'x': rx, 'y': ry, 'z': rz}[axis.lower()](theta)
    n = rotation.shape[0]
    result = np.eye(2*n, dtype=complex)
    result[n:2*n, n:2*n] = rotation
    return result

def tensor_product(*states: np.ndarray) -> np.ndarray:
    """
    Calcula el producto tensorial de múltiples estados.
    
    Args:
        states: Estados cuánticos
        
    Returns:
        np.ndarray: Producto tensorial
    """
    result = states[0]
    for state in states[1:]:
        result = np.kron(result, state)
    return result

def apply_two_qubit_gate(gate: np.ndarray, control: Qubit, target: Qubit) -> Tuple[np.ndarray, np.ndarray]:
    """
    Aplica una puerta de dos qubits.
    
    Args:
        gate: Matriz de la puerta
        control: Qubit de control
        target: Qubit objetivo
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: Estados resultantes
    """
    # Calcular estado conjunto
    state = tensor_product(control.state, target.state)
    
    # Aplicar puerta
    new_state = gate @ state
    
    # Separar estados (aproximado)
    n = len(control.state)
    control_state = new_state[:n].copy()
    target_state = new_state[n:].copy()
    
    # Normalizar
    control_state /= np.linalg.norm(control_state)
    target_state /= np.linalg.norm(target_state)
    
    return control_state, target_state

def optimize_circuit(operations: List[Dict]) -> List[Dict]:
    """
    Optimiza un circuito cuántico.
    
    Args:
        operations: Lista de operaciones
        
    Returns:
        List[Dict]: Circuito optimizado
    """
    # Reglas de optimización
    def cancel_adjacent_pairs(ops: List[Dict]) -> List[Dict]:
        """Cancela pares de puertas que se anulan."""
        result = []
        i = 0
        while i < len(ops):
            if i + 1 < len(ops):
                op1, op2 = ops[i], ops[i+1]
                # H-H, X-X, Y-Y, Z-Z
                if (op1['gate'] == op2['gate'] and
                    op1['type'] == 'single' and
                    op2['type'] == 'single' and
                    op1['target'] == op2['target'] and
                    op1['gate'] in ['H','X','Y','Z']):
                    i += 2
                    continue
            result.append(ops[i])
            i += 1
        return result

    def merge_rotations(ops: List[Dict]) -> List[Dict]:
        """Combina rotaciones consecutivas."""
        result = []
        i = 0
        while i < len(ops):
            if i + 1 < len(ops):
                op1, op2 = ops[i], ops[i+1]
                if (op1.get('type') == op2.get('type') == 'rotation' and
                    op1['axis'] == op2['axis'] and
                    op1['target'] == op2['target']):
                    # Sumar ángulos
                    theta = op1['theta'] + op2['theta']
                    if abs(theta) > 1e-10:  # Si no se anula
                        result.append({
                            'type': 'rotation',
                            'gate': f'R{op1["axis"].upper()}',
                            'axis': op1['axis'],
                            'theta': theta,
                            'target': op1['target']
                        })
                    i += 2
                    continue
            result.append(ops[i])
            i += 1
        return result

    def optimize_cnots(ops: List[Dict]) -> List[Dict]:
        """Optimiza secuencias de CNOTs."""
        result = []
        i = 0
        while i < len(ops):
            if i + 1 < len(ops):
                op1, op2 = ops[i], ops[i+1]
                # CNOT(a,b)-CNOT(a,b) = I
                if (op1['gate'] == op2['gate'] == 'CNOT' and
                    op1['control'] == op2['control'] and
                    op1['target'] == op2['target']):
                    i += 2
                    continue
                # CNOT(a,b)-CNOT(b,a)-CNOT(a,b) = SWAP
                if (i + 2 < len(ops) and
                    all(op['gate'] == 'CNOT' for op in ops[i:i+3]) and
                    ops[i]['control'] == ops[i+2]['control'] and
                    ops[i]['target'] == ops[i+1]['control'] and
                    ops[i+1]['target'] == ops[i+2]['target']):
                    result.append({
                        'type': 'two',
                        'gate': 'SWAP',
                        'control': ops[i]['control'],
                        'target': ops[i]['target']
                    })
                    i += 3
                    continue
            result.append(ops[i])
            i += 1
        return result

    # Aplicar optimizaciones
    optimized = operations.copy()
    optimized = cancel_adjacent_pairs(optimized)
    optimized = merge_rotations(optimized)
    optimized = optimize_cnots(optimized)
    
    return optimized

def verify_circuit_identity(ops1: List[Dict], ops2: List[Dict], n_qubits: int) -> bool:
    """
    Verifica si dos circuitos son equivalentes.
    
    Args:
        ops1: Primer circuito
        ops2: Segundo circuito
        n_qubits: Número de qubits
        
    Returns:
        bool: True si son equivalentes
    """
    # Construir matrices de los circuitos
    def build_circuit_matrix(ops: List[Dict]) -> np.ndarray:
        dim = 2**n_qubits
        result = np.eye(dim, dtype=complex)
        
        for op in ops:
            if op['type'] == 'single':
                # Obtener matriz de la puerta
                gate_matrix = {
                    'H': H, 'X': X, 'Y': Y, 'Z': Z,
                    'S': S, 'T': T, 'RHW': RHW
                }[op['gate']]
                
                # Construir matriz completa
                target = op['target']
                before = np.eye(2**target, dtype=complex)
                after = np.eye(2**(n_qubits-target-1), dtype=complex)
                full_gate = tensor_product(before, gate_matrix, after)
                result = full_gate @ result
                
            elif op['type'] == 'two':
                gate_matrix = {'CNOT': CNOT, 'CZ': CZ, 'SWAP': SWAP}[op['gate']]
                control, target = op['control'], op['target']
                
                # Reordenar para tener control y target adyacentes
                perm = list(range(n_qubits))
                perm[control], perm[target] = target, control
                
                # Aplicar permutación
                perm_matrix = np.zeros((dim, dim), dtype=complex)
                for i in range(dim):
                    bits = [int(b) for b in format(i, f'0{n_qubits}b')]
                    permuted = int(''.join(str(bits[j]) for j in perm), 2)
                    perm_matrix[permuted,i] = 1
                    
                # Aplicar puerta
                result = perm_matrix.T @ gate_matrix @ perm_matrix @ result
                
        return result
        
    # Construir y comparar matrices
    U1 = build_circuit_matrix(ops1)
    U2 = build_circuit_matrix(ops2)
    
    # Comparar con tolerancia numérica
    return np.allclose(U1, U2, atol=1e-10)

def get_circuit_complexity(operations: List[Dict]) -> Dict[str, float]:
    """
    Calcula métricas de complejidad del circuito.
    
    Args:
        operations: Lista de operaciones
        
    Returns:
        Dict[str, float]: Métricas de complejidad
    """
    # Métricas básicas
    n_gates = len(operations)
    n_single = sum(1 for op in operations if op['type'] == 'single')
    n_two = sum(1 for op in operations if op['type'] == 'two')
    
    # Profundidad del circuito (niveles de paralelismo)
    def calculate_depth() -> int:
        if not operations:
            return 0
            
        # Encontrar dependencias entre operaciones
        deps = []
        for i, op1 in enumerate(operations):
            level = 0
            for j, op2 in enumerate(operations[:i]):
                # Operaciones en mismo qubit no pueden ser paralelas
                if (op1['type'] == 'single' and op2['type'] == 'single' and
                    op1['target'] == op2['target']):
                    level = max(level, deps[j] + 1)
                # Operaciones de dos qubits con overlap no pueden ser paralelas
                elif (op1['type'] == 'two' and op2['type'] == 'two' and
                      (op1['control'] == op2['control'] or
                       op1['control'] == op2['target'] or
                       op1['target'] == op2['control'] or
                       op1['target'] == op2['target'])):
                    level = max(level, deps[j] + 1)
            deps.append(level)
        return max(deps) + 1

    # Calcular entropía de distribución de puertas
    def calculate_gate_entropy() -> float:
        from collections import Counter
        import math
        
        counts = Counter(op['gate'] for op in operations)
        total = sum(counts.values())
        probs = [count/total for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    return {
        'n_gates': n_gates,
        'n_single': n_single,
        'n_two': n_two,
        'depth': calculate_depth(),
        'gate_entropy': calculate_gate_entropy()
    }

def get_circuit_qasm(operations: List[Dict]) -> str:
    """
    Genera código QASM.
    
    Args:
        operations: Lista de operaciones
        
    Returns:
        str: Código QASM
    """
    qasm = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n\n"
    
    # Encontrar qubits usados
    qubits = set()
    for op in operations:
        qubits.add(op['target'])
        if 'control' in op:
            qubits.add(op['control'])
    
    # Declarar registros
    n_qubits = max(qubits) + 1
    qasm += f"qreg q[{n_qubits}];\n"
    qasm += f"creg c[{n_qubits}];\n\n"
    
    # Mapeo de nombres
    gate_names = {
        'H': 'h', 'X': 'x', 'Y': 'y', 'Z': 'z',
        'S': 's', 'T': 't', 'RHW': 'rhw',
        'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap'
    }
    
    # Generar instrucciones
    for op in operations:
        gate = gate_names[op['gate']]
        if op['type'] == 'single':
            qasm += f"{gate} q[{op['target']}];\n"
        else:
            qasm += f"{gate} q[{op['control']}],q[{op['target']}];\n"
            
    return qasm
