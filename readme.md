# Vehículo IoT API - Sistema de Control y Monitoreo (Examen 2.6)

API pública desarrollada con **Python, FastAPI y Programación Orientada a Objetos (POO)**, conectada a una base de datos relacional en **Amazon RDS for MySQL** y desplegada en **Amazon EC2**. Integra los 21 Procedimientos Almacenados (Stored Procedures) del esquema `vehiculo_iot`, servicios HTTP (GET/POST) y monitoreo en tiempo real mediante **WebSockets seguros (WSS)**.

---

## 🏗️ Arquitectura de la Solución
```text
[ Cliente / Thunder Client / Swagger UI ] 
        ↕ (HTTPS / WSS)
[ Aplicación FastAPI en Amazon EC2 ] 
        ↕ (TCP 3306)
[ Amazon RDS for MySQL (Esquema vehiculo_iot - 21 Stored Procedures) ]
```

---

## 📂 Organización Modular (POO)
El proyecto está estructurado bajo principios de responsabilidad única y encapsulamiento:
* `main.py`: Inicializa la aplicación FastAPI, define las rutas HTTP (agrupadas por etiquetas), administra los modelos Pydantic y gestiona el ciclo de vida de los WebSockets concurrentes mediante la clase `ConnectionManager`.
* `database.py`: Maneja la configuración y el pool de conexiones seguras hacia Amazon RDS utilizando variables de entorno.
* `services.py`: Contiene la clase estática `VehiculoIOTService`, encargada de aislar la lógica de negocio y ejecutar directamente los 21 Stored Procedures.

---

## 🚀 Instrucciones de Ejecución Local y Remota

### 1. Clonar el repositorio e instalar dependencias
```bash
git clone <url-del-repositorio>
cd vehiculo_iot_api
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate
pip install fastapi uvicorn pymysql python-dotenv pydantic websockets "uvicorn[standard]"
```

### 2. Configurar las variables de entorno (`.env`)
Crea un archivo llamado `.env` en la raíz del proyecto con las credenciales de tu base de datos en Amazon RDS (este archivo se encuentra excluido en `.gitignore` por seguridad):
```env
DB_HOST=tu-endpoint-de-rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=tu_contraseña_real
DB_NAME=vehiculo_iot
```

### 3. Ejecutar el servidor
* **Localmente:**
  ```bash
  uvicorn main:app --reload
  ```
* **En Amazon EC2 (Acceso Público):**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```

---

## 🔌 Documentación del Canal WebSocket (WSS)

El servicio de WebSockets permite el monitoreo y control en tiempo real por cada vehículo registrado.

* **URL de Conexión:** 
  `ws://100.60.28.1/:8000/ws/vehiculos/{id_vehiculo}`

### Eventos JSON transmitidos por el WebSocket:
1. **Estado Inicial (Al conectar):**
   ```json
   {
     "evento": "estado_inicial",
     "estado": {
       "id_vehiculo": 1,
       "vehiculo": "Excavadora IoT",
       "conectado": true,
       "id_comando_actual": 1
     }
   }
   ```
2. **Movimiento Individual (POST /mover):**
   ```json
   {
     "evento": "movimiento_individual",
     "id_vehiculo": 1,
     "comando": "AVANZAR",
     "codigo": 1,
     "origen": "MANUAL"
   }
   ```
3. **Secuencia DEMO (Inicio, Pasos y Fin):**
   * Inicio: `{"evento": "inicio_demo", "id_vehiculo": 1, "id_demo": 1}`
   * Paso: `{"evento": "paso_demo", "id_vehiculo": 1, "orden": 1, "comando": "AVANZAR", "duracion_ms": 2000, "pausa_ms": 400}`
   * Fin: `{"evento": "fin_demo", "id_vehiculo": 1, "id_demo": 1}`

---

## 📋 Enlaces y Evidencias
* **Swagger UI (Documentación Interactiva):** `http://100.60.28.1/:8000/docs`