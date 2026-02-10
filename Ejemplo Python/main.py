import time
import random

from observability.observability import logger
import observability.metrics as metrics
from observability.decorator import instrument

# 1. Inicializar métricas
logger.info("Inicializando metricas...")
metrics.init_metrics()


@instrument(operation_name="process_user_data")
def process_data(user_id):
    """Simula una tarea de procesamiento."""

    # Simular trabajo
    sleep_time = random.uniform(0.1, 0.5)
    time.sleep(sleep_time)

    # Registrar métrica de duración manualmente (además de lo que hace el tracer)
    if metrics.processing_duration:
        metrics.processing_duration.record(sleep_time * 1000, {"user_type": "standard"})

    # Simular un error ocasional
    if random.random() < 0.1:
        raise ValueError("Error aleatorio simulado durante el procesamiento")


def main():
    logger.info("Iniciando simulacion de trafico (Presiona Ctrl+C para detener)...")
    try:
        while True:
            # 1. Incrementar contador de usuarios activos
            metrics.active_users_gauge.add(1)

            try:
                # 2. Incrementar contador de requests global
                metrics.request_counter.add(1, {"endpoint": "/api/process"})

                # 3. Llamada a función instrumentada
                user_id = random.randint(1000, 9999)
                process_data(user_id)

                logger.info(f"Solicitud completada para usuario {user_id}")
            except Exception as e:
                logger.error(f"Error procesando solicitud: {e}")

            # Decrementar contador de usuarios activos
            metrics.active_users_gauge.add(-1)

            # 4. Registrar Ping simulado
            ping_latency = random.uniform(10, 300)  # De 10ms a 300ms
            metrics.current_ping_value = (
                ping_latency  # Actualizar el valor para el ObservableGauge
            )
            if ping_latency > 200:
                logger.warning(f"Ping alto detectado: {ping_latency:.2f}ms")

            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("\nDeteniendo simulacion...")


if __name__ == "__main__":
    main()
