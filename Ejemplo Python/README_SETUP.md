# Guía de Configuración del Entorno de Python

Sigue estos pasos para preparar el entorno y ejecutar la demo de observabilidad.

## 1. Crear el Entorno Virtual (venv)
Abre una terminal (PowerShell o CMD) en la carpeta `Ejemplo Python` y ejecuta:

```powershell
# Crear el entorno llamado 'venv'
python -m venv venv
```

## 2. Activar el Entorno
Dependiendo de qué terminal uses:

### En PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

### En CMD (Símbolo del sistema):
```cmd
.\venv\Scripts\activate.bat
```

## 3. Instalar Dependencias
Una vez activado (verás un `(venv)` al inicio de tu línea de comandos), instala las librerías necesarias:

```powershell
pip install -r requirements.txt
```

---

## 4. Ejecutar la Demo de la API
Para iniciar el servidor de la demo:

```powershell
python api_demo.py
```

El servidor quedará escuchando en `http://localhost:8000`.

## 5. Probar y capturar Evidencia
En **otra terminal** (mientras el servidor corre), ejecuta el comando `curl` para generar telemetría:

```bash
curl -X POST http://localhost:8000/comprar \
     -H "Content-Type: application/json" \
     -d "{\"producto\": \"Laptop Pro\", \"precio\": 1500, \"usuario\": \"jefe_demo\"}"
```

### Qué observar:
1.  **En la terminal de la API**: Verás el JSON que se envía a OpenTelemetry (Request) y la confirmación del éxito (Response: SUCCESS).
2.  **En el Dashboard de Grafana**: Verás los puntos de métrica, el log de la compra y el trace de la transacción.
