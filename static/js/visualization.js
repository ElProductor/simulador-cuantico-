/**
 * visualization.js - Visualización de resultados del simulador cuántico
 * Este archivo maneja la representación visual de los resultados de simulación
 * incluyendo histogramas, esferas de Bloch, matrices y diagramas de circuitos
 */

// Variables globales para gráficos
let histogramChart = null;
let blochSpheres = [];

// Elementos DOM principales
const histogramCanvas = document.getElementById('histogramChart');
const blochSpheresContainer = document.getElementById('blochSpheres');
const stateMatrixContainer = document.getElementById('stateMatrix');
const circuitDiagramCanvas = document.getElementById('circuitDiagram');

// Inicialización cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    initializeVisualizations();
});

/**
 * Inicializa las visualizaciones
 */
function initializeVisualizations() {
    // Inicializar el gráfico de histograma vacío
    initializeHistogram();
    
    // Preparar contenedores para otras visualizaciones
    prepareBlochSpheres();
}

/**
 * Inicializa el gráfico de histograma
 */
function initializeHistogram() {
    if (histogramChart) {
        histogramChart.destroy();
    }
    
    const ctx = histogramCanvas.getContext('2d');
    histogramChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['|0⟩', '|1⟩'],
            datasets: [{
                label: 'Probabilidad',
                data: [1, 0],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.6)',
                    'rgba(240, 147, 251, 0.6)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(240, 147, 251, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Probabilidad'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Estado'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Probabilidad: ${(context.raw * 100).toFixed(2)}%`;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Prepara los contenedores para las esferas de Bloch
 */
function prepareBlochSpheres() {
    // Limpiar contenedor
    blochSpheresContainer.innerHTML = '';
    
    // Crear mensaje de placeholder
    const placeholder = document.createElement('div');
    placeholder.className = 'bloch-placeholder';
    placeholder.textContent = 'Ejecute una simulación para ver las esferas de Bloch';
    blochSpheresContainer.appendChild(placeholder);
}

/**
 * Actualiza todas las visualizaciones con los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function updateVisualizations(results) {
    if (!results) return;
    
    // Determinar qué vista está activa
    const activeView = document.querySelector('.result-view.active').id;
    
    // Actualizar solo la visualización activa para optimizar rendimiento
    switch (activeView) {
        case 'histogramView':
            updateHistogram(results);
            break;
        case 'blochView':
            updateBlochSpheres(results);
            break;
        case 'matrixView':
            updateStateMatrix(results);
            break;
        case 'circuitView':
            updateCircuitDiagram(results);
            break;
    }
}

/**
 * Actualiza el histograma con los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function updateHistogram(results) {
    if (!results.counts) return;
    
    // Extraer datos de conteos
    const counts = results.counts;
    const labels = Object.keys(counts);
    const data = Object.values(counts).map(count => count / results.shots);
    
    // Actualizar datos del gráfico
    histogramChart.data.labels = labels;
    histogramChart.data.datasets[0].data = data;
    
    // Generar colores dinámicamente basados en el número de estados
    const colors = generateGradientColors(labels.length);
    histogramChart.data.datasets[0].backgroundColor = colors.map(color => `rgba(${color}, 0.6)`);
    histogramChart.data.datasets[0].borderColor = colors.map(color => `rgba(${color}, 1)`);
    
    // Actualizar opciones para ajustar la escala si es necesario
    histogramChart.options.scales.y.max = Math.max(...data) * 1.1;
    
    // Actualizar el gráfico
    histogramChart.update();
}

/**
 * Actualiza las esferas de Bloch con los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function updateBlochSpheres(results) {
    if (!results.statevector) return;
    
    // Limpiar contenedor
    blochSpheresContainer.innerHTML = '';
    blochSpheres = [];
    
    // Obtener número de qubits
    const numQubits = Math.log2(results.statevector.length);
    
    // Crear una esfera de Bloch para cada qubit
    for (let i = 0; i < numQubits; i++) {
        const sphereContainer = document.createElement('div');
        sphereContainer.className = 'bloch-sphere-container';
        
        const sphereLabel = document.createElement('div');
        sphereLabel.className = 'bloch-sphere-label';
        sphereLabel.textContent = `Qubit ${i}`;
        
        const sphereCanvas = document.createElement('canvas');
        sphereCanvas.className = 'bloch-sphere';
        sphereCanvas.width = 200;
        sphereCanvas.height = 200;
        
        sphereContainer.appendChild(sphereLabel);
        sphereContainer.appendChild(sphereCanvas);
        blochSpheresContainer.appendChild(sphereContainer);
        
        // Calcular coordenadas de Bloch para este qubit
        const blochCoordinates = calculateBlochCoordinates(results.statevector, i);
        
        // Renderizar esfera de Bloch
        renderBlochSphere(sphereCanvas, blochCoordinates);
    }
}

/**
 * Calcula las coordenadas de Bloch para un qubit específico
 * @param {Array} statevector - El vector de estado cuántico
 * @param {number} qubitIndex - El índice del qubit
 * @returns {Object} - Las coordenadas x, y, z en la esfera de Bloch
 */
function calculateBlochCoordinates(statevector, qubitIndex) {
    // Esta es una implementación simplificada
    // En un simulador real, se calcularía la matriz de densidad reducida
    // y se extraerían los valores de Bloch de ella
    
    // Por ahora, generamos valores aleatorios para demostración
    const x = Math.random() * 2 - 1;
    const y = Math.random() * 2 - 1;
    let z = Math.random() * 2 - 1;
    
    // Normalizar para asegurar que está en la esfera
    const norm = Math.sqrt(x*x + y*y + z*z);
    
    return {
        x: x / norm,
        y: y / norm,
        z: z / norm
    };
}

/**
 * Renderiza una esfera de Bloch con las coordenadas dadas
 * @param {HTMLCanvasElement} canvas - El elemento canvas para renderizar
 * @param {Object} coordinates - Las coordenadas x, y, z en la esfera de Bloch
 */
function renderBlochSphere(canvas, coordinates) {
    // Crear escena Three.js
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    
    // Configurar cámara
    camera.position.z = 2;
    
    // Añadir luz
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const pointLight = new THREE.PointLight(0xffffff, 0.8);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);
    
    // Crear esfera
    const sphereGeometry = new THREE.SphereGeometry(1, 32, 32);
    const sphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x667eea,
        transparent: true,
        opacity: 0.2,
        wireframe: false
    });
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    scene.add(sphere);
    
    // Crear ejes
    const axisLength = 1.2;
    
    // Eje X (rojo)
    const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-axisLength, 0, 0),
        new THREE.Vector3(axisLength, 0, 0)
    ]);
    const xAxisMaterial = new THREE.LineBasicMaterial({ color: 0xff0000 });
    const xAxis = new THREE.Line(xAxisGeometry, xAxisMaterial);
    scene.add(xAxis);
    
    // Eje Y (verde)
    const yAxisGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, -axisLength, 0),
        new THREE.Vector3(0, axisLength, 0)
    ]);
    const yAxisMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00 });
    const yAxis = new THREE.Line(yAxisGeometry, yAxisMaterial);
    scene.add(yAxis);
    
    // Eje Z (azul)
    const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, -axisLength),
        new THREE.Vector3(0, 0, axisLength)
    ]);
    const zAxisMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff });
    const zAxis = new THREE.Line(zAxisGeometry, zAxisMaterial);
    scene.add(zAxis);
    
    // Crear vector de estado
    const vectorGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(
            coordinates.x,
            coordinates.y,
            coordinates.z
        )
    ]);
    const vectorMaterial = new THREE.LineBasicMaterial({ color: 0xff8906, linewidth: 3 });
    const vector = new THREE.Line(vectorGeometry, vectorMaterial);
    scene.add(vector);
    
    // Añadir punto en la punta del vector
    const pointGeometry = new THREE.SphereGeometry(0.05, 16, 16);
    const pointMaterial = new THREE.MeshBasicMaterial({ color: 0xff8906 });
    const point = new THREE.Mesh(pointGeometry, pointMaterial);
    point.position.set(coordinates.x, coordinates.y, coordinates.z);
    scene.add(point);
    
    // Función de animación
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotar la esfera lentamente
        sphere.rotation.x += 0.005;
        sphere.rotation.y += 0.005;
        
        // Mantener los ejes y el vector estáticos
        xAxis.rotation.copy(sphere.rotation);
        yAxis.rotation.copy(sphere.rotation);
        zAxis.rotation.copy(sphere.rotation);
        vector.rotation.copy(sphere.rotation);
        point.rotation.copy(sphere.rotation);
        
        renderer.render(scene, camera);
    }
    
    // Iniciar animación
    animate();
    
    // Guardar referencia para limpieza posterior
    blochSpheres.push({
        scene,
        camera,
        renderer,
        animate
    });
}

/**
 * Actualiza la matriz de estado con los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function updateStateMatrix(results) {
    if (!results.statevector) return;
    
    // Limpiar contenedor
    stateMatrixContainer.innerHTML = '';
    
    // Crear tabla para la matriz
    const table = document.createElement('table');
    table.className = 'state-matrix';
    
    // Crear encabezados
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const stateHeader = document.createElement('th');
    stateHeader.textContent = 'Estado';
    headerRow.appendChild(stateHeader);
    
    const amplitudeHeader = document.createElement('th');
    amplitudeHeader.textContent = 'Amplitud';
    headerRow.appendChild(amplitudeHeader);
    
    const probabilityHeader = document.createElement('th');
    probabilityHeader.textContent = 'Probabilidad';
    headerRow.appendChild(probabilityHeader);
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Crear cuerpo de la tabla
    const tbody = document.createElement('tbody');
    
    // Obtener número de qubits
    const numQubits = Math.log2(results.statevector.length);
    
    // Crear filas para cada estado
    for (let i = 0; i < results.statevector.length; i++) {
        const row = document.createElement('tr');
        
        // Convertir índice a representación binaria (estado)
        const stateBinary = i.toString(2).padStart(numQubits, '0');
        const stateKet = `|${stateBinary}⟩`;
        
        const stateCell = document.createElement('td');
        stateCell.textContent = stateKet;
        row.appendChild(stateCell);
        
        // Amplitud (número complejo)
        const amplitude = results.statevector[i];
        const amplitudeCell = document.createElement('td');
        amplitudeCell.textContent = formatComplexNumber(amplitude);
        row.appendChild(amplitudeCell);
        
        // Probabilidad
        const probability = Math.pow(Math.abs(amplitude), 2);
        const probabilityCell = document.createElement('td');
        probabilityCell.textContent = probability.toFixed(4);
        row.appendChild(probabilityCell);
        
        tbody.appendChild(row);
    }
    
    table.appendChild(tbody);
    stateMatrixContainer.appendChild(table);
}

/**
 * Actualiza el diagrama de circuito con los resultados de la simulación
 * @param {Object} results - Los resultados de la simulación
 */
function updateCircuitDiagram(results) {
    if (!results.circuit) return;
    
    // Obtener contexto del canvas
    const ctx = circuitDiagramCanvas.getContext('2d');
    
    // Limpiar canvas
    ctx.clearRect(0, 0, circuitDiagramCanvas.width, circuitDiagramCanvas.height);
    
    // Configurar dimensiones del canvas
    const numQubits = results.circuit.num_qubits;
    const numGates = results.circuit.gates.length;
    
    circuitDiagramCanvas.width = Math.max(600, numGates * 60 + 100);
    circuitDiagramCanvas.height = numQubits * 60 + 60;
    
    // Dibujar líneas de qubits
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 2;
    
    for (let i = 0; i < numQubits; i++) {
        const y = (i + 1) * 60;
        
        // Dibujar etiqueta de qubit
        ctx.fillStyle = '#00d4ff';
        ctx.font = '16px var(--font-family)';
        ctx.textAlign = 'right';
        ctx.fillText(`q${i}:`, 40, y + 5);
        
        // Dibujar línea
        ctx.beginPath();
        ctx.moveTo(50, y);
        ctx.lineTo(circuitDiagramCanvas.width - 50, y);
        ctx.stroke();
    }
    
    // Dibujar puertas
    if (results.circuit.gates) {
        for (let i = 0; i < results.circuit.gates.length; i++) {
            const gate = results.circuit.gates[i];
            const x = 80 + i * 60;
            
            // Dibujar puerta
            drawGate(ctx, gate, x);
        }
    }
}

/**
 * Dibuja una puerta cuántica en el canvas
 * @param {CanvasRenderingContext2D} ctx - El contexto del canvas
 * @param {Object} gate - La puerta a dibujar
 * @param {number} x - La posición x en el canvas
 */
function drawGate(ctx, gate, x) {
    const targetQubit = gate.target_qubits[0];
    const y = (targetQubit + 1) * 60;
    
    // Dibujar caja de puerta
    ctx.fillStyle = getGateColor(gate.gate_type);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    
    // Dibujar forma de puerta
    ctx.beginPath();
    ctx.roundRect(x - 20, y - 20, 40, 40, 5);
    ctx.fill();
    ctx.stroke();
    
    // Dibujar texto de puerta
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 16px var(--font-family)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(gate.gate_type, x, y);
    
    // Si es una puerta controlada, dibujar línea de control y punto
    if (gate.control_qubits && gate.control_qubits.length > 0) {
        const controlQubit = gate.control_qubits[0];
        const controlY = (controlQubit + 1) * 60;
        
        // Dibujar línea de control
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, controlY);
        ctx.lineTo(x, y - 20);
        ctx.stroke();
        
        // Dibujar punto de control
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(x, controlY, 5, 0, Math.PI * 2);
        ctx.fill();
    }
}

/**
 * Obtiene el color para un tipo de puerta
 * @param {string} gateType - El tipo de puerta
 * @returns {string} - El color en formato CSS
 */
function getGateColor(gateType) {
    const gateColors = {
        'X': '#f093fb',
        'Y': '#f5576c',
        'Z': '#667eea',
        'H': '#00d4ff',
        'S': '#00f2fe',
        'T': '#764ba2',
        'CNOT': '#f093fb',
        'CZ': '#667eea',
        'SWAP': '#00d4ff',
        'RX': '#f5576c',
        'RY': '#f5576c',
        'RZ': '#f5576c',
        'TOFFOLI': '#f093fb',
        'FREDKIN': '#00d4ff',
        'QFT': '#00f2fe'
    };
    
    return gateColors[gateType] || '#00d4ff';
}

/**
 * Genera colores en gradiente para el histograma
 * @param {number} count - El número de colores a generar
 * @returns {Array} - Array de strings de colores en formato 'r, g, b'
 */
function generateGradientColors(count) {
    const colors = [];
    
    // Colores de inicio y fin del gradiente
    const startColor = [102, 126, 234]; // #667eea
    const endColor = [240, 147, 251]; // #f093fb
    
    for (let i = 0; i < count; i++) {
        const ratio = count === 1 ? 0.5 : i / (count - 1);
        
        const r = Math.round(startColor[0] + ratio * (endColor[0] - startColor[0]));
        const g = Math.round(startColor[1] + ratio * (endColor[1] - startColor[1]));
        const b = Math.round(startColor[2] + ratio * (endColor[2] - startColor[2]));
        
        colors.push(`${r}, ${g}, ${b}`);
    }
    
    return colors;
}

/**
 * Formatea un número complejo para mostrar
 * @param {Complex} complex - El número complejo
 * @returns {string} - Representación formateada
 */
function formatComplexNumber(complex) {
    // Si es un objeto con partes real e imaginaria
    if (typeof complex === 'object' && complex !== null) {
        const real = complex.real.toFixed(4);
        const imag = complex.imag.toFixed(4);
        
        if (complex.imag >= 0) {
            return `${real} + ${imag}i`;
        } else {
            return `${real} - ${Math.abs(complex.imag).toFixed(4)}i`;
        }
    }
    // Si es un número
    else if (typeof complex === 'number') {
        return complex.toFixed(4);
    }
    // Valor por defecto
    return '0.0000';
}

// Exportar funciones para uso en otros módulos
window.visualization = {
    updateVisualizations
};