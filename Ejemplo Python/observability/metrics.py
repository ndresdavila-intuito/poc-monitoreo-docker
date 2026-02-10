import observability.observability as obs
from opentelemetry.metrics import CallbackOptions, Observation

request_counter = None
processing_duration = None
active_users_gauge = None
# Variable global para almacenar el valor actual del ping
current_ping_value = 0


def ping_callback(options: CallbackOptions):
    """Callback para reportar el valor actual del ping."""
    yield Observation(value=current_ping_value)


def init_metrics():
    global request_counter, processing_duration, active_users_gauge

    meter = obs.meter

    if meter is None:
        raise RuntimeError(
            "Meter aún no está inicializado. Llama init_observability() antes de init_metrics()."
        )

    # Counter: Número total de solicitudes
    request_counter = meter.create_counter(
        "demo.requests.total",
        unit="1",
        description="Número total de solicitudes procesadas",
    )

    # Histogram: Duración del procesamiento de tareas
    processing_duration = meter.create_histogram(
        "demo.processing.duration",
        unit="ms",
        description="Tiempo de procesamiento de tareas simuladas",
    )

    # UpDownCounter (Gauge simulado): Usuarios activos
    active_users_gauge = meter.create_up_down_counter(
        "demo.active_users", unit="1", description="Número simulado de usuarios activos"
    )

    # ObservableGauge: Ideal para valores que "son" (como temperatura o ping actual)
    # Se actualiza via callback.
    meter.create_observable_gauge(
        "demo.ping.latency",
        callbacks=[ping_callback],
        unit="ms",
        description="Latencia simulada de ping",
    )
