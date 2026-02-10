# POC Monitoreo Docker

Este repositorio contiene una Prueba de Concepto (POC) para una pila de monitoreo completa basada en Docker, junto con un ejemplo de aplicación en Python instrumentada con OpenTelemetry.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

*   **`docker-compose.yaml`**: Archivo principal que define y orquesta todos los servicios de monitoreo (Grafana, Tempo, VictoriaMetrics, ClickHouse, OpenTelemetry Collector).
*   **`Monitoreo/`**: Contiene los archivos de configuración necesarios para los servicios de Docker.
*   **`Ejemplo Python/`**: Contiene el código fuente de una aplicación Python de ejemplo que genera trazas y métricas para ser recolectadas por la pila de monitoreo.

## Prerrequisitos

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y ejecutándose.
*   [Python 3.9+](https://www.python.org/downloads/) (para ejecutar el ejemplo de Python localmente).

## Instrucciones de Ejecución

### 1. Iniciar la Pila de Monitoreo

Para levantar todos los servicios de monitoreo, se debe ejecutar el siguiente comando en la raíz del proyecto (donde está el `docker-compose.yaml`):

```bash
docker-compose up -d
```

Esto iniciará los siguientes servicios:
*   **Grafana**: http://localhost:3000 (Usuario: `admin`, Contraseña: no requerida / acceso anónimo habilitado).
*   **VictoriaMetrics**: http://localhost:8428 (Almacenamiento de métricas).
*   **Tempo**: Puerto 3200 (Almacenamiento de trazas).
*   **ClickHouse**: Puertos 8123/9000 (Almacenamiento de logs).
*   **OpenTelemetry Collector**: Puertos 4317 (gRPC) y 4318 (HTTP).

### 2. Ejecutar el Ejemplo de Python

Para generar datos de prueba, seguir estos pasos:

1.  Navegar a la carpeta del ejemplo:
    ```bash
    cd "Ejemplo Python"
    ```

2.  Crear un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # En Windows PowerShell
    # source venv/bin/activate  # En Linux/Mac
    ```

3.  Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4.  Ejecutar la aplicación:
    ```bash
    python main.py
    ```

## Visualización en Grafana

1.  Abrir el navegador en http://localhost:3000.
2.  No se necesitan credenciales, el acceso anónimo como Admin está habilitado.
3.  Ir a **Dashboards** para ver los tableros pre-configurados (los cuales se cargaron desde la carpeta `Monitoreo/grafana/dashboards`).
