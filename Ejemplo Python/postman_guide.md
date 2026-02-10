# Guía de Pruebas con Postman (OpenTelemetry)

Esta guía permite enviar señales de telemetría (Traces, Metrics, Logs) manualmente al OpenTelemetry Collector usando Postman.

> [!NOTE]
> **¿Quién genera estos JSONs normalmente?**
> En una aplicación real, **no se escriben estos JSONs manualmente**.
> Son generados automáticamente por el **SDK de OpenTelemetry** (la librería que se instala en el código, como `opentelemetry-sdk` en Python).
> 
> El SDK toma las llamadas de alto nivel (como `tracer.start_span("mi_operacion")`) y las transforma en estos paquetes JSON (para HTTP) o Protobuf binario (para gRPC) antes de enviarlos al Collector.
> Esta guía usa los formatos "crudos" solo para fines de prueba y depuración.

## Pre-requisitos
1. **OpenTelemetry Collector** en ejecución.
   - Puerto HTTP habilitado: `4318`
   - Puerto gRPC habilitado: `4317`
2. **Postman** instalado.

---

## 1. Protocolo HTTP (REST)
**URL Base:** `http://localhost:4318`

### A. Enviar Trace (Trazabilidad)
*   **Método:** `POST`
*   **URL:** `http://localhost:4318/v1/traces`
*   **Body (JSON):**
    ```json
    {
      "resourceSpans": [
        {
          "resource": {
            "attributes": [
              { "key": "service.name", "value": { "stringValue": "prueba-postman-http" } }
            ]
          },
          "scopeSpans": [
            {
              "scope": { "name": "manual-test" },
              "spans": [
                {
                  "traceId": "5b8aa5a2d2c872e8321cf37308d69df2",
                  "spanId": "051581bf3cb55c13",
                  "name": "Prueba HTTP Manual",
                  "kind": 1,
                  "startTimeUnixNano": "1698700000000000000",
                  "endTimeUnixNano": "1698700001000000000",
                  "attributes": [
                    { "key": "http.method", "value": { "stringValue": "POST" } }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    ```

### B. Enviar Metric (Métricas)
*   **Método:** `POST`
*   **URL:** `http://localhost:4318/v1/metrics`
*   **Body (JSON):**
    ```json
    {
      "resourceMetrics": [
        {
          "resource": {
            "attributes": [
              { "key": "service.name", "value": { "stringValue": "prueba-postman-http" } }
            ]
          },
          "scopeMetrics": [
            {
              "scope": { "name": "manual-test" },
              "metrics": [
                {
                  "name": "contador_http_manual",
                  "description": "Contador de prueba HTTP",
                  "unit": "1",
                  "sum": {
                    "aggregationTemporality": 2,
                    "isMonotonic": true,
                    "dataPoints": [
                      {
                        "asInt": 1,
                        "timeUnixNano": "1698700000000000000",
                        "attributes": [
                          { "key": "env", "value": { "stringValue": "dev" } }
                        ]
                      }
                    ]
                  }
                }
              ]
            }
          ]
        }
      ]
    }
    ```

### C. Enviar Log (Registro)
*   **Método:** `POST`
*   **URL:** `http://localhost:4318/v1/logs`
*   **Body (JSON):**
    ```json
    {
      "resourceLogs": [
        {
          "resource": {
            "attributes": [
              { "key": "service.name", "value": { "stringValue": "prueba-postman-http" } }
            ]
          },
          "scopeLogs": [
            {
              "scope": { "name": "manual-test" },
              "logRecords": [
                {
                  "timeUnixNano": "1698700000000000000",
                  "severityText": "INFO",
                  "body": { "stringValue": "Hola desde Postman HTTP!" },
                  "attributes": [
                    { "key": "source", "value": { "stringValue": "postman" } }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    ```

---

## 2. Protocolo gRPC
Postman soporta gRPC nativamente. Se debe crear un nuevo request y seleccionar "gRPC" en lugar de "HTTP".

**URL:** `localhost:4317` (sin http://)

### Configuración en Postman
> [!TIP]
> **Se han descargado los archivos .proto necesarios.**
> Se encuentran en la carpeta `Ejemplo Python/postman_protos`.

1.  **Nuevo Request:** Seleccione "gRPC Request".
2.  **Server URL:** `localhost:4317`
3.  **Service Definition (Protobuf):**
    *   Seleccione **"Import a .proto file"**.
    *   Navegue a la carpeta `Ejemplo Python/postman_protos/opentelemetry/proto/collector/logs/v1/`.
    *   Seleccione el archivo **`logs_service.proto`**.
    *   **Importante:** Si Postman solicita "Import Paths" o indica que faltan dependencias, agregue la carpeta raíz `Ejemplo Python/postman_protos` como un `valid import path`.
4.  **Método:** Una vez cargado, seleccione:
    *   `opentelemetry.proto.collector.logs.v1.LogsService/Export`

**(Repita los pasos para Traces y Metrics usando `trace_service.proto` y `metrics_service.proto` respectivamente).**

### Ejemplos de Payload (JSON)

#### 1. Logs (gRPC)
**Método:** `opentelemetry.proto.collector.logs.v1.LogsService/Export`

```json
{
  "resource_logs": [
    {
      "resource": {
        "attributes": [
          { "key": "service.name", "value": { "string_value": "prueba-postman-grpc" } }
        ]
      },
      "scope_logs": [
        {
          "scope": { "name": "manual-test-grpc" },
          "logRecords": [
            {
              "time_unix_nano": "1770747600000000000",
              "severity_text": "INFO",
              "body": { "string_value": "Hola desde Postman gRPC!" },
              "attributes": [
                { "key": "source", "value": { "string_value": "postman-grpc" } }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

#### 2. Traces (gRPC)
**Método:** `opentelemetry.proto.collector.trace.v1.TraceService/Export`

> [!IMPORTANT]
> En gRPC, `trace_id` y `span_id` deben enviarse en **Base64**.
> - `trace_id`: 32 caracteres hex -> Base64
> - `span_id`: 16 caracteres hex -> Base64

```json
{
  "resource_spans": [
    {
      "resource": {
        "attributes": [
          { "key": "service.name", "value": { "string_value": "prueba-postman-grpc" } }
        ]
      },
      "scope_spans": [
        {
          "scope": { "name": "manual-test-grpc" },
          "spans": [
            {
              "trace_id": "EjRWeJASNFZ4kBI0VniQEg==", 
              "span_id": "EjRWeJASNFY=",
              "name": "Prueba Trace gRPC",
              "kind": 2,
              "start_time_unix_nano": "1770747600000000000",
              "end_time_unix_nano": "1770747601000000000",
              "attributes": [
                { "key": "http.method", "value": { "string_value": "POST" } }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

#### 3. Metrics (gRPC)
**Método:** `opentelemetry.proto.collector.metrics.v1.MetricsService/Export`

```json
{
  "resource_metrics": [
    {
      "resource": {
        "attributes": [
          { "key": "service.name", "value": { "string_value": "prueba-postman-grpc" } }
        ]
      },
      "scope_metrics": [
        {
          "scope": { "name": "manual-test-grpc" },
          "metrics": [
            {
              "name": "contador_grpc_manual",
              "description": "Contador de prueba gRPC",
              "unit": "1",
              "sum": {
                "aggregation_temporality": 2, 
                "is_monotonic": true,
                "data_points": [
                  {
                    "as_int": 5,
                    "time_unix_nano": "1770747600000000000",
                    "attributes": [
                      { "key": "env", "value": { "string_value": "dev" } }
                    ]
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```
*Nota: En gRPC, los nombres de campos usan snake_case (`resource_logs`, `time_unix_nano`) en lugar de camelCase (`resourceLogs`), y los valores primitivos a veces requieren envoltorios como `string_value` o `int_value` dependiendo de la definición exacta del proto.*