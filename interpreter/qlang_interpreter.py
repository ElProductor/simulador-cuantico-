from core.qubit import Qubit
from core.bit import Bit
from gates.quantum_gates import H, X, Z, Y, RHW, CNOT, SWAP, CZ, apply_two_qubit_gate, get_circuit_qasm
from gates.classical_gates import and_gate, or_gate, not_gate, xor_gate, nand_gate, nor_gate
from visualizer.circuit_visualizer import QuantumVisualizer

qubits = {}
bits = {}
visualizer = QuantumVisualizer()
circuit_operations = []

def handle_qubit_command(tokens):
    if len(tokens) != 2:
        raise ValueError("Uso: QUBIT <nombre>")
    name = tokens[1]
    if name in qubits:
        print(f"El qubit {name} ya existe")
    else:
        qubits[name] = Qubit(name)
        print(f"Qubit {name} creado")

def handle_bit_command(tokens):
    if len(tokens) != 2:
        raise ValueError("Uso: BIT <nombre>")
    name = tokens[1]
    if name in bits:
        print(f"El bit {name} ya existe")
    else:
        bits[name] = Bit(name)
        print(f"Bit {name} creado")

def handle_set_command(tokens):
    if len(tokens) != 3:
        raise ValueError("Uso: SET <bit> <0|1>")
    name = tokens[1]
    try:
        value = int(tokens[2])
    except ValueError:
        raise ValueError("El valor debe ser 0 o 1")
    
    if name not in bits:
        raise ValueError(f"El bit {name} no existe")
    if value not in [0, 1]:
        raise ValueError("El valor debe ser 0 o 1")
    
    bits[name].set_state(value)
    print(f"Bit {name} establecido a {value}")

def handle_quantum_gate(gate, tokens):
    if gate in ["H", "X", "Z", "Y", "RHW"]:
        # Puertas de un qubit
        if len(tokens) != 3:
            raise ValueError(f"Uso: GATE {gate} <qubit>")
        target = tokens[2]
        if target not in qubits:
            raise ValueError(f"El qubit {target} no existe")
        gate_matrix = {"H": H, "X": X, "Z": Z, "Y": Y, "RHW": RHW}[gate]
        qubits[target].apply_gate(gate_matrix)
        visualizer.add_operation(gate, int(target[1]))
        circuit_operations.append({"type": "single", "gate": gate, "target": int(target[1])})
        print(f"Puerta {gate} aplicada a {target}")
    
    elif gate in ["CNOT", "CZ", "SWAP"]:
        # Puertas de dos qubits
        if len(tokens) != 4:
            raise ValueError(f"Uso: GATE {gate} <control> <target>")
        control, target = tokens[2], tokens[3]
        if control not in qubits or target not in qubits:
            raise ValueError("Uno o ambos qubits no existen")
        
        gate_matrix = {"CNOT": CNOT, "CZ": CZ, "SWAP": SWAP}[gate]
        qubits[control].entangled_with.add(target)
        qubits[target].entangled_with.add(control)
        state1, state2 = apply_two_qubit_gate(gate_matrix, qubits[control].state, qubits[target].state)
        qubits[control].state = state1
        qubits[target].state = state2
        
        visualizer.add_operation(gate, int(target[1]), int(control[1]))
        circuit_operations.append({
            "type": "two",
            "gate": gate,
            "control": int(control[1]),
            "target": int(target[1])
        })
        print(f"Puerta {gate} aplicada entre {control} y {target}")

def handle_classical_gate(gate, tokens):
    if len(tokens) != 4 and gate != "NOT":
        raise ValueError(f"Uso: GATE {gate} <bit1> <bit2>")
    
    target = tokens[2]
    if target not in bits:
        raise ValueError(f"El bit {target} no existe")

    if gate == "NOT":
        result = not_gate(bits[target])
        print(f"Resultado de NOT({target}) = {1 if result else 0}")
        return

    target2 = tokens[3]
    if target2 not in bits:
        raise ValueError(f"El bit {target2} no existe")
    
    gate_func = {
        "AND": and_gate,
        "OR": or_gate,
        "XOR": xor_gate,
        "NAND": nand_gate,
        "NOR": nor_gate
    }[gate]
    
    result = gate_func(bits[target], bits[target2])
    print(f"Resultado de {gate}({target}, {target2}) = {1 if result else 0}")

def handle_gate_command(tokens):
    if len(tokens) < 3:
        raise ValueError("Uso: GATE <tipo> <target> [target2]")
    
    gate = tokens[1]
    if gate in ["H", "X", "Z", "Y", "RHW", "CNOT", "CZ", "SWAP"]:
        handle_quantum_gate(gate, tokens)
    elif gate in ["AND", "OR", "XOR", "NAND", "NOR", "NOT"]:
        handle_classical_gate(gate, tokens)
    else:
        raise ValueError(f"Puerta {gate} no válida")

def handle_measure_command(tokens):
    if len(tokens) != 2:
        raise ValueError("Uso: MEASURE <qubit|bit>")
    target = tokens[1]
    
    if target in qubits:
        result = qubits[target].measure()
        print(f"Qubit {target} -> {result}")
    elif target in bits:
        result = bits[target].get_state()
        print(f"Bit {target} -> {result}")
    else:
        raise ValueError(f"No existe {target}")

def handle_show_command(tokens):
    if len(tokens) < 2:
        raise ValueError("Uso: SHOW <bloch|circuit|qasm> [qubit]")
    
    what = tokens[1].lower()
    if what == "bloch":
        if len(tokens) != 3 or tokens[2] not in qubits:
            raise ValueError("Uso: SHOW bloch <qubit>")
        visualizer.draw_bloch_sphere(qubits[tokens[2]])
    elif what == "circuit":
        visualizer.draw_circuit()
    elif what == "qasm":
        print(get_circuit_qasm(circuit_operations))
    else:
        raise ValueError("Opciones válidas: bloch, circuit, qasm")

def interpret(command):
    tokens = command.split()
    if len(tokens) < 1:
        raise ValueError("Comando incompleto")

    handlers = {
        "QUBIT": handle_qubit_command,
        "BIT": handle_bit_command,
        "SET": handle_set_command,
        "GATE": handle_gate_command,
        "MEASURE": handle_measure_command,
        "SHOW": handle_show_command
    }

    handler = handlers.get(tokens[0])
    if handler:
        handler(tokens)
    else:
        raise ValueError(f"Comando {tokens[0]} no reconocido")
