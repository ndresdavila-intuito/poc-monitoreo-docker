import time
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pprint

# Importamos nuestra configuración de observabilidad
from observability.observability import (
    logger,
    logger_provider,
    trace_provider,
    meter_provider,
)
import observability.metrics as metrics
from observability.decorator import instrument


# --- CLASE INTERCEPTORA RAW ---
class InterceptorExporter:
    def __init__(self, inner_exporter, signal_type):
        self.inner_exporter = inner_exporter
        self.signal_type = signal_type

    def _pretty_print_object(self, obj, label, indent=2):
        prefix = "  " * indent
        print(f"\n{prefix}[{label}]")

        # --- LÓGICA DE DESENVOLVIMIENTO (UNWRAPPING) ---
        # Si es un Log, queremos ver lo que hay dentro de 'log_record'
        if hasattr(obj, "log_record"):
            lr = obj.log_record
            data_to_print = {
                "body": lr.body,
                "severity": lr.severity_text,
                "attributes": dict(lr.attributes) if lr.attributes else {},
                "trace_id": hex(lr.trace_id) if hasattr(lr, "trace_id") else None,
                "span_id": hex(lr.span_id) if hasattr(lr, "span_id") else None,
                "resource": dict(obj.resource.attributes)
                if hasattr(obj, "resource")
                else {},
            }
        # Si es un Span (Traza), queremos ver su contexto y atributos
        elif hasattr(obj, "context") and hasattr(obj, "kind"):
            data_to_print = {
                "name": obj.name,
                "context": {
                    "trace_id": hex(obj.context.trace_id),
                    "span_id": hex(obj.context.span_id),
                },
                "kind": str(obj.kind),
                "attributes": dict(obj.attributes) if obj.attributes else {},
                "start_time": obj.start_time,
                "end_time": obj.end_time,
            }
        else:
            # Fallback para métricas u otros objetos (introspección genérica)
            data_to_print = vars(obj) if hasattr(obj, "__dict__") else {}
            if not data_to_print:
                data_to_print = {
                    a: getattr(obj, a)
                    for a in dir(obj)
                    if not a.startswith("_") and not callable(getattr(obj, a, None))
                }

        formatted = pprint.pformat(data_to_print, indent=2, width=80)
        for line in formatted.splitlines():
            print(f"{prefix}  {line}")

    def export(self, data, **kwargs):
        print("\n" + "#" * 80)
        print(
            f"### [OTLP REQUEST RAW] TRANSMISIÓN OTLP - SEÑAL: {self.signal_type.upper()}"
        )
        print("#" * 80)

        items = data if isinstance(data, (list, tuple)) else [data]
        for i, item in enumerate(items):
            self._pretty_print_object(item, f"Elemento {i + 1} - {type(item).__name__}")

        print("-" * 80)

        # --- TRANSMISIÓN REAL ---
        result = self.inner_exporter.export(data, **kwargs)

        # --- RESPUESTA ---
        print(
            f"<<< [OTLP RESPONSE RAW] RESPUESTA DEL COLLECTOR ({self.signal_type.upper()})"
        )
        # Mostramos la clase y todo el contenido interno del objeto de respuesta
        print(
            f"  - Clase del Objeto: {type(result).__module__}.{type(result).__name__}"
        )

        # Intentamos sacar el diccionario interno o sus atributos via dir()
        raw_res = {}
        if hasattr(result, "__dict__"):
            raw_res = vars(result)
        else:
            for attr in dir(result):
                if not attr.startswith("__") and not callable(
                    getattr(result, attr, None)
                ):
                    try:
                        raw_res[attr] = getattr(result, attr)
                    except:
                        pass

        print("  - Contenido Interno (Raw):")
        pprint.pprint(raw_res, indent=4)
        print("#" * 80 + "\n")

        return result

    def shutdown(self, **kwargs):
        self.inner_exporter.shutdown(**kwargs)


# --- VINCULACIÓN PROFUNDA (OTel Internal Access) ---
print("\n--- Vinculando Interceptores OTLP (Deep Binding) ---")


def deep_bind(processor, signal_type):
    print(f"  [Debug] Analizando procesador: {type(processor).__name__}")

    # Lista de todos los atributos que podrian contener el exporter
    for attr in dir(processor):
        try:
            val = getattr(processor, attr)
            # Si el valor tiene 'OTLP' en su representacion y tiene metodo 'export'
            if (
                val
                and "OTLP" in str(val)
                and hasattr(val, "export")
                and not isinstance(val, InterceptorExporter)
            ):
                setattr(processor, attr, InterceptorExporter(val, signal_type))
                print(
                    f"    [OK] {signal_type} -> Encontrado en {type(processor).__name__}.{attr}"
                )
                return True
        except (AttributeError, TypeError, Exception):
            continue

    # Si no lo encontramos, buscamos un nivel mas adentro (ej. _batch_processor)
    if hasattr(processor, "_batch_processor"):
        helper = processor._batch_processor
        print(
            f"    [Debug] Buscando dentro de _batch_processor de {type(processor).__name__}"
        )
        for attr in dir(helper):
            try:
                val = getattr(helper, attr)
                if (
                    val
                    and "OTLP" in str(val)
                    and hasattr(val, "export")
                    and not isinstance(val, InterceptorExporter)
                ):
                    setattr(helper, attr, InterceptorExporter(val, signal_type))
                    print(
                        f"    [OK] {signal_type} -> Encontrado en {type(processor).__name__}._batch_processor.{attr}"
                    )
                    return True
            except Exception:
                continue

    return False


# 1. Logs
log_procs = getattr(
    logger_provider._multi_log_record_processor, "_log_record_processors", []
)
for p in log_procs:
    deep_bind(p, "LOGS")

# 2. Traces
trace_procs = getattr(trace_provider._active_span_processor, "_span_processors", [])
for p in trace_procs:
    deep_bind(p, "TRACES")

# 3. Metrics
try:
    for reader in meter_provider._sdk_config.metric_readers:
        if not deep_bind(reader, "METRICS"):
            # Fallback manual para métricas si el reader es raro
            if hasattr(reader, "_exporter") and "OTLP" in str(reader._exporter):
                reader._exporter = InterceptorExporter(reader._exporter, "METRICS")
                print(
                    f"    [OK] METRICS -> {type(reader).__name__}._exporter (fallback)"
                )
except Exception:
    pass


# --- API CON LOG ESTRUCTURADO ---
metrics.init_metrics()
app = FastAPI(title="Demo Observabilidad Raw")


class Compra(BaseModel):
    producto: str
    precio: float
    usuario: str


@app.post("/comprar")
@instrument(operation_name="venta_raw")
def realizar_compra(compra: Compra):
    logger.info(
        {"msg": "Ejecutando venta", "usuario": compra.usuario, "monto": compra.precio}
    )

    time.sleep(0.05)

    if metrics.transacciones_usuario_counter:
        metrics.transacciones_usuario_counter.add(1, {"debug": "raw"})

    print("\n[PYTHON] Solicitando envio inmediato de telemetria al Collector...")
    logger_provider.force_flush()
    trace_provider.force_flush()

    return {"status": "ok", "ver": "Mira los bloques RAW en la consola abajo"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
