from typing import List, Dict, Union, Optional, Callable
from core.bit import Bit
import time

def create_gate_function(truth_table: List[int]) -> Callable:
    """
    Crea una función de puerta desde una tabla de verdad.
    
    Args:
        truth_table: Lista con salidas para cada entrada
        
    Returns:
        Callable: Función que implementa la puerta
    """
    def gate_function(*bits: Bit) -> int:
        n = len(bits)
        if len(truth_table) != 2**n:
            raise ValueError("Tabla de verdad inválida")
            
        # Convertir estados de entrada a índice
        index = sum(bit.get_state() * 2**i for i, bit in enumerate(bits))
        return truth_table[index]
        
    return gate_function

# Puertas fundamentales
def not_gate(bit: Bit) -> int:
    """NOT lógico."""
    return 1 - bit.get_state()

def and_gate(bit1: Bit, bit2: Bit) -> int:
    """AND lógico."""
    return bit1.get_state() & bit2.get_state()

def or_gate(bit1: Bit, bit2: Bit) -> int:
    """OR lógico."""
    return bit1.get_state() | bit2.get_state()

def xor_gate(bit1: Bit, bit2: Bit) -> int:
    """XOR lógico."""
    return bit1.get_state() ^ bit2.get_state()

def nand_gate(bit1: Bit, bit2: Bit) -> int:
    """NAND lógico."""
    return 1 - and_gate(bit1, bit2)

def nor_gate(bit1: Bit, bit2: Bit) -> int:
    """NOR lógico."""
    return 1 - or_gate(bit1, bit2)

def xnor_gate(bit1: Bit, bit2: Bit) -> int:
    """XNOR lógico."""
    return 1 - xor_gate(bit1, bit2)

# Circuitos combinacionales
def half_adder(bit1: Bit, bit2: Bit) -> Dict[str, int]:
    """
    Sumador de medio bit.
    
    Args:
        bit1, bit2: Bits a sumar
        
    Returns:
        Dict[str, int]: Suma y acarreo
    """
    return {
        'sum': xor_gate(bit1, bit2),
        'carry': and_gate(bit1, bit2)
    }

def full_adder(bit1: Bit, bit2: Bit, carry_in: Bit) -> Dict[str, int]:
    """
    Sumador completo.
    
    Args:
        bit1, bit2: Bits a sumar
        carry_in: Acarreo de entrada
        
    Returns:
        Dict[str, int]: Suma y acarreo
    """
    # Primera etapa
    stage1 = half_adder(bit1, bit2)
    
    # Segunda etapa
    carry_bit = Bit('temp_carry')
    carry_bit.set_state(stage1['carry'])
    
    sum_bit = Bit('temp_sum')
    sum_bit.set_state(stage1['sum'])
    
    stage2 = half_adder(sum_bit, carry_in)
    
    return {
        'sum': stage2['sum'],
        'carry': or_gate(carry_bit, Bit('temp', stage2['carry']))
    }

def multiplexer_2to1(data0: Bit, data1: Bit, select: Bit) -> int:
    """
    Multiplexor 2 a 1.
    
    Args:
        data0, data1: Entradas de datos
        select: Bit de selección
        
    Returns:
        int: Salida seleccionada
    """
    s = select.get_state()
    return data1.get_state() if s else data0.get_state()

def demultiplexer_1to2(data: Bit, select: Bit) -> Dict[str, int]:
    """
    Demultiplexor 1 a 2.
    
    Args:
        data: Entrada de datos
        select: Bit de selección
        
    Returns:
        Dict[str, int]: Salidas
    """
    s = select.get_state()
    d = data.get_state()
    return {
        'out0': d if not s else 0,
        'out1': d if s else 0
    }

def decoder_2to4(bit1: Bit, bit2: Bit) -> List[int]:
    """
    Decodificador 2 a 4.
    
    Args:
        bit1, bit2: Bits de entrada
        
    Returns:
        List[int]: Salidas decodificadas
    """
    b1, b2 = bit1.get_state(), bit2.get_state()
    index = (b1 << 1) | b2
    return [1 if i == index else 0 for i in range(4)]

def encoder_4to2(inputs: List[Bit]) -> Dict[str, int]:
    """
    Codificador 4 a 2.
    
    Args:
        inputs: Lista de 4 bits de entrada
        
    Returns:
        Dict[str, int]: Bits codificados
    """
    if len(inputs) != 4:
        raise ValueError("Se requieren 4 bits de entrada")
        
    # Encontrar posición del 1
    pos = -1
    for i, bit in enumerate(inputs):
        if bit.get_state() == 1:
            if pos != -1:  # Ya se encontró un 1
                raise ValueError("Codificador: entrada inválida")
            pos = i
            
    if pos == -1:
        raise ValueError("Codificador: no hay entrada activa")
        
    # Convertir a binario
    return {
        'out1': (pos >> 1) & 1,
        'out0': pos & 1
    }

def parity_generator(bits: List[Bit], even: bool = True) -> int:
    """
    Generador de paridad.
    
    Args:
        bits: Lista de bits
        even: True para paridad par, False para impar
        
    Returns:
        int: Bit de paridad
    """
    count = sum(bit.get_state() for bit in bits)
    return (count + (0 if even else 1)) % 2

def majority_voter(bits: List[Bit]) -> int:
    """
    Votador por mayoría.
    
    Args:
        bits: Lista de bits (típicamente 3)
        
    Returns:
        int: Valor mayoritario
    """
    count = sum(bit.get_state() for bit in bits)
    return 1 if count > len(bits)//2 else 0

# Circuitos secuenciales básicos
class SRLatch:
    """Latch SR."""
    
    def __init__(self):
        self.state = 0
        self._history: List[Dict] = []
        
    def update(self, s: int, r: int) -> int:
        """
        Actualiza el estado del latch.
        
        Args:
            s: Set
            r: Reset
            
        Returns:
            int: Nuevo estado
        """
        if s and r:
            # Estado inválido
            self._record_state(s, r, self.state, "invalid")
            return self.state
            
        if s:
            self.state = 1
        elif r:
            self.state = 0
            
        self._record_state(s, r, self.state, "valid")
        return self.state
        
    def _record_state(self, s: int, r: int, q: int, status: str) -> None:
        """Registra cambio de estado."""
        self._history.append({
            'timestamp': time.time(),
            'set': s,
            'reset': r,
            'output': q,
            'status': status
        })
        
    def get_history(self) -> List[Dict]:
        """Obtiene historial de cambios."""
        return self._history.copy()

class DLatch:
    """Latch D."""
    
    def __init__(self):
        self.state = 0
        self._history: List[Dict] = []
        
    def update(self, d: int, enable: int) -> int:
        """
        Actualiza el estado del latch.
        
        Args:
            d: Dato
            enable: Habilitación
            
        Returns:
            int: Nuevo estado
        """
        if enable:
            self.state = d
            
        self._record_state(d, enable, self.state)
        return self.state
        
    def _record_state(self, d: int, enable: int, q: int) -> None:
        """Registra cambio de estado."""
        self._history.append({
            'timestamp': time.time(),
            'data': d,
            'enable': enable,
            'output': q
        })
        
    def get_history(self) -> List[Dict]:
        """Obtiene historial de cambios."""
        return self._history.copy()

# Funciones de análisis
def get_gate_delay(gate: Callable, 
                   inputs: List[Bit],
                   iterations: int = 100) -> float:
    """
    Mide el retardo promedio de una puerta.
    
    Args:
        gate: Función de la puerta
        inputs: Lista de bits de entrada
        iterations: Número de iteraciones
        
    Returns:
        float: Retardo promedio en segundos
    """
    delays = []
    
    for _ in range(iterations):
        start = time.time()
        gate(*inputs)
        delays.append(time.time() - start)
        
    return sum(delays) / len(delays)

def analyze_gate_function(gate: Callable, n_inputs: int) -> Dict:
    """
    Analiza una función de puerta.
    
    Args:
        gate: Función de la puerta
        n_inputs: Número de entradas
        
    Returns:
        Dict: Análisis de la puerta
    """
    # Generar todas las combinaciones de entrada
    combinations = []
    outputs = []
    
    for i in range(2**n_inputs):
        inputs = []
        for j in range(n_inputs):
            bit = Bit(f'test_{j}')
            bit.set_state((i >> j) & 1)
            inputs.append(bit)
            
        try:
            out = gate(*inputs)
            combinations.append([b.get_state() for b in inputs])
            outputs.append(out)
        except Exception as e:
            return {'error': str(e)}
            
    # Analizar función
    return {
        'truth_table': list(zip(combinations, outputs)),
        'is_constant': len(set(outputs)) == 1,
        'is_balanced': outputs.count(1) == outputs.count(0),
        'zeros': outputs.count(0),
        'ones': outputs.count(1)
    }