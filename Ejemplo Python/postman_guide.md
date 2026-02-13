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
              { "key": "service.name", "value": { "stringValue": "tienda-virtual-postman" } },
              { "key": "service.version", "value": { "stringValue": "1.2.0" } },
              { "key": "telemetry.sdk.name", "value": { "stringValue": "opentelemetry" } },
              { "key": "telemetry.sdk.language", "value": { "stringValue": "python" } }
            ]
          },
          "scopeSpans": [
            {
              "scope": { "name": "manual-test-ecommerce", "version": "1.0.0" },
              "spans": [
                {
                  "traceId": "5b8aa5a2d2c872e8321cf37308d69df2",
                  "spanId": "051581bf3cb55c13",
                  "parentSpanId": "",
                  "name": "procesar_transaccion",
                  "kind": 1,
                  "startTimeUnixNano": "1698700000000000000",
                  "endTimeUnixNano": "1698700001500000000",
                  "status": {
                    "code": 1
                  },
                  "attributes": [
                    { "key": "http.method", "value": { "stringValue": "POST" } },
                    { "key": "http.scheme", "value": { "stringValue": "https" } },
                    { "key": "http.client_ip", "value": { "stringValue": "192.168.10.45" } },
                    { "key": "user_agent.original", "value": { "stringValue": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)..." } },
                    
                    { "key": "enduser.id", "value": { "stringValue": "a1b2c3d4-e5f6-7890-1234-567890abcdef" } },
                    { "key": "enduser.role", "value": { "stringValue": "Admin" } },
                    { "key": "enduser.email", "value": { "stringValue": "juan.perez@example.com" } },
                    
                    { "key": "device.type", "value": { "stringValue": "Mobile" } },
                    
                    { "key": "ecommerce.cart.total", "value": { "doubleValue": 450.50 } },
                    { "key": "ecommerce.cart.items_count", "value": { "intValue": 3 } }
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
              { "key": "service.name", "value": { "stringValue": "tienda-virtual-postman" } }
            ]
          },
          "scopeMetrics": [
            {
              "scope": { "name": "manual-test-ecommerce" },
              "metrics": [
                {
                  "name": "ecommerce.cart.value",
                  "description": "Valor monetario de los carritos procesados",
                  "unit": "USD",
                  "histogram": {
                    "aggregationTemporality": 2,
                    "dataPoints": [
                      {
                        "count": 1,
                        "sum": 250.0,
                        "bucketCounts": [0, 0, 1, 0],
                        "explicitBounds": [0, 100, 500, 1000],
                        "timeUnixNano": "1698700000000000000",
                        "attributes": [
                          { "key": "device.type", "value": { "stringValue": "Desktop" } }
                        ]
                      }
                    ]
                  }
                },
                {
                  "name": "ecommerce.abonos.total",
                  "description": "Total de ventas realizadas",
                  "unit": "1",
                  "sum": {
                    "aggregationTemporality": 2,
                    "isMonotonic": true,
                    "dataPoints": [
                      {
                        "asInt": 1,
                        "timeUnixNano": "1698700000000000000",
                        "attributes": [
                            { "key": "payment.method", "value": { "stringValue": "paypal" } },
                            { "key": "device.type", "value": { "stringValue": "Mobile" } }
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
              { "key": "service.name", "value": { "stringValue": "tienda-virtual-postman" } }
            ]
          },
          "scopeLogs": [
            {
              "scope": { "name": "manual-test-ecommerce" },
              "logRecords": [
                {
                  "timeUnixNano": "1698700000000000000",
                  "severityText": "INFO",
                  "severityNumber": 9,
                  "traceId": "5b8aa5a2d2c872e8321cf37308d69df2",
                  "spanId": "051581bf3cb55c13",
                  "body": {
                    "kvlistValue": {
                      "values": [
                        { "key": "nombre", "value": { "stringValue": "Juan Perez" } },
                        { "key": "email", "value": { "stringValue": "juan.perez@example.com" } },
                        { "key": "telefono", "value": { "stringValue": "+5512345678" } },
                        { 
                          "key": "direccion", 
                          "value": { 
                            "kvlistValue": {
                              "values": [
                                { "key": "calle", "value": { "stringValue": "Av. Reforma 123" } },
                                { "key": "ciudad", "value": { "stringValue": "CDMX" } },
                                { "key": "cp", "value": { "stringValue": "06500" } }
                              ]
                            }
                          }
                        }
                      ]
                    }
                  },
                  "attributes": [
                    { "key": "enduser.id", "value": { "stringValue": "a1b2c3d4-e5f6-7890-1234-567890abcdef" } },
                    { "key": "ecommerce.total", "value": { "doubleValue": 450.50 } },
                    { 
                        "key": "usuario.json", 
                        "value": { 
                            "stringValue": "{\"id\": \"...\", \"contexto\": {\"ip\": \"192.168.1.1\", \"device\": \"Mobile\"}, \"carrito\": [{\"producto_nombre\": \"Laptop\", \"precio\": 1200}]}" 
                        } 
                    }
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
          { "key": "service.name", "value": { "string_value": "tienda-virtual-postman-grpc" } }
        ]
      },
      "scope_logs": [
        {
          "scope": { "name": "manual-test-ecommerce-grpc" },
          "logRecords": [
            {
              "time_unix_nano": "1770747600000000000",
              "severity_text": "INFO",
              "severity_number": 9,
              "trace_id": "EjRWeJASNFZ4kBI0VniQEg==", 
              "span_id": "EjRWeJASNFY=",
              "body": {
                "kvlist_value": {
                  "values": [
                    { "key": "nombre", "value": { "string_value": "Juan Perez" } },
                    { "key": "email", "value": { "string_value": "juan.perez@example.com" } },
                    { "key": "telefono", "value": { "string_value": "+5512345678" } },
                    { 
                      "key": "direccion", 
                      "value": { 
                        "kvlist_value": {
                          "values": [
                            { "key": "calle", "value": { "string_value": "Av. Reforma 123" } },
                            { "key": "ciudad", "value": { "string_value": "CDMX" } },
                            { "key": "cp", "value": { "string_value": "06500" } }
                          ]
                        }
                      }
                    }
                  ]
                }
              },
              "attributes": [
                { "key": "enduser.id", "value": { "string_value": "a1b2c3d4-e5f6-7890-1234-567890abcdef" } },
                { "key": "ecommerce.total", "value": { "double_value": 450.50 } },
                { 
                    "key": "usuario.json", 
                    "value": { 
                        "string_value": "{\"id\": \"...\", \"contexto\": {\"ip\": \"192.168.1.1\", \"device\": \"Mobile\"}, \"carrito\": [{\"producto_nombre\": \"Laptop\", \"precio\": 1200}]}" 
                    } 
                }
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
          { "key": "service.name", "value": { "string_value": "tienda-virtual-postman-grpc" } },
          { "key": "service.version", "value": { "string_value": "1.2.0" } }
        ]
      },
      "scope_spans": [
        {
          "scope": { "name": "manual-test-ecommerce-grpc", "version": "1.0.0" },
          "spans": [
            {
              "trace_id": "EjRWeJASNFZ4kBI0VniQEg==", 
              "span_id": "EjRWeJASNFY=",
              "parent_span_id": "",
              "name": "procesar_transaccion",
              "kind": 2,
              "start_time_unix_nano": "1770747600000000000",
              "end_time_unix_nano": "1770747601500000000",
              "status": {
                "code": 1
              },
              "attributes": [
                { "key": "http.method", "value": { "string_value": "POST" } },
                { "key": "http.scheme", "value": { "string_value": "https" } },
                { "key": "http.client_ip", "value": { "string_value": "192.168.10.45" } },
                
                { "key": "enduser.id", "value": { "string_value": "a1b2c3d4-e5f6-7890-1234-567890abcdef" } },
                { "key": "enduser.role", "value": { "string_value": "Admin" } },
                
                { "key": "device.type", "value": { "string_value": "Mobile" } },
                
                { "key": "ecommerce.cart.total", "value": { "double_value": 450.50 } },
                { "key": "ecommerce.cart.items_count", "value": { "int_value": 3 } }
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
          { "key": "service.name", "value": { "string_value": "tienda-virtual-postman-grpc" } }
        ]
      },
      "scope_metrics": [
        {
          "scope": { "name": "manual-test-ecommerce-grpc" },
          "metrics": [
             {
              "name": "ecommerce.cart.value",
              "description": "Valor monetario de los carritos procesados",
              "unit": "USD",
              "histogram": {
                "aggregation_temporality": 2,
                "data_points": [
                  {
                    "count": 1,
                    "sum": 250.0,
                    "bucket_counts": [0, 0, 1, 0],
                    "explicit_bounds": [0, 100, 500, 1000],
                    "time_unix_nano": "1770747600000000000",
                    "attributes": [
                      { "key": "device.type", "value": { "string_value": "Desktop" } }
                    ]
                  }
                ]
              }
            },
            {
              "name": "ecommerce.abonos.total",
              "description": "Total de ventas realizadas",
              "unit": "1",
              "sum": {
                "aggregation_temporality": 2, 
                "is_monotonic": true,
                "data_points": [
                  {
                    "as_int": 5,
                    "time_unix_nano": "1770747600000000000",
                    "attributes": [
                      { "key": "payment.method", "value": { "string_value": "paypal" } },
                      { "key": "device.type", "value": { "string_value": "Mobile" } }
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

---

## 3. Desglose del JSON (Anatomía de un Log en OTLP)

A continuación, se explica cada sección del JSON estándar de OpenTelemetry (OTLP/HTTP).

### 1. `resourceLogs` (El "Quién")
Es la capa superior. Define **quién** está enviando los datos.
*   **`resource`**: Representa la entidad (servicio, contenedor, host) que produce la telemetría.
    *   **`attributes`**: Pares clave-valor que identifican al recurso de forma única.
        *   `service.name`: El nombre de tu aplicación (CRÍTICO para encontrar los datos en tu backend).
        *   `service.instance.id`: ID único de la instancia (ej. nombre del pod).

### 2. `scopeLogs` (El "Desde Dónde")
Agrupa los logs por la **librería de instrumentación** que los generó dentro de ese servicio.
*   **`scope`**:
    *   `name`: Nombre del logger o librería (ej. `opentelemetry.sdk`, `my-custom-logger`).
    *   `version`: Versión de la librería.

### 3. `logRecords` (El "Qué")
La lista de eventos de log individuales. Cada objeto aquí es un mensaje de log.
*   **`timeUnixNano`**: Timestamp exacto en nanosegundos (UTC).
*   **`severityText` / `severityNumber`**: Nivel del log (INFO=9, WARN=13, ERROR=17, etc.).
*   **`attributes`**: Metadatos extra asociados a ESTE log específico (ej. `http.request.id`, `enduser.id`). Ideal para filtrar.
*   **`body`**: El contenido principal del mensaje. Puede ser simple (`stringValue`) o estructurado (`kvlistValue`).

### 4. `body` Estructurado (`kvlistValue`)
Aquí es donde enviamos objetos complejos. OTLP usa un formato recursivo para tipos de datos:
*   **`kvlistValue`**: Representa un Objeto/Diccionario. Contiene una lista de `values` (pares key-value).
*   **`arrayValue`**: Representa una Lista/Array.
*   **`stringValue`, `intValue`, `doubleValue`, `boolValue`**: Tipos primitivos.

**Ejemplo de conversión:**
*   JSON Simple: `{"nombre": "Juan"}`
*   OTLP JSON: 
    ```json
    {
      "kvlistValue": {
        "values": [
          { "key": "nombre", "value": { "stringValue": "Juan" } }
        ]
      }
    }
    ```