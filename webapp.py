from enum import Enum

# Enums for data types
class QuantumGateType(str, Enum):
    # Pauli gates
    PAULI_X = "X"      # Bit-flip
    PAULI_Y = "Y"      # Bit and phase flip
    PAULI_Z = "Z"      # Phase-flip
    
    # Fundamental gates  
    HADAMARD = "H"     # Superposition
    PHASE = "S"        # Phase rotation π/2
    T_GATE = "T"       # Phase rotation π/4
    SQRT_X = "SX"      # Square root of X
    SQRT_Y = "SY"      # Square root of Y
    
    # Rotation gates
    RX = "RX"          # X-axis rotation
    RY = "RY"          # Y-axis rotation
    RZ = "RZ"          # Z-axis rotation
    U1 = "U1"          # Phase rotation
    U2 = "U2"          # X+Z rotation
    U3 = "U3"          # General rotation
    
    # Multi-qubit gates
    CNOT = "CNOT"      # Control-NOT
    CZ = "CZ"          # Control-Z
    CY = "CY"          # Control-Y
    CH = "CH"          # Control-Hadamard
    SWAP = "SWAP"      # Swap
    ISWAP = "ISWAP"    # Swap with phase
    TOFFOLI = "TOFFOLI"  # Control-Control-NOT
    FREDKIN = "FREDKIN"  # Control-SWAP
    CUSTOM = "CUSTOM"    # Custom matrix
    
    # Advanced gates
    CPHASE = "CPHASE"    # Control-Phase
    XX = "XX"            # XX interaction
    YY = "YY"            # YY interaction
    ZZ = "ZZ"            # ZZ interaction
    PERES = "PERES"      # Peres gate
    QFT = "QFT"          # Quantum Fourier Transform
