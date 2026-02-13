import observability.observability as obs
from opentelemetry.metrics import CallbackOptions, Observation

request_counter = None
processing_duration = None
active_users_gauge = None
transacciones_usuario_counter = None
ecommerce_cart_value = None
ecommerce_items_sold = None
# Variable global para almacenar el valor actual del ping
current_ping_value = 0


def ping_callback(options: CallbackOptions):
    """Callback para reportar el valor actual del ping."""
    yield Observation(value=current_ping_value)


def init_metrics():
    global \
        request_counter, \
        processing_duration, \
        active_users_gauge, \
        transacciones_usuario_counter, \
        ecommerce_cart_value, \
        ecommerce_items_sold

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
        "ecommerce.usuarios.activos",
        unit="1",
        description="Usuarios concurrentes en el sitio",
    )

    # Counter: Número de transacciones de usuarios (Checkouts)
    global transacciones_usuario_counter
    transacciones_usuario_counter = meter.create_counter(
        "ecommerce.abonos.total",
        unit="1",
        description="Total de ventas realizadas",
    )

    # Histogram: Valor del carrito de compras
    global ecommerce_cart_value
    ecommerce_cart_value = meter.create_histogram(
        "ecommerce.cart.value",
        unit="USD",
        description="Valor monetario de los carritos procesados",
    )

    # Counter: Ítems vendidos
    global ecommerce_items_sold
    ecommerce_items_sold = meter.create_counter(
        "ecommerce.items.count",
        unit="1",
        description="Total de ítems individuales vendidos",
    )

    # ObservableGauge: Ideal para valores que "son" (como temperatura o ping actual)
    # Se actualiza via callback.
    meter.create_observable_gauge(
        "demo.ping.latency",
        callbacks=[ping_callback],
        unit="ms",
        description="Latencia simulada de ping",
    )
