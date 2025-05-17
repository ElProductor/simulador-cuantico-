import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Importar después de configurar el path
from gui.quantum_gui import main as gui_main

if __name__ == "__main__":
    gui_main()
