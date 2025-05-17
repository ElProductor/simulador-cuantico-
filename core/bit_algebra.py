from typing import List, Dict, Optional, Union
import numpy as np

class BitAlgebra:
    """
    Clase para realizar operaciones avanzadas con bits clásicos.
    Provee funcionalidades de álgebra booleana y análisis.
    """
    
    @staticmethod
    def add_bits(bit1: int, bit2: int, carry_in: int = 0) -> dict:
        """
        Suma dos bits con acarreo.
        
        Args:
            bit1: Primer bit (0 o 1)
            bit2: Segundo bit (0 o 1)
            carry_in: Acarreo de entrada (0 o 1)
            
        Returns:
            dict: Diccionario con 'sum' y 'carry_out'
        """
        if not all(b in [0,1] for b in [bit1, bit2, carry_in]):
            raise ValueError("Los bits deben ser 0 o 1")
            
        total = bit1 + bit2 + carry_in
        return {
            'sum': total % 2,  
            'carry_out': total // 2
        }
        
    @staticmethod
    def ripple_carry_adder(bits1: List[int], bits2: List[int]) -> Dict[str, List[int]]:
        """
        Implementa un sumador con acarreo en cascada.
        
        Args:
            bits1: Primera lista de bits
            bits2: Segunda lista de bits
            
        Returns:
            Dict[str, List[int]]: Resultado con suma y acarreos
        """
        if len(bits1) != len(bits2):
            raise ValueError("Las listas deben tener igual longitud")
            
        n = len(bits1)
        sum_bits = []
        carry = 0
        carries = []
        
        for i in range(n):
            result = BitAlgebra.add_bits(bits1[i], bits2[i], carry)
            sum_bits.append(result['sum'])
            carry = result['carry_out']
            carries.append(carry)
            
        return {
            'sum': sum_bits,
            'carries': carries,
            'overflow': carry
        }
        
    @staticmethod
    def multiply_bits(bits1: List[int], bits2: List[int]) -> List[int]:
        """
        Multiplica dos números binarios.
        
        Args:
            bits1: Primera lista de bits
            bits2: Segunda lista de bits
            
        Returns:
            List[int]: Resultado de la multiplicación
        """
        if not all(b in [0,1] for b in bits1 + bits2):
            raise ValueError("Los bits deben ser 0 o 1")
            
        n1, n2 = len(bits1), len(bits2)
        result = [0] * (n1 + n2)
        
        for i in range(n1):
            for j in range(n2):
                if bits1[i] and bits2[j]:
                    pos = i + j
                    carry = 1
                    while carry and pos < len(result):
                        total = result[pos] + carry
                        result[pos] = total % 2
                        carry = total // 2
                        pos += 1
                        
        return result
        
    @staticmethod
    def karnaugh_map(func: List[int], vars_count: int) -> np.ndarray:
        """
        Genera un mapa de Karnaugh para una función booleana.
        
        Args:
            func: Lista con valores de la función
            vars_count: Número de variables
            
        Returns:
            np.ndarray: Mapa de Karnaugh
        """
        if len(func) != 2**vars_count:
            raise ValueError("Longitud de función incorrecta")
            
        if vars_count < 2 or vars_count > 4:
            raise ValueError("Soporta 2-4 variables")
            
        # Códigos Gray para filas y columnas
        def gray_code(n: int) -> List[int]:
            return [i ^ (i >> 1) for i in range(n)]
            
        if vars_count == 2:
            shape = (2, 2)
        elif vars_count == 3:
            shape = (2, 4)
        else:  # vars_count == 4
            shape = (4, 4)
            
        kmap = np.zeros(shape, dtype=int)
        gray_rows = gray_code(shape[0])
        gray_cols = gray_code(shape[1])
        
        for i in range(shape[0]):
            for j in range(shape[1]):
                idx = (gray_rows[i] << (vars_count//2)) | gray_cols[j]
                kmap[i,j] = func[idx]
                
        return kmap
        
    @staticmethod
    def minimize_function(kmap: np.ndarray) -> List[str]:
        """
        Minimiza una función booleana usando el mapa de Karnaugh.
        
        Args:
            kmap: Mapa de Karnaugh
            
        Returns:
            List[str]: Lista de términos minimizados
        """
        rows, cols = kmap.shape
        terms = []
        
        # Buscar grupos de 1s
        def find_groups(arr: np.ndarray) -> List[tuple]:
            groups = []
            # Potencias de 2 válidas para grupos
            sizes = [4, 2, 1]
            
            # Marcar celdas usadas
            used = np.zeros_like(arr, dtype=bool)
            
            for size in sizes:
                # Buscar grupos horizontales
                for i in range(rows):
                    for j in range(cols):
                        if (not used[i,j] and arr[i,j] == 1 and
                            j + size <= cols and
                            all(arr[i,k] == 1 for k in range(j,j+size))):
                            groups.append(((i,j), size, 'h'))
                            used[i,j:j+size] = True
                            
                # Buscar grupos verticales
                for j in range(cols):
                    for i in range(rows):
                        if (not used[i,j] and arr[i,j] == 1 and
                            i + size <= rows and
                            all(arr[k,j] == 1 for k in range(i,i+size))):
                            groups.append(((i,j), size, 'v'))
                            used[i:i+size,j] = True
                            
            return groups
            
        # Convertir grupos a términos
        def group_to_term(group: tuple) -> str:
            (i,j), size, direction = group
            term = []
            
            # Variables según posición
            if rows == 2:  # 2 variables
                if direction == 'h':
                    if size == 2:
                        term.append('A' if i == 0 else 'A\'')
                    else:
                        term.extend(['A' if i == 0 else 'A\'',
                                   'B' if j == 0 else 'B\''])
                else:  # vertical
                    if size == 2:
                        term.append('B' if j == 0 else 'B\'')
                    else:
                        term.extend(['A' if i == 0 else 'A\'',
                                   'B' if j == 0 else 'B\''])
                                   
            else:  # 4 variables
                var_map = {
                    (0,0): ['A','B','C','D'],
                    (0,1): ['A','B','C\'','D'],
                    (1,0): ['A\'','B','C','D'],
                    (1,1): ['A\'','B','C\'','D']
                }
                base_vars = var_map[(i,j)]
                
                if direction == 'h':
                    if size == 4:
                        term.extend(base_vars[:2])
                    elif size == 2:
                        term.extend(base_vars[:3])
                    else:
                        term.extend(base_vars)
                else:
                    if size == 4:
                        term.extend([base_vars[0], base_vars[2]])
                    elif size == 2:
                        term.extend([base_vars[0], base_vars[2], base_vars[3]])
                    else:
                        term.extend(base_vars)
                        
            return ''.join(term)
            
        # Encontrar grupos y convertir a términos
        groups = find_groups(kmap)
        terms = [group_to_term(g) for g in groups]
        
        return terms if terms else ['0']  # Retornar 0 si no hay términos
        
    @staticmethod
    def analyze_function(func: List[int]) -> Dict[str, Union[bool, List[int]]]:
        """
        Analiza propiedades de una función booleana.
        
        Args:
            func: Lista con valores de la función
            
        Returns:
            Dict: Diccionario con propiedades
        """
        n = len(func)
        if not all(b in [0,1] for b in func):
            raise ValueError("Los valores deben ser 0 o 1")
            
        # Convertir a array numpy para operaciones
        arr = np.array(func)
        
        # Propiedades
        props = {
            'is_constant': len(set(func)) == 1,
            'is_balanced': np.sum(arr) == n//2,
            'ones_count': int(np.sum(arr)),
            'zeros_count': int(n - np.sum(arr)),
            'truth_table': list(enumerate(func))
        }
        
        return props

    @staticmethod
    def hamming_distance(bits1: List[int], bits2: List[int]) -> int:
        """
        Calcula la distancia de Hamming entre dos secuencias.
        
        Args:
            bits1: Primera secuencia
            bits2: Segunda secuencia
            
        Returns:
            int: Distancia de Hamming
        """
        if len(bits1) != len(bits2):
            raise ValueError("Las secuencias deben tener igual longitud")
            
        return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
        
    @staticmethod
    def gray_code(n: int) -> List[List[int]]:
        """
        Genera el código Gray de n bits.
        
        Args:
            n: Número de bits
            
        Returns:
            List[List[int]]: Secuencias del código Gray
        """
        if n < 1:
            raise ValueError("n debe ser positivo")
            
        def binary_to_gray(num: int) -> List[int]:
            return [int(b) for b in format(num ^ (num >> 1), f'0{n}b')]
            
        return [binary_to_gray(i) for i in range(2**n)]
        
    @staticmethod
    def error_correction_code(data: List[int]) -> Dict[str, List[int]]:
        """
        Implementa código de corrección de errores Hamming.
        
        Args:
            data: Bits de datos
            
        Returns:
            Dict: Datos codificados y bits de paridad
        """
        def calculate_parity_positions(length: int) -> List[int]:
            return [2**i for i in range(length.bit_length())]
            
        def calculate_parity_bit(encoded: List[int], pos: int) -> int:
            indices = [i for i in range(len(encoded)) 
                      if i & pos == pos and i < len(encoded)]
            return sum(encoded[i] for i in indices if i < len(encoded)) % 2
            
        # Calcular número de bits de paridad necesarios
        m = len(data)
        r = (m + 1).bit_length()
        n = m + r
        
        # Posiciones de los bits de paridad
        parity_positions = calculate_parity_positions(n)
        
        # Crear mensaje codificado
        encoded = [0] * n
        data_idx = 0
        
        for i in range(1, n+1):
            if i not in parity_positions:
                encoded[i-1] = data[data_idx]
                data_idx += 1
                
        # Calcular bits de paridad
        for pos in parity_positions:
            idx = pos - 1
            if idx < len(encoded):
                encoded[idx] = calculate_parity_bit(encoded, pos)
                
        return {
            'encoded': encoded,
            'parity_bits': [encoded[p-1] for p in parity_positions],
            'parity_positions': parity_positions
        }
        
    @staticmethod
    def detect_errors(encoded: List[int]) -> Dict[str, Union[bool, int]]:
        """
        Detecta errores en datos codificados con Hamming.
        
        Args:
            encoded: Datos codificados
            
        Returns:
            Dict: Información sobre errores detectados
        """
        n = len(encoded)
        r = (n + 1).bit_length() - 1
        
        # Calcular síndrome
        syndrome = 0
        for i in range(r):
            pos = 2**i
            indices = [j for j in range(1, n+1) if j & pos == pos]
            if sum(encoded[j-1] for j in indices) % 2 == 1:
                syndrome |= pos
                
        return {
            'error_detected': syndrome != 0,
            'error_position': syndrome if syndrome != 0 else None,
            'syndrome': syndrome
        }
        
    @staticmethod
    def verify_circuit(func: List[int], circuit: List[Dict]) -> bool:
        """
        Verifica si un circuito implementa una función booleana.
        
        Args:
            func: Función objetivo
            circuit: Lista de puertas del circuito
            
        Returns:
            bool: True si el circuito implementa la función
        """
        n = len(func)
        vars_count = (n-1).bit_length()
        
        def evaluate_circuit(inputs: List[int]) -> int:
            """Evalúa el circuito con las entradas dadas."""
            state = inputs.copy()
            
            for gate in circuit:
                op = gate['gate']
                targets = gate['targets']
                
                if op == 'NOT':
                    state[targets[0]] = 1 - state[targets[0]]
                elif op == 'AND':
                    state[targets[1]] = state[targets[0]] & state[targets[1]]
                elif op == 'OR':
                    state[targets[1]] = state[targets[0]] | state[targets[1]]
                elif op == 'XOR':
                    state[targets[1]] = state[targets[0]] ^ state[targets[1]]
                    
            return state[-1]  # último bit es la salida
            
        # Probar todas las combinaciones posibles
        for i in range(n):
            inputs = [int(b) for b in format(i, f'0{vars_count}b')]
            if evaluate_circuit(inputs) != func[i]:
                return False
                
        return True