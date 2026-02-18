import uvicorn
import pprint
import observability.metrics as metrics
from fastapi import FastAPI
from opentelemetry import trace
from pydantic import BaseModel
from observability.decorator import instrument
from observability.observability import (
    logger,
    logger_provider,
    trace_provider,
    meter_provider,
)

# Suprimir warnings de Pydantic y OTel para mantener la consola limpia
import warnings

warnings.filterwarnings("ignore")


# --- CLASE INTERCEPTORA ---
class InterceptorExporter:
    """
    Clase que intercepta los exportadores OTLP (OpenTelemetry Protocol) y les agrega el interceptor (InterceptorExporter)
    Input:
    - inner_exporter: Exportador original
    - signal_type: Tipo de señal (logs, traces, metrics)
    """

    def __init__(self, inner_exporter, signal_type):
        self.inner_exporter = inner_exporter
        self.signal_type = signal_type

    """
    Función que muestra el contenido de un objeto en un formato legible
    Input:
    - obj: Objeto a mostrar
    - label: Etiqueta del objeto
    - indent: Indentación
    """

    def _extract_raw(self, item):
        """Introspección profunda para extraer atributos de objetos complejos."""
        # Tipos básicos
        if isinstance(item, (str, int, float, bool, type(None))):
            return item
        if isinstance(item, (list, tuple)):
            return [self._extract_raw(x) for x in item]
        if isinstance(item, dict):
            return {k: self._extract_raw(v) for k, v in item.items()}

        # Introspección para objetos
        res = {}
        # Usar __dict__ como base rápida
        if hasattr(item, "__dict__"):
            for k, v in vars(item).items():
                if not k.startswith("_"):
                    res[k] = self._extract_raw(v)

        # Complementar con dir()
        for attr in dir(item):
            if (
                attr.startswith("_")
                or attr in res
                or callable(getattr(item, attr, None))
            ):
                continue
            try:
                val = getattr(item, attr)
                res[attr] = self._extract_raw(val)
            except Exception:
                continue

        return res if res else str(item)

    def _pretty_print_object(self, obj, label, indent=2):
        prefix = "  " * indent
        print(f"\n{prefix}[{label}]")

        import json

        data_to_print = self._extract_raw(obj)
        try:
            formatted = json.dumps(data_to_print, indent=4, default=str)
        except Exception:
            formatted = pprint.pformat(data_to_print, indent=4, width=120)

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

        raw_res = self._extract_raw(result)
        print("  - Contenido Interno (Raw):")
        import json

        try:
            formatted_res = json.dumps(raw_res, indent=4, default=str)
            for line in formatted_res.splitlines():
                print(f"    {line}")
        except Exception:
            pprint.pprint(raw_res, indent=4, width=120)
        print("#" * 80 + "\n")

        return result

    def shutdown(self, **kwargs):
        self.inner_exporter.shutdown(**kwargs)


# --- VINCULACIÓN PROFUNDA (OTel Internal Access) ---
print("\n--- Vinculando Interceptores OTLP (Deep Binding) ---")


"""
Función que busca los exportadores OTLP (OpenTelemetry Protocol) y les agrega el interceptor (InterceptorExporter)
Input: 
- processor: Procesador de señales (logs, traces, metrics)
- signal_type: Tipo de señal (logs, traces, metrics)
"""


def deep_bind(processor, signal_type):
    print(f"  [Debug] Analizando procesador: {type(processor).__name__}")

    # Itera sobre los atributos del procesador
    for attr in dir(processor):
        try:
            val = getattr(processor, attr)
            # Si el valor tiene 'OTLP' en su representacion, tiene metodo 'export' y no es un interceptor
            if (
                val
                and "OTLP" in str(val)
                and hasattr(val, "export")
                and not isinstance(val, InterceptorExporter)
            ):
                # Reemplazo el exporter original con el interceptor
                setattr(processor, attr, InterceptorExporter(val, signal_type))
                print(
                    f"[OK] {signal_type} -> Encontrado en {type(processor).__name__}.{attr}"
                )
                return True
        except (AttributeError, TypeError, Exception):
            continue

    # Si no se encuentra, se busca en el atributo _batch_processor
    if hasattr(processor, "_batch_processor"):
        helper = processor._batch_processor
        print(
            f"[Debug] Buscando dentro de _batch_processor de {type(processor).__name__}"
        )
        # Itera sobre los atributos del helper
        for attr in dir(helper):
            try:
                val = getattr(helper, attr)
                # Si el valor tiene 'OTLP' en su representacion, tiene metodo 'export' y no es un interceptor
                if (
                    val
                    and "OTLP" in str(val)
                    and hasattr(val, "export")
                    and not isinstance(val, InterceptorExporter)
                ):
                    # Reemplazo el exporter original con el interceptor
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


class Usuario(BaseModel):
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: str
    cedula: str
    nacionalidad: str
    estado_civil: str


def _print_curl_command(url: str, body: dict):
    """Imprime el comando curl equivalente para esta solicitud."""
    import json

    print("\n" + "~" * 80)
    print("### [CURL COMMAND] PARA REPRODUCIR ESTA PETICIÓN:")
    print("~" * 80)

    cmd = f"curl -X POST '{url}' \\\n"
    cmd += "  -H 'Content-Type: application/json' \\\n"
    cmd += f"  -d '{json.dumps(body)}'"

    print(cmd)
    print("~" * 80 + "\n")


@app.post("/crear_usuario")
@instrument(operation_name="crear_usuario_op")
def crear_usuario(usuario: Usuario):
    # 0. Agregar atributos al span actual de la traza
    current_span = trace.get_current_span()
    if current_span.is_recording():
        current_span.set_attribute("usuario.nombre", usuario.nombre)
        current_span.set_attribute("usuario.apellido", usuario.apellido)
        current_span.set_attribute("usuario.email", usuario.email)
        current_span.set_attribute("usuario.cedula", usuario.cedula)
        current_span.set_attribute("usuario.nacionalidad", usuario.nacionalidad)
        current_span.set_attribute("usuario.fecha_nacimiento", usuario.fecha_nacimiento)
        current_span.set_attribute("usuario.estado_civil", usuario.estado_civil)

    # 1. Imprimir Curl
    _print_curl_command("http://localhost:8000/crear_usuario", usuario.model_dump())

    # 2. Logica de Negocio (Simulada)
    msg = f"Usuario {usuario.nombre} {usuario.apellido} agregado"

    # 3. Telemetria
    # LOG
    log_payload = usuario.model_dump()
    log_payload["evento"] = "creacion_usuario"
    log_payload["mensaje"] = msg

    logger.info(log_payload)

    # METRICA
    if metrics.usuarios_creados_counter:
        metrics.usuarios_creados_counter.add(
            1, {"origen": "api_demo", "nacionalidad": usuario.nacionalidad}
        )

    print("\n[PYTHON] Solicitando envio inmediato de telemetria al Collector...")
    # Forzamos flush para ver los logs OTLP inmediatamente en consola
    logger_provider.force_flush()
    trace_provider.force_flush()

    return {"status": "ok", "mensaje": msg}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
