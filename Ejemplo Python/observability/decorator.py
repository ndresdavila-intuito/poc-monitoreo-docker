import time
import functools
from opentelemetry import trace
from observability.observability import tracer

def instrument(operation_name: str, measure_latency=True):
    """
    Decorador genérico para instrumentar funciones con Tracing y (opcionalmente) métricas.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Iniciar un nuevo Span
            with tracer.start_as_current_span(operation_name) as span:
                try:
                    # Añadir atributos al span (contexto)
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("module.name", func.__module__)

                    start_time = time.perf_counter()
                    
                    # Ejecutar la función original
                    result = func(*args, **kwargs)
                    
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000

                    # Registrar evento de éxito
                    span.add_event("Execution completed", {"duration_ms": duration_ms})
                    
                    return result

                except Exception as e:
                    # Registrar excepción en el span
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator
