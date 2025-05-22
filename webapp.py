import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional, Set
import uvicorn
import uuid
import asyncio
import json
import traceback
from datetime import datetime
from contextlib import asynccontextmanager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modelos Pydantic para validación de datos
class CircuitOperation(BaseModel):
    gate: str
    target: int
    control: Optional[int] = None
    parameters: Optional[List[float]] = None

class HybridSimulationRequest(BaseModel):
    circuit: List[CircuitOperation]
    classical_params: Optional[Dict[str, Any]] = {}
    quantum_params: Optional[Dict[str, Any]] = {}
    num_qubits: int = 2

class VisualizationRequest(BaseModel):
    operations: List[CircuitOperation]
    num_qubits: int = 2
    style: Optional[str] = "default"

class UserPreferences(BaseModel):
    theme: str = "dark"
    language: str = "es"
    accessibility: Optional[Dict[str, Any]] = {}

class AIAssistantRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}

# Estado global para colaboración y monitoreo
class AppState:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        self.system_stats = {
            "start_time": datetime.now(),
            "requests_count": 0,
            "errors_count": 0
        }
    
    def add_connection(self, session_id: str, websocket: WebSocket):
        if session_id not in self.user_connections:
            self.user_connections[session_id] = set()
        self.user_connections[session_id].add(websocket)
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "user_count": 0
            }
        self.active_sessions[session_id]["user_count"] = len(self.user_connections[session_id])
    
    def remove_connection(self, session_id: str, websocket: WebSocket):
        if session_id in self.user_connections:
            self.user_connections[session_id].discard(websocket)
            if not self.user_connections[session_id]:
                del self.user_connections[session_id]
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
            else:
                self.active_sessions[session_id]["user_count"] = len(self.user_connections[session_id])
    
    def increment_requests(self):
        self.system_stats["requests_count"] += 1
    
    def increment_errors(self):
        self.system_stats["errors_count"] += 1

# Instancia global del estado
app_state = AppState()

# Inicialización de directorios
def ensure_directories():
    """Crear directorios necesarios si no existen"""
    dirs = ["static", "templates", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

# Simulador básico de módulos
class ModuleSimulator:
    """Simulador básico para los módulos que no están implementados"""
    
    @staticmethod
    def safe_execute(module_name: str, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Simular procesamiento del módulo
            logger.info(f"Ejecutando {module_name}.{operation} con datos: {len(str(data))} chars")
            
            result = {
                "status": "success",
                "module": module_name,
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "processed": True,
                    "input_size": len(str(data)),
                    "message": f"Operación {operation} en módulo {module_name} ejecutada correctamente"
                }
            }
            
            # Agregar datos específicos según el módulo
            if module_name == "hardware":
                result["data"]["simulation_type"] = "quantum_hardware"
                result["data"]["qubits"] = data.get("qubits", 2)
            elif module_name == "qml":
                result["data"]["model_type"] = "quantum_neural_network"
                result["data"]["layers"] = data.get("layers", 3)
            elif module_name == "games":
                result["data"]["game_type"] = "quantum_puzzle"
                result["data"]["level"] = data.get("level", 1)
            elif module_name == "notebook":
                result["data"]["cell_type"] = "quantum_code"
                result["data"]["execution_time"] = "0.5s"
            elif module_name == "hardware_compare":
                result["data"]["comparison_type"] = "performance_analysis"
                result["data"]["platforms"] = ["IBM", "Google", "Rigetti"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error en {module_name}.{operation}: {str(e)}")
            app_state.increment_errors()
            return {
                "status": "error",
                "module": module_name,
                "operation": operation,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Contexto de aplicación para inicialización
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando aplicación...")
    ensure_directories()
    create_default_html()
    logger.info("Aplicación iniciada correctamente")
    yield
    # Shutdown
    logger.info("Cerrando aplicación...")

# Crear instancia de FastAPI
app = FastAPI(
    title="Simulador Híbrido Cuántico-Clásico",
    description="Plataforma avanzada para simulación cuántica híbrida",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware de CORS optimizado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware para conteo de requests
@app.middleware("http")
async def count_requests(request: Request, call_next):
    app_state.increment_requests()
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()
    logger.info(f"{request.method} {request.url} - {response.status_code} - {(end_time - start_time).total_seconds():.3f}s")
    return response

# Crear HTML por defecto si no existe
def create_default_html():
    html_path = Path("static/index.html")
    if not html_path.exists():
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador Cuántico Híbrido</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .module { background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #45a049; }
        .status { padding: 10px; background: #333; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Simulador Cuántico Híbrido</h1>
            <p>Plataforma avanzada para simulación cuántica en tiempo real</p>
        </div>
        
        <div class="module">
            <h3>📊 Estado del Sistema</h3>
            <div id="status" class="status">Cargando...</div>
            <button class="btn" onclick="checkStatus()">Actualizar Estado</button>
        </div>
        
        <div class="module">
            <h3>🔬 Simulación Híbrida</h3>
            <button class="btn" onclick="runSimulation()">Ejecutar Simulación</button>
            <div id="simulation-result" class="status" style="display:none;"></div>
        </div>
        
        <div class="module">
            <h3>🎮 Módulos Disponibles</h3>
            <button class="btn" onclick="testModule('hardware')">Hardware Cuántico</button>
            <button class="btn" onclick="testModule('qml')">Quantum ML</button>
            <button class="btn" onclick="testModule('games')">Juegos Cuánticos</button>
            <button class="btn" onclick="testModule('notebook')">Notebook</button>
            <button class="btn" onclick="testModule('hardware_compare')">Comparación HW</button>
        </div>
    </div>

    <script>
        async function checkStatus() {
            try {
                const response = await fetch('/api/monitoring');
                const data = await response.json();
                document.getElementById('status').innerHTML = 
                    `<strong>✅ Sistema Operativo</strong><br>
                     Sesiones activas: ${data.active_sessions?.length || 0}<br>
                     Requests: ${data.system_stats?.requests_count || 0}<br>
                     Errores: ${data.system_stats?.errors_count || 0}`;
            } catch (error) {
                document.getElementById('status').innerHTML = '❌ Error al conectar con el servidor';
            }
        }
        
        async function runSimulation() {
            const resultDiv = document.getElementById('simulation-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '⏳ Ejecutando simulación...';
            
            try {
                const response = await fetch('/api/simulate/hybrid', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        circuit: [{gate: 'H', target: 0}, {gate: 'CNOT', target: 1, control: 0}],
                        num_qubits: 2
                    })
                });
                const data = await response.json();
                resultDiv.innerHTML = `✅ ${data.message || 'Simulación completada'}`;
            } catch (error) {
                resultDiv.innerHTML = '❌ Error en la simulación';
            }
        }
        
        async function testModule(moduleName) {
            try {
                const response = await fetch(`/api/${moduleName}/main`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test: true, module: moduleName})
                });
                const data = await response.json();
                alert(`Módulo ${moduleName}: ${data.status === 'success' ? '✅ Operativo' : '❌ Error'}`);
            } catch (error) {
                alert(`Módulo ${moduleName}: ❌ Error de conexión`);
            }
        }
        
        // Cargar estado inicial
        checkStatus();
        setInterval(checkStatus, 30000); // Actualizar cada 30 segundos
    </script>
</body>
</html>"""
        html_path.write_text(html_content, encoding='utf-8')

# Montar archivos estáticos
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"No se pudo montar directorio static: {e}")

# --- ENDPOINTS PRINCIPALES ---

@app.get("/", response_class=HTMLResponse)
def home():
    """Página principal de la aplicación"""
    try:
        html_path = Path("static/index.html")
        if html_path.exists():
            return html_path.read_text(encoding="utf-8")
        else:
            create_default_html()
            return html_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error al cargar página principal: {e}")
        return HTMLResponse(content="<h1>Error al cargar la aplicación</h1>", status_code=500)

@app.get("/health")
def health_check():
    """Endpoint de salud para Render"""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - app_state.system_stats["start_time"]),
        "version": "2.0.0"
    })

# --- ENDPOINTS DE MÓDULOS FUNCIONALES ---

# Hardware Cuántico
@app.post("/api/hardware/main")
def hardware_main_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware", "main", data))

@app.post("/api/hardware/secondary")
def hardware_secondary_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware", "secondary", data))

@app.post("/api/hardware/customize")
def hardware_customize_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware", "customize", data))

# Quantum ML
@app.post("/api/qml/main")
def qml_main_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("qml", "main", data))

@app.post("/api/qml/secondary")
def qml_secondary_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("qml", "secondary", data))

@app.post("/api/qml/customize")
def qml_customize_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("qml", "customize", data))

# Juegos Cuánticos
@app.post("/api/games/main")
def games_main_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("games", "main", data))

@app.post("/api/games/secondary")
def games_secondary_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("games", "secondary", data))

@app.post("/api/games/customize")
def games_customize_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("games", "customize", data))

# Notebook
@app.post("/api/notebook/main")
def notebook_main_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("notebook", "main", data))

@app.post("/api/notebook/secondary")
def notebook_secondary_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("notebook", "secondary", data))

@app.post("/api/notebook/customize")
def notebook_customize_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("notebook", "customize", data))

# Comparación de Hardware
@app.post("/api/hardware_compare/main")
def compare_main_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware_compare", "main", data))

@app.post("/api/hardware_compare/secondary")
def compare_secondary_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware_compare", "secondary", data))

@app.post("/api/hardware_compare/customize")
def compare_customize_endpoint(data: dict):
    return JSONResponse(content=ModuleSimulator.safe_execute("hardware_compare", "customize", data))

# --- ENDPOINTS DE SIMULACIÓN ---

@app.post("/api/simulate/hybrid")
def simulate_hybrid(request: HybridSimulationRequest):
    """Endpoint para simulación híbrida cuántico-clásica"""
    try:
        logger.info(f"Iniciando simulación híbrida con {request.num_qubits} qubits")
        
        # Simular procesamiento
        result = {
            "status": "success",
            "message": f"Simulación híbrida completada exitosamente",
            "timestamp": datetime.now().isoformat(),
            "results": {
                "num_qubits": request.num_qubits,
                "operations_count": len(request.circuit),
                "execution_time": "0.45s",
                "fidelity": 0.987,
                "measurements": {
                    "0": 0.6,
                    "1": 0.4
                }
            },
            "circuit_summary": [
                {"gate": op.gate, "target": op.target, "control": op.control}
                for op in request.circuit
            ]
        }
        
        return JSONResponse(content=result)
        
    except ValidationError as e:
        app_state.increment_errors()
        raise HTTPException(status_code=422, detail=f"Error de validación: {str(e)}")
    except Exception as e:
        app_state.increment_errors()
        logger.error(f"Error en simulación híbrida: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/api/visualize/circuit")
def visualize_circuit(request: VisualizationRequest):
    """Visualización avanzada de circuitos cuánticos"""
    try:
        result = {
            "status": "success",
            "message": "Visualización generada correctamente",
            "timestamp": datetime.now().isoformat(),
            "visualization": {
                "num_qubits": request.num_qubits,
                "operations": len(request.operations),
                "style": request.style,
                "depth": max([op.target for op in request.operations], default=0) + 1,
                "gates_used": list(set([op.gate for op in request.operations])),
                "svg_data": "<!-- SVG visualization would be generated here -->"
            }
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        app_state.increment_errors()
        logger.error(f"Error en visualización: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# --- ENDPOINTS DE CONTENIDO ---

@app.get("/api/tutorials")
def get_tutorials():
    """Devuelve tutoriales interactivos y ejemplos predefinidos"""
    tutorials = [
        {
            "id": 1,
            "title": "Introducción a la Computación Cuántica",
            "level": "básico",
            "duration": "30 min",
            "description": "Conceptos fundamentales de qubits y puertas cuánticas",
            "topics": ["Qubits", "Superposición", "Entrelazamiento"]
        },
        {
            "id": 2,
            "title": "Simulación Híbrida Avanzada",
            "level": "avanzado",
            "duration": "60 min",
            "description": "Técnicas avanzadas de simulación híbrida",
            "topics": ["Algoritmos VQE", "QAOA", "Optimización híbrida"]
        },
        {
            "id": 3,
            "title": "Quantum Machine Learning",
            "level": "intermedio",
            "duration": "45 min",
            "description": "Aplicación de ML en sistemas cuánticos",
            "topics": ["QNN", "Clasificación cuántica", "Feature maps"]
        }
    ]
    
    return JSONResponse(content={
        "tutorials": tutorials,
        "total": len(tutorials),
        "timestamp": datetime.now().isoformat()
    })

# --- WEBSOCKETS ---

@app.websocket("/ws/collab/{session_id}")
async def websocket_collab(websocket: WebSocket, session_id: str):
    """WebSocket para colaboración en tiempo real"""
    await websocket.accept()
    app_state.add_connection(session_id, websocket)
    
    try:
        logger.info(f"Nueva conexión WebSocket en sesión {session_id}")
        
        # Enviar mensaje de bienvenida
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Conectado exitosamente"
        }))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Procesar el mensaje
            broadcast_message = {
                "type": "broadcast",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "data": message
            }
            
            # Broadcast a todos los usuarios de la sesión excepto el remitente
            if session_id in app_state.user_connections:
                for user_ws in app_state.user_connections[session_id]:
                    if user_ws != websocket:
                        try:
                            await user_ws.send_text(json.dumps(broadcast_message))
                        except:
                            # Conexión cerrada, se limpiará automáticamente
                            pass
                            
    except WebSocketDisconnect:
        logger.info(f"Desconexión WebSocket en sesión {session_id}")
    except Exception as e:
        logger.error(f"Error en WebSocket {session_id}: {str(e)}")
    finally:
        app_state.remove_connection(session_id, websocket)

# --- ENDPOINTS DE MONITOREO ---

@app.get("/api/monitoring")
def get_monitoring():
    """Monitoreo en vivo del estado del sistema"""
    uptime = datetime.now() - app_state.system_stats["start_time"]
    
    return JSONResponse(content={
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(uptime),
        "active_sessions": list(app_state.active_sessions.keys()),
        "system_stats": {
            **app_state.system_stats,
            "start_time": app_state.system_stats["start_time"].isoformat()
        },
        "session_details": {
            session_id: {
                **session_data,
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat()
            }
            for session_id, session_data in app_state.active_sessions.items()
        }
    })

# --- ENDPOINTS DE PERSONALIZACIÓN ---

@app.post("/api/user/customize")
def customize_user(preferences: UserPreferences):
    """Personalización de experiencia de usuario"""
    try:
        return JSONResponse(content={
            "status": "success",
            "message": "Preferencias actualizadas correctamente",
            "preferences": preferences.dict(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        app_state.increment_errors()
        raise HTTPException(status_code=500, detail=f"Error al actualizar preferencias: {str(e)}")

# --- ENDPOINTS DE IA ---

@app.post("/api/ai/assistant")
def ai_assistant(request: AIAssistantRequest):
    """Asistente IA para sugerencias y ayuda contextual"""
    try:
        # Respuestas inteligentes basadas en el contexto
        responses = {
            "help": "¡Hola! Soy tu asistente cuántico. Puedo ayudarte con simulaciones, explicar conceptos cuánticos y optimizar tus circuitos.",
            "circuit": "Para crear un circuito eficiente, te recomiendo comenzar con puertas básicas como H y CNOT. ¿Qué tipo de algoritmo quieres implementar?",
            "error": "He detectado un posible error en tu circuito. Revisa las conexiones entre qubits y asegúrate de que los índices sean correctos.",
            "optimization": "Puedo sugerir varias optimizaciones para tu circuito: reducir la profundidad, minimizar puertas ruidosas, o usar equivalencias de puertas."
        }
        
        # Análisis simple del mensaje
        message_lower = request.message.lower()
        if any(word in message_lower for word in ["hola", "ayuda", "help"]):
            response = responses["help"]
        elif any(word in message_lower for word in ["circuito", "circuit"]):
            response = responses["circuit"]
        elif any(word in message_lower for word in ["error", "problema"]):
            response = responses["error"]
        elif any(word in message_lower for word in ["optimizar", "mejorar"]):
            response = responses["optimization"]
        else:
            response = f"Entiendo que me preguntas sobre: '{request.message}'. ¿Podrías ser más específico sobre qué aspecto de la computación cuántica te interesa?"
        
        return JSONResponse(content={
            "response": response,
            "context": request.context,
            "timestamp": datetime.now().isoformat(),
            "suggestions": [
                "Crear un nuevo circuito",
                "Optimizar circuito existente",
                "Explicar conceptos cuánticos",
                "Revisar errores comunes"
            ]
        })
        
    except Exception as e:
        app_state.increment_errors()
        logger.error(f"Error en asistente IA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del asistente: {str(e)}")

# --- MANEJO DE ERRORES ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_state.increment_errors()
    logger.error(f"Error global: {str(exc)}\nTraceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.",
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    )

# --- CONFIGURACIÓN PARA RENDER ---

def get_port():
    """Obtener puerto desde variable de entorno (para Render)"""
    return int(os.environ.get("PORT", 8000))

def get_host():
    """Obtener host desde variable de entorno"""
    return os.environ.get("HOST", "0.0.0.0")

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    port = get_port()
    host = get_host()
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    
    uvicorn.run(
        "webapp:app",
        host=host,
        port=port,
        reload=False,  # Desactivado para producción
        access_log=True,
        log_level="info"
    )