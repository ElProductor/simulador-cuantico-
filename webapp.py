from flask import Flask, render_template, request, jsonify
import quantum_simulator
from typing import Dict, Union

app = Flask(__name__)

# Valid quantum gates for input validation
VALID_GATES = {'H', 'X', 'Y', 'Z', 'CX', 'SWAP', 'RX', 'RY', 'RZ'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        # Get and validate input
        circuit = request.form.get('circuit', '').strip()
        shots = request.form.get('shots', '100')
        
        if not circuit:
            return jsonify({'error': 'Circuit cannot be empty'}), 400
            
        # Basic syntax validation
        for gate in circuit.split():
            if gate not in VALID_GATES:
                return jsonify({'error': f'Invalid gate: {gate}'}), 400
        
        # Convert shots to int with validation
        try:
            shots = int(shots)
            if shots <= 0 or shots > 10000:
                return jsonify({'error': 'Shots must be between 1 and 10000'}), 400
        except ValueError:
            return jsonify({'error': 'Shots must be an integer'}), 400
        
        # Run simulation
        result = quantum_simulator.run(circuit, shots)
        
        # Enhanced results structure
        enhanced_result = {
            'probabilities': result.get('probabilities', {}),
            'state_vector': result.get('state_vector', []),
            'circuit_diagram': generate_circuit_diagram(circuit),
            'shots': shots
        }
        
        return render_template('results.html', result=enhanced_result)
        
    except Exception as e:
        app.logger.error(f"Simulation error: {str(e)}")
        return jsonify({'error': 'An error occurred during simulation'}), 500

def generate_circuit_diagram(circuit: str) -> str:
    """Generate a simple ASCII circuit diagram from the circuit string"""
    # This is a placeholder - you might want to use a proper visualization library
    return f"Circuit: {circuit}"

if __name__ == '__main__':
    app.run(debug=True)