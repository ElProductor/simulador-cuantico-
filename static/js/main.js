/**
 * main.js - Funcionalidad principal para el Simulador Cuántico
 * Este archivo maneja la interfaz de usuario, eventos y la configuración general
 */

// Configuración inicial y variables globales
let currentTheme = 'dark';
let currentLanguage = 'es';
let currentLayout = 'standard';
let advancedModeEnabled = false;
let autoSaveEnabled = true;

// Elementos DOM principales
const themeSwitcher = document.getElementById('themeSwitcher');
const userThemeSelect = document.getElementById('userTheme');
const userLanguageSelect = document.getElementById('userLanguage');
const userLayoutSelect = document.getElementById('userLayout');
const advancedModeCheckbox = document.getElementById('advancedMode');
const autoSaveCheckbox = document.getElementById('autoSave');
const showTooltipsCheckbox = document.getElementById('showTooltips');
const navItems = document.querySelectorAll('.nav-item');
const algorithmItems = document.querySelectorAll('.algorithm-item');
const tutorialItems = document.querySelectorAll('.tutorial-item');
const advancedConfigModal = document.getElementById('advancedConfigModal');
const closeModalBtn = document.querySelector('.close-modal');
const cancelConfigBtn = document.getElementById('cancelConfig');
const saveConfigBtn = document.getElementById('saveConfig');

// Inicialización cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    setupEventListeners();
    loadUserPreferences();
});

/**
 * Inicializa la interfaz de usuario
 */
function initializeUI() {
    // Activar el primer elemento de navegación por defecto
    if (navItems.length > 0) {
        navItems[0].classList.add('active');
    }
    
    // Configurar tema inicial
    applyTheme(currentTheme);
    
    // Inicializar tooltips si están habilitados
    if (showTooltipsCheckbox.checked) {
        initializeTooltips();
    }
}

/**
 * Configura los event listeners para los elementos de la UI
 */
function setupEventListeners() {
    // Event listener para el cambio de tema
    themeSwitcher.addEventListener('click', toggleTheme);
    userThemeSelect.addEventListener('change', (e) => applyTheme(e.target.value));
    
    // Event listeners para las opciones de usuario
    userLanguageSelect.addEventListener('change', (e) => changeLanguage(e.target.value));
    userLayoutSelect.addEventListener('change', (e) => changeLayout(e.target.value));
    advancedModeCheckbox.addEventListener('change', (e) => toggleAdvancedMode(e.target.checked));
    autoSaveCheckbox.addEventListener('change', (e) => toggleAutoSave(e.target.checked));
    showTooltipsCheckbox.addEventListener('change', (e) => toggleTooltips(e.target.checked));
    
    // Event listeners para los elementos de navegación
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(navItem => navItem.classList.remove('active'));
            item.classList.add('active');
        });
    });
    
    // Event listeners para algoritmos predefinidos
    algorithmItems.forEach(item => {
        item.addEventListener('click', () => loadAlgorithm(item.dataset.algorithm));
    });
    
    // Event listeners para tutoriales
    tutorialItems.forEach(item => {
        item.addEventListener('click', () => loadTutorial(item.dataset.tutorial));
    });
    
    // Event listeners para el modal de configuración avanzada
    closeModalBtn.addEventListener('click', closeModal);
    cancelConfigBtn.addEventListener('click', closeModal);
    saveConfigBtn.addEventListener('click', saveAdvancedConfig);
}

/**
 * Carga las preferencias del usuario desde localStorage
 */
function loadUserPreferences() {
    // Cargar tema
    const savedTheme = localStorage.getItem('userTheme');
    if (savedTheme) {
        currentTheme = savedTheme;
        userThemeSelect.value = savedTheme;
        applyTheme(savedTheme);
    }
    
    // Cargar idioma
    const savedLanguage = localStorage.getItem('userLanguage');
    if (savedLanguage) {
        currentLanguage = savedLanguage;
        userLanguageSelect.value = savedLanguage;
    }
    
    // Cargar layout
    const savedLayout = localStorage.getItem('userLayout');
    if (savedLayout) {
        currentLayout = savedLayout;
        userLayoutSelect.value = savedLayout;
        applyLayout(savedLayout);
    }
    
    // Cargar modo avanzado
    const savedAdvancedMode = localStorage.getItem('advancedMode');
    if (savedAdvancedMode !== null) {
        advancedModeEnabled = savedAdvancedMode === 'true';
        advancedModeCheckbox.checked = advancedModeEnabled;
        toggleAdvancedMode(advancedModeEnabled);
    }
    
    // Cargar autoguardado
    const savedAutoSave = localStorage.getItem('autoSave');
    if (savedAutoSave !== null) {
        autoSaveEnabled = savedAutoSave === 'true';
        autoSaveCheckbox.checked = autoSaveEnabled;
    }
    
    // Cargar tooltips
    const savedShowTooltips = localStorage.getItem('showTooltips');
    if (savedShowTooltips !== null) {
        const showTooltips = savedShowTooltips === 'true';
        showTooltipsCheckbox.checked = showTooltips;
        toggleTooltips(showTooltips);
    }
}

/**
 * Alterna entre temas claro y oscuro
 */
function toggleTheme() {
    themeSwitcher.classList.toggle('active');
    const newTheme = themeSwitcher.classList.contains('active') ? 'light' : 'dark';
    applyTheme(newTheme);
    userThemeSelect.value = newTheme;
}

/**
 * Aplica un tema específico
 * @param {string} theme - El tema a aplicar
 */
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('userTheme', theme);
    
    // Actualizar el estado del theme switcher
    if (theme === 'dark') {
        themeSwitcher.classList.remove('active');
    } else {
        themeSwitcher.classList.add('active');
    }
}

/**
 * Cambia el idioma de la interfaz
 * @param {string} language - El idioma a aplicar
 */
function changeLanguage(language) {
    currentLanguage = language;
    localStorage.setItem('userLanguage', language);
    // Aquí se implementaría la lógica para cambiar los textos de la interfaz
    console.log(`Idioma cambiado a: ${language}`);
}

/**
 * Cambia el layout de la interfaz
 * @param {string} layout - El layout a aplicar
 */
function changeLayout(layout) {
    currentLayout = layout;
    localStorage.setItem('userLayout', layout);
    applyLayout(layout);
}

/**
 * Aplica un layout específico
 * @param {string} layout - El layout a aplicar
 */
function applyLayout(layout) {
    // Eliminar clases de layout anteriores
    document.body.classList.remove('layout-standard', 'layout-compact', 'layout-expanded', 'layout-professional');
    // Aplicar nueva clase de layout
    document.body.classList.add(`layout-${layout}`);
    console.log(`Layout cambiado a: ${layout}`);
}

/**
 * Activa o desactiva el modo avanzado
 * @param {boolean} enabled - Si el modo avanzado está habilitado
 */
function toggleAdvancedMode(enabled) {
    advancedModeEnabled = enabled;
    localStorage.setItem('advancedMode', enabled);
    
    // Mostrar u ocultar elementos avanzados
    const advancedElements = document.querySelectorAll('.advanced-feature');
    advancedElements.forEach(element => {
        element.style.display = enabled ? 'block' : 'none';
    });
    
    console.log(`Modo avanzado: ${enabled ? 'activado' : 'desactivado'}`);
}

/**
 * Activa o desactiva el autoguardado
 * @param {boolean} enabled - Si el autoguardado está habilitado
 */
function toggleAutoSave(enabled) {
    autoSaveEnabled = enabled;
    localStorage.setItem('autoSave', enabled);
    console.log(`Autoguardado: ${enabled ? 'activado' : 'desactivado'}`);
}

/**
 * Activa o desactiva los tooltips
 * @param {boolean} enabled - Si los tooltips están habilitados
 */
function toggleTooltips(enabled) {
    localStorage.setItem('showTooltips', enabled);
    if (enabled) {
        initializeTooltips();
    } else {
        // Desactivar tooltips
        console.log('Tooltips desactivados');
    }
}

/**
 * Inicializa los tooltips en la interfaz
 */
function initializeTooltips() {
    console.log('Tooltips activados');
    // Aquí se implementaría la lógica para inicializar tooltips
}

/**
 * Carga un algoritmo predefinido
 * @param {string} algorithmName - El nombre del algoritmo a cargar
 */
function loadAlgorithm(algorithmName) {
    console.log(`Cargando algoritmo: ${algorithmName}`);
    // Aquí se implementaría la lógica para cargar el algoritmo seleccionado
    // Esto podría incluir una llamada a la API para obtener la configuración del algoritmo
    
    // Ejemplo de llamada a la API
    fetch(`/api/algorithms/${algorithmName}`)
        .then(response => response.json())
        .then(data => {
            // Pasar los datos al simulador
            if (window.simulator) {
                window.simulator.loadCircuit(data.circuit);
            }
        })
        .catch(error => console.error('Error al cargar el algoritmo:', error));
}

/**
 * Carga un tutorial
 * @param {string} tutorialName - El nombre del tutorial a cargar
 */
function loadTutorial(tutorialName) {
    console.log(`Cargando tutorial: ${tutorialName}`);
    // Aquí se implementaría la lógica para cargar el tutorial seleccionado
    
    // Ejemplo de llamada a la API
    fetch(`/api/tutorials/${tutorialName}`)
        .then(response => response.json())
        .then(data => {
            // Mostrar el contenido del tutorial en un modal o sección específica
            showTutorialContent(data);
        })
        .catch(error => console.error('Error al cargar el tutorial:', error));
}

/**
 * Muestra el contenido de un tutorial
 * @param {Object} tutorialData - Los datos del tutorial
 */
function showTutorialContent(tutorialData) {
    // Crear un modal para mostrar el tutorial
    const modalBody = document.querySelector('.modal-body');
    const modalHeader = document.querySelector('.modal-header h3');
    
    modalHeader.textContent = tutorialData.title;
    modalBody.innerHTML = tutorialData.content;
    
    // Mostrar el modal
    advancedConfigModal.classList.add('active');
}

/**
 * Cierra el modal de configuración avanzada
 */
function closeModal() {
    advancedConfigModal.classList.remove('active');
}

/**
 * Guarda la configuración avanzada
 */
function saveAdvancedConfig() {
    // Aquí se implementaría la lógica para guardar la configuración avanzada
    console.log('Guardando configuración avanzada');
    closeModal();
}

// Exportar funciones para uso en otros módulos
window.uiController = {
    applyTheme,
    changeLanguage,
    changeLayout,
    toggleAdvancedMode,
    loadAlgorithm,
    loadTutorial
};