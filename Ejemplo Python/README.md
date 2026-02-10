# Documentación de Observabilidad OpenTelemetry

Este proyecto demuestra cómo instrumentar una aplicación Python para enviar **Logs**, **Métricas** y **Trazas (Traces)** a un colector de OpenTelemetry (OTEL Collector) utilizando el protocolo OTLP sobre gRPC.

## ¿Cómo funciona el envío de telemetría?

El flujo de datos es el siguiente:

1.  **Instrumentación**: La aplicación genera datos de telemetría.
    *   **Traces**: Se generan automáticamente mediante el decorador `@instrument` (en `decorator.py`) que envuelve las funciones.
    *   **Métricas**: Se registran explícitamente (contadores, histogramas) definidos en `metrics.py`.
    *   **Logs**: Se interceptan los logs estándar de Python (`logging`) y se redirigen al exportador de OTEL.

2.  **Exportación (OTLP gRPC)**:
    *   El módulo `observability/observability.py` configura los "Provisores" (Providers) y "Exportadores" (Exporters) para cada señal (Log, Trace, Metric).
    *   Se utiliza el protocolo **Native OTLP** sobre **gRPC** para el envío eficiente de datos.

3.  **Seguridad y Conexión**:
    *   **TLS/SSL**: La conexión es segura. Se utiliza un certificado CA personalizado (`otel-test-ca.pem` o `otel-prod-ca.pem`) para validar el servidor del Collector.
    *   **Autenticación**: Se envía un **Bearer Token** en los headers de cada petición gRPC (`Authorization: Bearer <TOKEN>`).

## Configuración (.env)

El archivo `.env` controla los parámetros de conexión:

| Variable | Descripción |
| :--- | :--- |
| `SERVICE_NAME` | Identificador del servicio en las herramientas de monitoreo (ej. Grafana/Tempo). |
| `OTEL_COLLECTOR_ENDPOINT` | Dirección IP y Puerto del Collector (ej. `173.249.27.8:31317`). |
| `OTEL_BEARER_TOKEN` | Token de autenticación requerido por el Collector. |
| `APP_ENV` | Entorno (`development` o `production`), define qué certificado CA usar. |

## Estructura del Código de Observabilidad

*   **`observability/observability.py`**:
    *   Es el "corazón" de la configuración.
    *   Inicializa los `TracerProvider`, `MeterProvider` y `LoggerProvider`.
    *   Configura los canales seguros gRPC con los certificados SSL.
*   **`observability/decorator.py`**:
    *   Contiene `@instrument`. Úsalo sobre cualquier función para obtener trazas automáticas y medición de tiempo de ejecución.
*   **`observability/metrics.py`**:
    *   Define las métricas específicas de negocio (ej. `demo.requests.total`).
    *   Aquí debes declarar nuevos contadores o histogramas si los necesitas.
