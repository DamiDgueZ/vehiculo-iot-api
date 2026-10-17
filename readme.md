# Vehículo IoT API - Sistema de Control y Monitoreo (Examen Tema 2.6)

API pública desarrollada en **Python con FastAPI y Programación Orientada a Objetos (POO)**, conectada a una base de datos relacional en **Amazon RDS for MySQL** y desplegada de forma persistente en **Amazon EC2**. La aplicación integra de manera funcional los **21 Procedimientos Almacenados (Stored Procedures)** del esquema `vehiculo_iot`, servicios HTTP estandarizados (`GET`, `POST`, `PUT`, `DELETE`), documentación interactiva en **Swagger UI** y comunicación bidireccional en tiempo real mediante **WebSockets seguros (WSS)**.

---

## 🏗️ 1. Arquitectura de la Solución (Escenario Público)

```
[ Cliente Externo / Thunder Client / Swagger UI ] 
        ↕ (HTTPS / WSS)
[ Aplicación FastAPI (Servidor en Amazon EC2) ] 
        ↕ (TCP / 3306)
[ Amazon RDS for MySQL (Esquema vehiculo_iot - 21 Stored Procedures) ]
```

---

## 📂 2. Organización Modular y POO

El sistema está estructurado bajo principios de separación de responsabilidades:
* **`main.py`**: Inicializa la aplicación FastAPI, define los modelos Pydantic para validación de entradas, agrupa las rutas HTTP por bloques lógicos y gestiona el ciclo de vida de los clientes WebSocket concurrentes mediante la clase `ConnectionManager`.
* **`services.py`**: Contiene la clase estática `VehiculoIOTService`, encargada de encapsular la lógica de acceso a datos e invocar de manera segura los 21 procedimientos almacenados en Amazon RDS.
* **`database.py`**: Configura el pool de conexiones seguras hacia la base de datos relacional utilizando variables de entorno protegidas.

---

## 🔗 3. Mapeo de Endpoints y Procedimientos Almacenados (21 SP)

La API organiza sus operaciones funcionales en bloques temáticos, relacionando directamente cada ruta con su respectivo Stored Procedure en MySQL:

### Grupo A: Vehículos (5 Operaciones)
1. **Crear Vehículo** (`POST /vehiculos`) -> Invoca `sp_crear_vehiculo` (Parámetros: `nombre`, `modelo`, `descripcion`, `microcontrolador`).
2. **Obtener Todos los Vehículos** (`GET /vehiculos`) -> Invoca `sp_obtener_vehiculos`.
3. **Obtener Vehículo por ID** (`GET /vehiculos/{id_vehiculo}`) -> Invoca `sp_obtener_vehiculo` (Parámetro: `id_vehiculo`).
4. **Actualizar Vehículo** (`PUT /vehiculos/{id_vehiculo}`) -> Invoca `sp_actualizar_vehiculo` (Parámetros: `id_vehiculo`, `nombre`, `modelo`, `descripcion`, `microcontrolador`, `activo`).
5. **Eliminar Vehículo** (`DELETE /vehiculos/{id_vehiculo}`) -> Invoca `sp_eliminar_vehiculo` (Parámetro: `id_vehiculo`).

### Grupo B: Comandos (4 Operaciones)
6. **Crear Comando** (`POST /vehiculos/{id_vehiculo}/comandos`) -> Invoca `sp_crear_comando` (Parámetros: `id_vehiculo`, `nombre`, `codigo`, `descripcion`).
7. **Obtener Comandos del Vehículo** (`GET /vehiculos/{id_vehiculo}/comandos`) -> Invoca `sp_obtener_comandos_vehiculo` (Parámetro: `id_vehiculo`).
8. **Actualizar Comando** (`PUT /comandos/{id_comando}`) -> Invoca `sp_actualizar_comando` (Parámetros: `id_comando`, `nombre`, `codigo`, `descripcion`, `activo`).
9. **Eliminar Comando** (`DELETE /comandos/{id_comando}`) -> Invoca `sp_eliminar_comando` (Parámetro: `id_comando`).

### Grupo C: Estado (2 Operaciones)
10. **Actualizar Estado** (`PUT /vehiculos/{id_vehiculo}/estado`) -> Invoca `sp_actualizar_estado` (Parámetros: `id_vehiculo`, `id_comando`, `conectado`).
11. **Obtener Estado** (`GET /vehiculos/{id_vehiculo}/estado`) -> Invoca `sp_obtener_estado` (Parámetro: `id_vehiculo`).

### Grupo D: Historial (2 Operaciones)
12. **Registrar Historial** (`POST /vehiculos/{id_vehiculo}/historial`) -> Invoca `sp_registrar_historial` (Parámetros: `id_vehiculo`, `id_comando`, `origen`).
13. **Obtener Historial** (`GET /vehiculos/{id_vehiculo}/historial`) -> Invoca `sp_obtener_historial` (Devuelve máximo 10 registros recientes ordenados de forma descendente).

### Grupo E: Demos (4 Operaciones)
14. **Crear Demo** (`POST /vehiculos/{id_vehiculo}/demos`) -> Invoca `sp_crear_demo` (Parámetros: `id_vehiculo`, `nombre`, `descripcion`).
15. **Obtener Demos** (`GET /vehiculos/{id_vehiculo}/demos`) -> Invoca `sp_obtener_demos` (Parámetro: `id_vehiculo`).
16. **Actualizar Demo** (`PUT /demos/{id_demo}`) -> Invoca `sp_actualizar_demo` (Parámetros: `id_demo`, `nombre`, `descripcion`, `activo`).
17. **Eliminar Demo** (`DELETE /demos/{id_demo}`) -> Invoca `sp_eliminar_demo` (Parámetro: `id_demo`).

### Grupo F: Movimientos Demo (4 Operaciones)
18. **Agregar Movimiento a Demo** (`POST /demos/{id_demo}/movimientos`) -> Invoca `sp_agregar_movimiento_demo` (Parámetros: `id_demo`, `id_comando`, `orden`, `duracion_ms`, `pausa_ms`).
19. **Obtener Movimientos de Demo** (`GET /demos/{id_demo}/movimientos`) -> Invoca `sp_obtener_movimientos_demo` (Parámetro: `id_demo`).
20. **Actualizar Movimiento de Demo** (`PUT /demo-movimientos/{id_movimiento}`) -> Invoca `sp_actualizar_movimiento_demo` (Parámetros: `id_movimiento`, `id_comando`, `orden`, `duracion_ms`, `pausa_ms`).
21. **Eliminar Movimiento de Demo** (`DELETE /demo-movimientos/{id_movimiento}`) -> Invoca `sp_eliminar_movimiento_demo` (Parámetro: `id_movimiento`).

---

## ⚡ 4. Documentación del Canal WebSocket (WSS) y Eventos JSON

El canal de comunicación en tiempo real permite el monitoreo simultáneo de múltiples clientes por cada vehículo conectado.

* **URL de Conexión Pública:**  
  `ws://100.60.28.1/:8000/ws/vehiculos/{id_vehiculo}`

### Eventos y Mensajes JSON Transmitidos:

1. **Evento de Estado Inicial (Al establecer conexión WSS):**
   Entrega inmediata del último estado persistido en Amazon RDS.
   ```json
   {
     "evento": "estado_inicial",
     "estado": [
       {
         "id_vehiculo": 1,
         "vehiculo": "Excavadora IoT",
         "id_comando": 9,
         "comando": "DETENER",
         "codigo": 9,
         "conectado": true,
         "fecha_actualizacion": "2026-10-17T12:00:00"
       }
     ]
   }
   ```

2. **Evento de Movimiento Individual (Tras un POST en `/mover`):**
   Notifica a todos los clientes WSS conectados al vehículo y registra el evento en el historial.
   ```json
   {
     "evento": "movimiento_individual",
     "id_vehiculo": 1,
     "comando": "AVANZAR",
     "codigo": 1,
     "origen": "MANUAL"
   }
   ```

3. **Secuencia DEMO en Tiempo Real (Inicio, Pasos y Finalización):**
   Transmitido al invocar el POST `/ejecutar-demo`. Ejecuta los $N$ pasos temporizados sin alterar la tabla de historial.
   * **Inicio:**
     ```json
     {
       "evento": "inicio_demo",
       "id_vehiculo": 1,
       "id_demo": 1
     }
     ```
   * **Paso Individual ($N$ veces):**
     ```json
     {
       "evento": "paso_demo",
       "id_vehiculo": 1,
       "orden": 1,
       "comando": "AVANZAR",
       "codigo": 1,
       "duracion_ms": 2000,
       "pausa_ms": 400
     }
     ```
   * **Finalización:**
     ```json
     {
       "evento": "fin_demo",
       "id_vehiculo": 1,
       "id_demo": 1
     }
     ```

4. **Gestión de Cancelación y Errores:**
   * **Cancelación de Demo / Emergencia:**
     ```json
     {
       "evento": "cancelar_demo",
       "id_vehiculo": 1,
       "mensaje": "Secuencia detenida por solicitud del operador."
     }
     ```
   * **Manejo de Errores de Conexión o Datos:**
     ```json
     {
       "evento": "error",
       "id_vehiculo": 1,
       "detalle": "Fallo en la comunicación con Amazon RDS o comando inválido."
     }
     ```

---

## 🚀 5. Instrucciones de Ejecución y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd vehiculo_iot_api
   ```
2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
3. **Instalar dependencias:**
   ```bash
   pip install fastapi uvicorn pymysql python-dotenv pydantic websockets "uvicorn[standard]"
   ```
4. **Configurar variables de entorno (`.env`):**
   Crear un archivo `.env` en la raíz (excluido en `.gitignore`):
   ```env
   DB_HOST=tu-endpoint-de-rds.amazonaws.com
   DB_PORT=3306
   DB_USER=admin
   DB_PASSWORD=tu_contraseña_real
   DB_NAME=vehiculo_iot
   ```
5. **Ejecutar el servidor en producción/AWS (EC2):**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## 🌐 Enlaces Verificables para Evaluación
* **Documentación Interactiva (Swagger UI):** `http://100.60.28.1:8000/docs`