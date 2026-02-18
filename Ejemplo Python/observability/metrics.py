import observability.observability as obs

usuarios_creados_counter = None


def init_metrics():
    global usuarios_creados_counter

    meter = obs.meter

    if meter is None:
        raise RuntimeError(
            "Meter aún no está inicializado. Llama init_observability() antes de init_metrics()."
        )

    # Counter: Número total de usuarios creados
    usuarios_creados_counter = meter.create_counter(
        "demo.usuarios.creados",
        unit="1",
        description="Número total de usuarios creados",
    )
