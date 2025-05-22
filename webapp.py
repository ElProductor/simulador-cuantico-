import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import uvicorn
import uuid
import asyncio

# Importar módulos internos (simulación, visualización, IA, etc.)
from visualizer.circuit_visualizer import QuantumVisualizer
# Aquí se pueden importar otros módulos relevantes para simulación híbrida
from modules.hardware_simulation import main_view as hardware_main, secondary_view as hardware_secondary, user_customization as hardware_customize
from modules.quantum_ml import main_view as qml_main, secondary_view as qml_secondary, user_customization as qml_customize
from modules.quantum_games import main_view as games_main, secondary_view as games_secondary, user_customization as games_customize
from modules.quantum_notebook import main_view as notebook_main, secondary_view as notebook_secondary, user_customization as notebook_customize
from modules.hardware_comparison import main_view as compare_main, secondary_view as compare_secondary, user_customization as compare_customize

app = FastAPI(title="Simulador Híbrido Cuántico-Clásico Revolucionario")

# CORS para colaboración en tiempo real y despliegue cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para UI avanzada
app.mount("/static", StaticFiles(directory="static"), name="static")

# Estado global para colaboración y monitoreo
active_sessions: Dict[str, Dict[str, Any]] = {}

# --- ENDPOINTS PRINCIPALES ---

# --- ENDPOINTS DE MÓDULOS FUNCIONALES ---
@app.post("/api/hardware/main")
def hardware_main_endpoint(data: Dict[str, Any]):
    return hardware_main(data)

@app.post("/api/hardware/secondary")
def hardware_secondary_endpoint(data: Dict[str, Any]):
    return hardware_secondary(data)

@app.post("/api/hardware/customize")
def hardware_customize_endpoint(data: Dict[str, Any]):
    return hardware_customize(data)

@app.post("/api/qml/main")
def qml_main_endpoint(data: Dict[str, Any]):
    return qml_main(data)

@app.post("/api/qml/secondary")
def qml_secondary_endpoint(data: Dict[str, Any]):
    return qml_secondary(data)

@app.post("/api/qml/customize")
def qml_customize_endpoint(data: Dict[str, Any]):
    return qml_customize(data)

@app.post("/api/games/main")
def games_main_endpoint(data: Dict[str, Any]):
    return games_main(data)

@app.post("/api/games/secondary")
def games_secondary_endpoint(data: Dict[str, Any]):
    return games_secondary(data)

@app.post("/api/games/customize")
def games_customize_endpoint(data: Dict[str, Any]):
    return games_customize(data)

@app.post("/api/notebook/main")
def notebook_main_endpoint(data: Dict[str, Any]):
    return notebook_main(data)

@app.post("/api/notebook/secondary")
def notebook_secondary_endpoint(data: Dict[str, Any]):
    return notebook_secondary(data)

@app.post("/api/notebook/customize")
def notebook_customize_endpoint(data: Dict[str, Any]):
    return notebook_customize(data)

@app.post("/api/hardware_compare/main")
def compare_main_endpoint(data: Dict[str, Any]):
    return compare_main(data)

@app.post("/api/hardware_compare/secondary")
def compare_secondary_endpoint(data: Dict[str, Any]):
    return compare_secondary(data)

@app.post("/api/hardware_compare/customize")
def compare_customize_endpoint(data: Dict[str, Any]):
    return compare_customize(data)


@app.get("/", response_class=HTMLResponse)
def home():
    with open(os.path.join("static", "index.html"), encoding="utf-8") as f:
        return f.read()

@app.post("/api/simulate/hybrid")
def simulate_hybrid(data: Dict[str, Any]):
    """
    Endpoint para simulación híbrida cuántico-clásica.
    data: { 'circuit': ..., 'classical_params': ..., 'quantum_params': ... }
    """
    # Aquí se integraría el motor híbrido
    # resultado = hybrid_simulation(data)
    resultado = {"status": "ok", "message": "Simulación híbrida ejecutada (demo)", "data": data}
    return JSONResponse(content=resultado)

@app.post("/api/visualize/circuit")
def visualize_circuit(data: Dict[str, Any]):
    """
    Visualización avanzada de circuitos cuánticos.
    """
    visualizer = QuantumVisualizer()
    for op in data.get("operations", []):
        visualizer.add_operation(op["gate"], op["target"], op.get("control"))
    # Aquí se podría devolver una imagen codificada o datos para frontend
    return JSONResponse(content={"status": "ok", "message": "Visualización generada (demo)"})

@app.get("/api/tutorials")
def get_tutorials():
    """
    Devuelve tutoriales interactivos y ejemplos predefinidos.
    """
    # Demo: lista de tutoriales
    tutorials = [
        {"id": 1, "title": "Introducción a la computación cuántica", "level": "básico"},
        {"id": 2, "title": "Simulación híbrida avanzada", "level": "avanzado"}
    ]
    return JSONResponse(content={"tutorials": tutorials})

@app.websocket("/ws/collab/{session_id}")
async def websocket_collab(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in active_sessions:
        active_sessions[session_id] = {"users": [], "state": {}}
    active_sessions[session_id]["users"].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast a todos los usuarios de la sesión
            for user in active_sessions[session_id]["users"]:
                if user != websocket:
                    await user.send_text(data)
    except WebSocketDisconnect:
        active_sessions[session_id]["users"].remove(websocket)

@app.get("/api/monitoring")
def get_monitoring():
    """
    Monitoreo en vivo del estado del sistema y sesiones activas.
    """
    return JSONResponse(content={"active_sessions": list(active_sessions.keys())})

@app.post("/api/user/customize")
def customize_user(data: Dict[str, Any]):
    """
    Personalización de experiencia de usuario (preferencias, temas, accesibilidad).
    """
    # Guardar preferencias (demo)
    return JSONResponse(content={"status": "ok", "preferences": data})

# --- ENDPOINTS DE IA ASISTIDA (DEMO) ---
@app.post("/api/ai/assistant")
def ai_assistant(data: Dict[str, Any]):
    """
    Asistente IA para sugerencias, explicación de circuitos y ayuda contextual.
    """
    # Demo: respuesta estática
    return JSONResponse(content={"response": "¡Hola! Soy tu asistente IA. ¿En qué puedo ayudarte con tu circuito?"})

# --- MANEJO DE ERRORES Y LOGGING AVANZADO ---
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc), "message": "Error interno del simulador."})

# --- INICIO DEL SERVIDOR (para desarrollo local) ---
if __name__ == "__main__":
    uvicorn.run("webapp:app", host="0.0.0.0", port=8000, reload=True)