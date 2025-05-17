import re
from typing import Dict, List, Optional, Tuple
from gates.quantum_gates import H, X, Y, Z, CNOT, CZ, SWAP

class QuantumLanguageTranslator:
    """
    Traductor entre diferentes lenguajes de programación cuántica.
    Soporta traducción entre QASM, Qiskit, Cirq, y Q#.
    """
    
    def __init__(self):
        self._supported_languages = ['qasm', 'qiskit', 'cirq', 'qsharp']
        self._gate_mappings = self._initialize_gate_mappings()
        
    def _initialize_gate_mappings(self) -> Dict:
        """
        Inicializa los mapeos de puertas entre lenguajes.
        
        Returns:
            Dict: Diccionario con los mapeos de puertas
        """
        return {
            'qasm': {
                'H': 'h', 'X': 'x', 'Y': 'y', 'Z': 'z',
                'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap'
            },
            'qiskit': {
                'H': 'h', 'X': 'x', 'Y': 'y', 'Z': 'z',
                'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap'
            },
            'cirq': {
                'H': 'H', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
                'CNOT': 'CNOT', 'CZ': 'CZ', 'SWAP': 'SWAP'
            },
            'qsharp': {
                'H': 'H', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
                'CNOT': 'CNOT', 'CZ': 'CZ', 'SWAP': 'SWAP'
            }
        }
        
    def translate_circuit(self, source_code: str, 
                        source_lang: str, 
                        target_lang: str) -> Optional[str]:
        """
        Traduce un circuito de un lenguaje a otro.
        
        Args:
            source_code: Código fuente del circuito
            source_lang: Lenguaje origen ('qasm', 'qiskit', 'cirq', 'qsharp')
            target_lang: Lenguaje destino ('qasm', 'qiskit', 'cirq', 'qsharp')
            
        Returns:
            Optional[str]: Código traducido o None si hay error
        """
        try:
            # Validar lenguajes
            if not (source_lang in self._supported_languages and 
                   target_lang in self._supported_languages):
                raise ValueError("Lenguaje no soportado")
                
            # Parsear código fuente
            operations = self._parse_source_code(source_code, source_lang)
            
            # Generar código en lenguaje destino
            return self._generate_target_code(operations, target_lang)
            
        except Exception as e:
            print(f"Error en traducción: {str(e)}")
            return None
            
    def _parse_source_code(self, source_code: str, 
                          language: str) -> List[Dict]:
        """
        Parsea el código fuente y extrae las operaciones.
        
        Args:
            source_code: Código del circuito
            language: Lenguaje del código
            
        Returns:
            List[Dict]: Lista de operaciones del circuito
        """
        operations = []
        
        if language == 'qasm':
            operations = self._parse_qasm(source_code)
        elif language == 'qiskit':
            operations = self._parse_qiskit(source_code)
        elif language == 'cirq':
            operations = self._parse_cirq(source_code)
        elif language == 'qsharp':
            operations = self._parse_qsharp(source_code)
            
        return operations
        
    def _generate_target_code(self, operations: List[Dict], 
                            language: str) -> str:
        """
        Genera código en el lenguaje destino.
        
        Args:
            operations: Lista de operaciones del circuito
            language: Lenguaje destino
            
        Returns:
            str: Código generado
        """
        if language == 'qasm':
            return self._generate_qasm(operations)
        elif language == 'qiskit':
            return self._generate_qiskit(operations)
        elif language == 'cirq':
            return self._generate_cirq(operations)
        elif language == 'qsharp':
            return self._generate_qsharp(operations)
            
    def _parse_qasm(self, source_code: str) -> List[Dict]:
        """
        Parsea código QASM.
        
        Args:
            source_code: Código QASM
            
        Returns:
            List[Dict]: Lista de operaciones
        """
        operations = []
        lines = source_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            # Extraer operación y qubits
            match = re.match(r'(\w+)\s+(q\[\d+\])\s*(,\s*q\[\d+\])?', line)
            if match:
                gate, target = match.group(1), match.group(2)
                control = match.group(3)
                
                op = {
                    'gate': gate.upper(),
                    'target': target,
                    'type': 'single'
                }
                
                if control:
                    op['control'] = control.strip(', ')
                    op['type'] = 'two'
                    
                operations.append(op)
                
        return operations
        
    def _generate_qasm(self, operations: List[Dict]) -> str:
        """
        Genera código QASM.
        
        Args:
            operations: Lista de operaciones
            
        Returns:
            str: Código QASM
        """
        code = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n\n"
        
        # Encontrar número de qubits necesarios
        qubits = set()
        for op in operations:
            target = int(re.search(r'\d+', op['target']).group())
            qubits.add(target)
            if 'control' in op:
                control = int(re.search(r'\d+', op['control']).group())
                qubits.add(control)
                
        n_qubits = max(qubits) + 1
        code += f"qreg q[{n_qubits}];\n"
        code += f"creg c[{n_qubits}];\n\n"
        
        # Generar instrucciones
        for op in operations:
            gate = self._gate_mappings['qasm'][op['gate']]
            if op['type'] == 'single':
                code += f"{gate} {op['target']};\n"
            else:
                code += f"{gate} {op['control']},{op['target']};\n"
                
        return code
        
    def _parse_qiskit(self, source_code: str) -> List[Dict]:
        """
        Parsea código Qiskit.
        
        Args:
            source_code: Código Qiskit
            
        Returns:
            List[Dict]: Lista de operaciones
        """
        operations = []
        lines = source_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Buscar operaciones Qiskit
            match = re.search(r'circuit\.(\w+)\((\[?\w+\]?,?\s*\[?\w+\]?)', line)
            if match:
                gate, qubits = match.group(1), match.group(2)
                qubits = [q.strip('[]') for q in qubits.split(',')]
                
                op = {
                    'gate': gate.upper(),
                    'target': qubits[-1],
                    'type': 'single'
                }
                
                if len(qubits) > 1:
                    op['control'] = qubits[0]
                    op['type'] = 'two'
                    
                operations.append(op)
                
        return operations
        
    def _generate_qiskit(self, operations: List[Dict]) -> str:
        """
        Genera código Qiskit.
        
        Args:
            operations: Lista de operaciones
            
        Returns:
            str: Código Qiskit
        """
        code = "from qiskit import QuantumCircuit\n\n"
        
        # Encontrar número de qubits necesarios
        qubits = set()
        for op in operations:
            target = int(re.search(r'\d+', op['target']).group())
            qubits.add(target)
            if 'control' in op:
                control = int(re.search(r'\d+', op['control']).group())
                qubits.add(control)
                
        n_qubits = max(qubits) + 1
        code += f"circuit = QuantumCircuit({n_qubits}, {n_qubits})\n\n"
        
        # Generar instrucciones
        for op in operations:
            gate = self._gate_mappings['qiskit'][op['gate']]
            if op['type'] == 'single':
                code += f"circuit.{gate}({op['target']})\n"
            else:
                code += f"circuit.{gate}({op['control']}, {op['target']})\n"
                
        return code

    def verify_equivalence(self, circuit1: str, lang1: str,
                          circuit2: str, lang2: str) -> bool:
        """
        Verifica si dos circuitos en diferentes lenguajes son equivalentes.
        
        Args:
            circuit1: Primer circuito
            lang1: Lenguaje del primer circuito
            circuit2: Segundo circuito
            lang2: Lenguaje del segundo circuito
            
        Returns:
            bool: True si los circuitos son equivalentes
        """
        try:
            # Convertir ambos circuitos a representación interna
            ops1 = self._parse_source_code(circuit1, lang1)
            ops2 = self._parse_source_code(circuit2, lang2)
            
            # Comparar operaciones
            if len(ops1) != len(ops2):
                return False
                
            for op1, op2 in zip(ops1, ops2):
                if op1['gate'] != op2['gate'] or op1['type'] != op2['type']:
                    return False
                    
                if op1['type'] == 'two':
                    if (op1['control'] != op2['control'] or 
                        op1['target'] != op2['target']):
                        return False
                else:
                    if op1['target'] != op2['target']:
                        return False
                        
            return True
            
        except Exception:
            return False

    def get_supported_languages(self) -> List[str]:
        """
        Obtiene la lista de lenguajes soportados.
        
        Returns:
            List[str]: Lista de lenguajes soportados
        """
        return self._supported_languages.copy()

    def get_supported_gates(self, language: str) -> Optional[Dict[str, str]]:
        """
        Obtiene las puertas soportadas para un lenguaje.
        
        Args:
            language: Lenguaje a consultar
            
        Returns:
            Optional[Dict[str, str]]: Mapeo de puertas o None si el lenguaje no existe
        """
        return self._gate_mappings.get(language)
