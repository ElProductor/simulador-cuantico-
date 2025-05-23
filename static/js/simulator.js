/**
 * simulator.js - Lógica principal del simulador cuántico
 * Este archivo maneja la creación y manipulación de circuitos cuánticos,
 * así como la comunicación con el backend para ejecutar simulaciones
 */

// Configuración inicial y variables globales
let circuit = [];
let numQubits = 3;
let numShots = 1024;
let simulationType = 'quantum';
let noiseModel = 'ideal';
let optimizationAlgorithm = 'nelder_mead';
let realTimeSimulation = false;
let parallelExecution = true;
let hardwareProfile = 'ideal';
let simulationResults = null;
let websocket = null;

// Elementos DOM principales
const circuitBuilder = document.getElementById('circuitBuilder');
const numQubitsInput = document.getElementById('numQubits');
const numQubitsValue = document.getElementById('numQubitsValue');
const numShotsInput = document.getElementById('numShots');
const numShotsValue = document.getElementById('numShotsValue');
const simulationTypeSelect = document.getElementById('simulationType');
const noiseModelSelect = document.getElementById('noiseModel');
const optimizationAlgorithmSelect = document.getElementById('optimizationAlgorithm');
const realTimeCheckbox = document.getElementById('realTime');
const parallelExecutionCheckbox = document.getElementById('parallelExecution');
const hardwareProfileSelect = document.getElementById('hardwareProfile');
const runSimulationBtn = document.getElementById('runSimulation');
const clearCircuitBtn = document.getElementById('clearCircuit');
const saveCircuitBtn = document.getElementById('saveCircuit');
const addQubitBtn = document.getElementById('addQubit');
const removeQubitBtn = document.getElementById('removeQubit');
const quantumGates = document.querySelectorAll('.quantum-gate');

// Inicialización cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    initializeSimulator();
    setupEventListeners();
    createCircuitUI();
    setupWebSocket();
});

/**
 * Inicializa el simulador
 */
function initializeSimulator() {
    // Inicializar valores de configuración
    numQubitsValue.textContent = numQubits;
    numShotsValue.textContent = numShots;
    simulationTypeSelect.value = simulationType;
    noiseModelSelect.value = noiseModel;
    optimizationAlgorithmSelect.value = optimizationAlgorithm;
    realTimeCheckbox.checked = realTimeSimulation;
    parallelExecutionCheckbox.checked = parallelExecution;
    hardwareProfileSelect.value = hardwareProfile;
    
    // Crear circuito inicial vacío
    resetCircuit();
}

/**
 * Configura los event listeners para los elementos del simulador
 */
function setupEventListeners() {
    // Event listeners para controles de configuración
    numQubitsInput.addEventListener('input', updateNumQubits);
    numShotsInput.addEventListener('input', updateNumShots);
    simulationTypeSelect.addEventListener('change', (e) => simulationType = e.target.value);
    noiseModelSelect.addEventListener('change', (e) => noiseModel = e.target.value);
    optimizationAlgorithmSelect.addEventListener('change', (e) => optimizationAlgorithm = e.target.value);
    realTimeCheckbox.addEventListener('change', (e) => realTimeSimulation = e.target.checked);
    parallelExecutionCheckbox.addEventListener('change', (e) => parallelExecution = e.target.checked);
    hardwareProfileSelect.addEventListener('change', (e) => hardwareProfile = e.target.value);
    
    // Event listeners para botones de control
    runSimulationBtn.addEventListener('click', runSimulation);
    clearCircuitBtn.addEventListener('click', clearCircuit);
    saveCircuitBtn.addEventListener('click', saveCircuit);
    addQubitBtn.addEventListener('click', addQubit);
    removeQubitBtn.addEventListener('click', removeQubit);
    
    // Event listeners para puertas cuánticas
    quantumGates.forEach(gate => {
        gate.addEventListener('click', () => selectGate(gate.dataset.gate));
    });
    
    // Event listeners para vistas de resultados
    const viewButtons = document.querySelectorAll('.view-button');
    viewButtons.forEach(button => {
        button.addEventListener('click', () => switchResultView(button.dataset.view));
    });
}

/**
 * Actualiza el número de qubits
 */
function updateNumQubits() {
    const newNumQubits = parseInt(numQubitsInput.value);
    numQubitsValue.textContent = newNumQubits;
    
    // Solo actualizar si el número ha cambiado
    if (newNumQubits !== numQubits) {
        numQubits = newNumQubits;
        createCircuitUI();
    }
}

/**
 * Actualiza el número de disparos (shots)
 */
function updateNumShots() {
    numShots = parseInt(numShotsInput.value);
    numShotsValue.textContent = numShots;
}

/**
 * Crea la interfaz del circuito cuántico
 */
function createCircuitUI() {
    // Limpiar el constructor de circuitos
    circuitBuilder.innerHTML = '';
    
    // Crear líneas de qubits
    for (let i = 0; i < numQubits; i++) {
        const qubitLine = document.createElement('div');
        qubitLine.className = 'qubit-line';
        
        const qubitLabel = document.createElement('div');
        qubitLabel.className = 'qubit-label';
        qubitLabel.textContent = `q${i}`;
        
        const gateContainer = document.createElement('div');
        gateContainer.className = 'gate-container';
        gateContainer.dataset.qubit = i;
        gateContainer.addEventListener('click', (e) => {
            if (e.target === gateContainer) {
                placeGate(i);
            }
        });
        
        qubitLine.appendChild(qubitLabel);
        qubitLine.appendChild(gateContainer);
        circuitBuilder.appendChild(qubitLine);
    }
    
    // Renderizar puertas existentes
    renderCircuit();
}

/**
 * Renderiza el circuito actual en la interfaz
 */
function renderCircuit() {
    // Limpiar todas las puertas existentes
    const gateContainers = document.querySelectorAll('.gate-container');
    gateContainers.forEach(container => {
        container.innerHTML = '';
    });
    
    // Renderizar cada puerta en el circuito
    circuit.forEach(gate => {
        const gateElement = createGateElement(gate);
        const container = document.querySelector(`.gate-container[data-qubit="${gate.target}"]`);
        if (container) {
            container.appendChild(gateElement);
        }
    });
}

/**
 * Crea un elemento DOM para una puerta cuántica
 * @param {Object} gate - La puerta cuántica a representar
 * @returns {HTMLElement} - El elemento DOM de la puerta
 */
function createGateElement(gate) {
    const gateElement = document.createElement('div');
    gateElement.className = 'quantum-gate';
    gateElement.textContent = gate.type;
    gateElement.dataset.gate = gate.type;
    gateElement.dataset.target = gate.target;
    
    if (gate.control !== undefined) {
        gateElement.dataset.control = gate.control;
        gateElement.classList.add('controlled-gate');
    }
    
    if (gate.parameters) {
        gateElement.dataset.parameters = JSON.stringify(gate.parameters);
        gateElement.classList.add('parameterized-gate');
    }
    
    // Añadir event listener para eliminar la puerta
    gateElement.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        removeGate(gate);
    });
    
    return gateElement;
}

/**
 * Selecciona una puerta cuántica para colocar en el circuito
 * @param {string} gateType - El tipo de puerta seleccionada
 */
let selectedGate = null;

function selectGate(gateType) {
    selectedGate = gateType;
    console.log(`Puerta seleccionada: ${gateType}`);
    
    // Resaltar la puerta seleccionada
    quantumGates.forEach(gate => {
        gate.classList.remove('selected');
        if (gate.dataset.gate === gateType) {
            gate.classList.add('selected');
        }
    });
}

/**
 * Coloca una puerta en el circuito
 * @param {number} qubit - El qubit objetivo
 */
function placeGate(qubit) {
    if (!selectedGate) return;
    
    // Crear objeto de puerta
    const gate = {
        type: selectedGate,
        target: qubit
    };
    
    // Para puertas de múltiples qubits, solicitar qubit de control
    if (['CNOT', 'CZ', 'CY', 'CH', 'SWAP', 'TOFFOLI', 'FREDKIN'].includes(selectedGate)) {
        // Implementar lógica para seleccionar qubit de control
        // Por ahora, usar un qubit de control predeterminado diferente al objetivo
        gate.control = (qubit + 1) % numQubits;
    }
    
    // Para puertas parametrizadas, solicitar parámetros
    if (['RX', 'RY', 'RZ', 'U1', 'U2', 'U3', 'CPHASE'].includes(selectedGate)) {
        // Implementar lógica para ingresar parámetros
        // Por ahora, usar un valor predeterminado
        gate.parameters = [Math.PI/4];
    }
    
    // Añadir puerta al circuito
    circuit.push(gate);
    
    // Actualizar la interfaz
    renderCircuit();
    
    // Si la simulación en tiempo real está habilitada, ejecutar simulación
    if (realTimeSimulation) {
        runSimulation();
    }
}

/**
 * Elimina una puerta del circuito
 * @param {Object} gateToRemove - La puerta a eliminar
 */
function removeGate(gateToRemove) {
    // Encontrar y eliminar la puerta del circuito
    const index = circuit.findIndex(gate => 
        gate.type === gateToRemove.type && 
        gate.target === gateToRemove.target && 
        gate.control === gateToRemove.control
    );
    
    if (index !== -1) {
        circuit.splice(index, 1);
        renderCircuit();
        
        // Si la simulación en tiempo real está habilitada, ejecutar simulación
        if (realTimeSimulation) {
            runSimulation();
        }
    }
}

/**
 * Añade un qubit al circuito
 */
function addQubit() {
    if (numQubits < 20) {
        numQubits++;
        numQubitsInput.value = numQubits;
        numQubitsValue.textContent = numQubits;
        createCircuitUI();
    }
}

/**
 * Elimina un qubit del circuito
 */
function removeQubit() {
    if (numQubits > 1) {
        // Eliminar puertas asociadas con el último qubit
        circuit = circuit.filter(gate => 
            gate.target < numQubits - 1 && 
            (gate.control === undefined || gate.control < numQubits - 1)
        );
        
        numQubits--;
        numQubitsInput.value = numQubits;
        numQubitsValue.textContent = numQubits;
        createCircuitUI();
    }
}

/**
 * Limpia el circuito actual
 */
function clearCircuit() {
    resetCircuit();
    renderCircuit();
}

/**
 * Reinicia el circuito a un estado vacío
 */
function resetCircuit() {
    circuit = [];
}

/**
 * Guarda el circuito actual
 */
function saveCircuit() {
    const circuitData = {
        numQubits,
        gates: circuit,
        simulationType,
        noiseModel,
        optimizationAlgorithm,
        numShots,
        hardwareProfile
    };
    
    // Guardar en localStorage
    localStorage.setItem('savedCircuit', JSON.stringify(circuitData));
    
    // También podría implementarse una llamada a la API para guardar en el servidor
    console.log('Circuito guardado:', circuitData);
    
    // Mostrar notificación
    showNotification('Circuito guardado correctamente');
}

/**
 * Carga un circuito guardado
 * @param {Object} circuitData - Los datos del circuito a cargar
 */
function loadCircuit(circuitData) {
    // Actualizar configuración
    numQubits = circuitData.numQubits;
    circuit = circuitData.gates;
    simulationType = circuitData.simulationType || 'quantum';
    noiseModel = circuitData.noiseModel || 'ideal';
    optimizationAlgorithm = circuitData.optimizationAlgorithm || 'nelder_mead';
    numShots = circuitData.numShots || 1024;
    hardwareProfile = circuitData.hardwareProfile || 'ideal';
    
    // Actualizar controles de la interfaz
    numQubitsInput.value = numQubits;
    numQubitsValue.textContent = numQubits;
    numShotsInput.value = numShots;
    numShotsValue.textContent = numShots;
    simulationTypeSelect.value = simulationType;
    noiseModelSelect.value = noiseModel;
    optimizationAlgorithmSelect.value = optimizationAlgorithm;
    hardwareProfileSelect.value = hardwareProfile;
    
    // Actualizar interfaz
    createCircuitUI();
    
    // Mostrar notificación
    showNotification('Circuito cargado correctamente');
}

/**
 * Ejecuta la simulación del circuito actual
 */
function runSimulation() {
    // Mostrar indicador de carga
    showLoadingIndicator(true);
    
    // Preparar datos para la simulación
    const simulationData = {
        circuit: {
            num_qubits: numQubits,
            gates: circuit.map(gate => ({
                gate_type: gate.type,
                target_qubits: [gate.target],
                control_qubits: gate.control !== undefined ? [gate.control] : [],
                parameters: gate.parameters || []
            }))
        },
        simulation_type: simulationType,
        noise_model: noiseModel,
        optimization_algorithm: optimizationAlgorithm,
        shots: numShots,
        hardware_profile: hardwareProfile,
        parallel_execution: parallelExecution
    };
    
    // Si hay una conexión WebSocket activa, usar WebSocket
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            action: 'run_simulation',
            data: simulationData
        }));
    } else {
        // De lo contrario, usar API REST
        fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(simulationData)
        })
        .then(response => response.json())
        .then(data => {
            processSimulationResults(data);
        })
        .catch(error => {
            console.error('Error al ejecutar la simulación:', error);
            showNotification('Error al ejecutar la simulación', 'error');
            showLoadingIndicator(false);
        });
    }
}

/**
 * Procesa los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function processSimulationResults(results) {
    simulationResults = results;
    showLoadingIndicator(false);
    
    // Actualizar métricas
    updateMetrics(results);
    
    // Actualizar visualizaciones
    updateVisualizations(results);
    
    console.log('Resultados de la simulación:', results);
}

/**
 * Actualiza las métricas mostradas en la interfaz
 * @param {Object} results - Los resultados de la simulación
 */
function updateMetrics(results) {
    // Actualizar valores de métricas
    document.getElementById('entanglementValue').textContent = 
        results.entanglement_entropy ? results.entanglement_entropy.toFixed(2) : '0.00';
    
    document.getElementById('fidelityValue').textContent = 
        results.fidelity ? results.fidelity.toFixed(2) : '1.00';
    
    document.getElementById('executionTime').textContent = 
        results.execution_time ? `${results.execution_time.toFixed(2)} ms` : '0 ms';
    
    document.getElementById('circuitDepth').textContent = 
        results.circuit_depth || '0';
}

/**
 * Configura la conexión WebSocket para simulación en tiempo real
 */
function setupWebSocket() {
    // Crear conexión WebSocket solo si está soportado por el navegador
    if ('WebSocket' in window) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/simulator`;
        
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function() {
            console.log('Conexión WebSocket establecida');
        };
        
        websocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.action === 'simulation_results') {
                processSimulationResults(data.results);
            } else if (data.action === 'notification') {
                showNotification(data.message, data.type);
            }
        };
        
        websocket.onclose = function() {
            console.log('Conexión WebSocket cerrada');
            // Intentar reconectar después de un tiempo
            setTimeout(setupWebSocket, 5000);
        };
        
        websocket.onerror = function(error) {
            console.error('Error en la conexión WebSocket:', error);
        };
    } else {
        console.warn('WebSocket no está soportado por este navegador');
    }
}

/**
 * Cambia la vista de resultados
 * @param {string} viewName - El nombre de la vista a mostrar
 */
function switchResultView(viewName) {
    // Desactivar todos los botones y vistas
    const viewButtons = document.querySelectorAll('.view-button');
    viewButtons.forEach(button => button.classList.remove('active'));
    
    const resultViews = document.querySelectorAll('.result-view');
    resultViews.forEach(view => view.classList.remove('active'));
    
    // Activar el botón y vista seleccionados
    document.querySelector(`.view-button[data-view="${viewName}"]`).classList.add('active');
    document.getElementById(`${viewName}View`).classList.add('active');
    
    // Actualizar visualización si hay resultados
    if (simulationResults) {
        updateVisualizations(simulationResults);
    }
}

/**
 * Muestra u oculta el indicador de carga
 * @param {boolean} show - Si se debe mostrar el indicador
 */
function showLoadingIndicator(show) {
    // Implementar lógica para mostrar/ocultar indicador de carga
    runSimulationBtn.disabled = show;
    runSimulationBtn.innerHTML = show ? 
        '<i class="fas fa-spinner fa-spin"></i> Ejecutando...' : 
        'Ejecutar Simulación';
}

/**
 * Muestra una notificación
 * @param {string} message - El mensaje a mostrar
 * @param {string} type - El tipo de notificación (success, error, warning, info)
 */
function showNotification(message, type = 'success') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${getIconForNotificationType(type)}"></i>
        </div>
        <div class="notification-content">
            <p>${message}</p>
        </div>
        <div class="notification-close">
            <i class="fas fa-times"></i>
        </div>
    `;
    
    // Añadir al DOM
    document.body.appendChild(notification);
    
    // Añadir event listener para cerrar
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.add('closing');
        setTimeout(() => notification.remove(), 300);
    });
    
    // Mostrar con animación
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto-cerrar después de un tiempo
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.add('closing');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

/**
 * Obtiene el icono para un tipo de notificación
 * @param {string} type - El tipo de notificación
 * @returns {string} - La clase del icono
 */
function getIconForNotificationType(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        case 'info': return 'fa-info-circle';
        default: return 'fa-info-circle';
    }
}

// Exportar funciones para uso en otros módulos
window.simulator = {
    loadCircuit,
    runSimulation,
    clearCircuit,
    saveCircuit,
    addQubit,
    removeQubit
};