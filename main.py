import asyncio
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from services import VehiculoIOTService

app = FastAPI(title="Vehículo IoT API", version="1.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, vehicle_id: int, websocket: WebSocket):
        await websocket.accept()
        if vehicle_id not in self.active_connections:
            self.active_connections[vehicle_id] = []
        self.active_connections[vehicle_id].append(websocket)

    def disconnect(self, vehicle_id: int, websocket: WebSocket):
        if vehicle_id in self.active_connections:
            if websocket in self.active_connections[vehicle_id]:
                self.active_connections[vehicle_id].remove(websocket)
            if not self.active_connections[vehicle_id]:
                del self.active_connections[vehicle_id]

    async def broadcast_to_vehicle(self, vehicle_id: int, message: dict):
        if vehicle_id in self.active_connections:
            for connection in list(self.active_connections[vehicle_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(vehicle_id, connection)

manager = ConnectionManager()

# --- MODELOS PYDANTIC ---
class MovimientoIndividualRequest(BaseModel):
    id_comando: int
    origen: str = "MANUAL"

class DemoEjecucionRequest(BaseModel):
    id_demo: int

class VehiculoCreateRequest(BaseModel):
    nombre: str
    modelo: str
    descripcion: str
    microcontrolador: str

class VehiculoUpdateRequest(BaseModel):
    nombre: str
    modelo: str
    descripcion: str
    microcontrolador: str
    activo: bool

class ComandoCreateRequest(BaseModel):
    nombre: str
    codigo: int
    descripcion: str

class ComandoUpdateRequest(BaseModel):
    nombre: str
    codigo: int
    descripcion: str
    activo: bool

class EstadoUpdateRequest(BaseModel):
    conectado: bool
    id_comando_actual: Optional[int] = None

class HistorialCreateRequest(BaseModel):
    id_comando: int
    origen: str = "MANUAL"

class DemoCreateRequest(BaseModel):
    nombre: str
    descripcion: str

class DemoUpdateRequest(BaseModel):
    nombre: str
    descripcion: str
    activo: bool

class MovimientoDemoRequest(BaseModel):
    id_comando: int
    orden: int
    duracion_ms: int
    pausa_ms: int = 0


# --- ENDPOINTS: VEHÍCULOS ---
@app.post("/vehiculos")
def crear_vehiculo(data: VehiculoCreateRequest):
    try:
        id_vehiculo = VehiculoIOTService.crear_vehiculo(data.nombre, data.modelo, data.descripcion, data.microcontrolador)
        return {"status": "success", "id_vehiculo": id_vehiculo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos")
def get_vehiculos():
    return VehiculoIOTService.obtener_vehiculos()

@app.get("/vehiculos/{id_vehiculo}")
def get_vehiculo_by_id(id_vehiculo: int):
    vehiculo = VehiculoIOTService.obtener_vehiculo(id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@app.put("/vehiculos/{id_vehiculo}")
def actualizar_vehiculo(id_vehiculo: int, data: VehiculoUpdateRequest):
    try:
        VehiculoIOTService.actualizar_vehiculo(id_vehiculo, data.nombre, data.modelo, data.descripcion, data.microcontrolador, data.activo)
        return {"status": "success", "message": "Vehículo actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vehiculos/{id_vehiculo}")
def eliminar_vehiculo(id_vehiculo: int):
    try:
        VehiculoIOTService.eliminar_vehiculo(id_vehiculo)
        return {"status": "success", "message": "Vehículo eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ENDPOINTS: COMANDOS ---
@app.post("/vehiculos/{id_vehiculo}/comandos")
def crear_comando(id_vehiculo: int, data: ComandoCreateRequest):
    try:
        id_comando = VehiculoIOTService.crear_comando(id_vehiculo, data.nombre, data.codigo, data.descripcion)
        return {"status": "success", "id_comando": id_comando}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{id_vehiculo}/comandos")
def get_comandos(id_vehiculo: int):
    comandos = VehiculoIOTService.obtener_comandos_vehiculo(id_vehiculo)
    return {"vehiculo_id": id_vehiculo, "comandos": comandos}

@app.put("/comandos/{id_comando}")
def actualizar_comando(id_comando: int, data: ComandoUpdateRequest):
    try:
        VehiculoIOTService.actualizar_comando(id_comando, data.nombre, data.codigo, data.descripcion, data.activo)
        return {"status": "success", "message": "Comando actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/comandos/{id_comando}")
def eliminar_comando(id_comando: int):
    try:
        VehiculoIOTService.eliminar_comando(id_comando)
        return {"status": "success", "message": "Comando eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ENDPOINTS: ESTADO E HISTORIAL ---
@app.get("/vehiculos/{id_vehiculo}/estado")
def get_estado(id_vehiculo: int):
    estado = VehiculoIOTService.obtener_estado(id_vehiculo)
    if not estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return {"vehiculo_id": id_vehiculo, "estado": estado}

@app.put("/vehiculos/{id_vehiculo}/estado")
def actualizar_estado_vehiculo(id_vehiculo: int, data: EstadoUpdateRequest):
    try:
        VehiculoIOTService.actualizar_estado(id_vehiculo, data.id_comando_actual, data.conectado)
        return {"status": "success", "message": "Estado actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{id_vehiculo}/historial")
def get_historial(id_vehiculo: int):
    historial = VehiculoIOTService.obtener_historial(id_vehiculo)
    return {"vehiculo_id": id_vehiculo, "total_registros": len(historial), "historial": historial}

@app.post("/vehiculos/{id_vehiculo}/historial")
def registrar_historial(id_vehiculo: int, data: HistorialCreateRequest):
    try:
        VehiculoIOTService.registrar_historial(id_vehiculo, data.id_comando, data.origen)
        return {"status": "success", "message": "Historial registrado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ENDPOINTS: DEMOS Y MOVIMIENTOS ---
@app.post("/vehiculos/{id_vehiculo}/demos")
def crear_demo(id_vehiculo: int, data: DemoCreateRequest):
    try:
        id_demo = VehiculoIOTService.crear_demo(id_vehiculo, data.nombre, data.descripcion)
        return {"status": "success", "id_demo": id_demo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{id_vehiculo}/demos")
def obtener_demos(id_vehiculo: int):
    demos = VehiculoIOTService.obtener_demos(id_vehiculo)
    return {"vehiculo_id": id_vehiculo, "demos": demos}

@app.put("/demos/{id_demo}")
def actualizar_demo(id_demo: int, data: DemoUpdateRequest):
    try:
        VehiculoIOTService.actualizar_demo(id_demo, data.nombre, data.descripcion, data.activo)
        return {"status": "success", "message": "Demo actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/demos/{id_demo}")
def eliminar_demo(id_demo: int):
    try:
        VehiculoIOTService.eliminar_demo(id_demo)
        return {"status": "success", "message": "Demo eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/demos/{id_demo}/movimientos")
def agregar_movimiento_demo(id_demo: int, data: MovimientoDemoRequest):
    try:
        VehiculoIOTService.agregar_movimiento_demo(id_demo, data.id_comando, data.orden, data.duracion_ms, data.pausa_ms)
        return {"status": "success", "message": "Movimiento agregado a la demo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demos/{id_demo}/movimientos")
def get_movimientos_demo(id_demo: int):
    movs = VehiculoIOTService.obtener_movimientos_demo(id_demo)
    return {"id_demo": id_demo, "movimientos": movs}

@app.put("/demo-movimientos/{id_movimiento}")
def actualizar_movimiento_demo(id_movimiento: int, data: MovimientoDemoRequest):
    try:
        VehiculoIOTService.actualizar_movimiento_demo(id_movimiento, data.id_comando, data.orden, data.duracion_ms, data.pausa_ms)
        return {"status": "success", "message": "Movimiento de demo actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/demo-movimientos/{id_movimiento}")
def eliminar_movimiento_demo(id_movimiento: int):
    try:
        VehiculoIOTService.eliminar_movimiento_demo(id_movimiento)
        return {"status": "success", "message": "Movimiento de demo eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- CONTROLADOR DE ACCIÓN Y WEBSOCKETS ---
@app.post("/vehiculos/{id_vehiculo}/mover")
async def ejecutar_movimiento_individual(id_vehiculo: int, data: MovimientoIndividualRequest):
    vehiculo = VehiculoIOTService.obtener_vehiculo(id_vehiculo)
    if not vehiculo or not vehiculo.get("activo"):
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o inactivo")

    comandos = VehiculoIOTService.obtener_comandos_vehiculo(id_vehiculo)
    comando_valido = next((c for c in comandos if c["id_comando"] == data.id_comando and c["activo"]), None)
    
    if not comando_valido:
        raise HTTPException(status_code=400, detail="El comando no existe o no pertenece a este vehículo")

    try:
        VehiculoIOTService.actualizar_estado(id_vehiculo=id_vehiculo, id_comando=data.id_comando, conectado=True)
        VehiculoIOTService.registrar_historial(id_vehiculo=id_vehiculo, id_comando=data.id_comando, origen=data.origen)

        evento_ws = {
            "evento": "movimiento_individual",
            "id_vehiculo": id_vehiculo,
            "comando": comando_valido["nombre"],
            "codigo": comando_valido["codigo"],
            "origen": data.origen
        }
        
        try:
            await manager.broadcast_to_vehicle(id_vehiculo, evento_ws)
        except Exception:
            pass

        return {"status": "success", "message": "Movimiento individual ejecutado y guardado en historial."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vehiculos/{id_vehiculo}/ejecutar-demo")
async def ejecutar_demo(id_vehiculo: int, data: DemoEjecucionRequest):
    movimientos = VehiculoIOTService.obtener_movimientos_demo(data.id_demo)
    if not movimientos:
        raise HTTPException(status_code=404, detail="La demo no existe o no tiene movimientos.")

    asyncio.create_task(reproducir_demo_ws(id_vehiculo, data.id_demo, movimientos))
    return {"status": "success", "message": f"Demo {data.id_demo} iniciada por WebSocket (sin afectar historial)."}

async def reproducir_demo_ws(id_vehiculo: int, id_demo: int, movimientos: list):
    try:
        await manager.broadcast_to_vehicle(id_vehiculo, {
            "evento": "inicio_demo",
            "id_vehiculo": id_vehiculo,
            "id_demo": id_demo
        })

        for mov in movimientos:
            VehiculoIOTService.actualizar_estado(id_vehiculo=id_vehiculo, id_comando=mov["id_comando"], conectado=True)

            await manager.broadcast_to_vehicle(id_vehiculo, {
                "evento": "paso_demo",
                "id_vehiculo": id_vehiculo,
                "orden": mov["orden"],
                "comando": mov["comando"],
                "codigo": mov["codigo"],
                "duracion_ms": mov["duracion_ms"],
                "pausa_ms": mov["pausa_ms"]
            })

            await asyncio.sleep(mov["duracion_ms"] / 1000.0)
            if mov["pausa_ms"] > 0:
                await asyncio.sleep(mov["pausa_ms"] / 1000.0)

        await manager.broadcast_to_vehicle(id_vehiculo, {
            "evento": "fin_demo",
            "id_vehiculo": id_vehiculo,
            "id_demo": id_demo
        })
    except Exception as e:
        print(f"Error reproduciendo demo por WebSocket: {e}")

@app.websocket("/ws/vehiculos/{id_vehiculo}")
async def websocket_endpoint(websocket: WebSocket, id_vehiculo: int):
    await manager.connect(id_vehiculo, websocket)
    try:
        estado_actual = VehiculoIOTService.obtener_estado(id_vehiculo)
        await websocket.send_json({"evento": "estado_inicial", "estado": estado_actual})

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(id_vehiculo, websocket)
    except Exception:
        manager.disconnect(id_vehiculo, websocket)

@app.get("/")
def read_root():
    return {"message": "API de Retroexcavadora IoT activa y conectada a AWS RDS"}