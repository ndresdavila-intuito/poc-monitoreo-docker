import time
from opentelemetry._logs import LogRecord
from observability.observability import logger_provider


def main():
    # 1. Obtener un Logger de OpenTelemetry (SDK)
    # Importante: Usamos el logger provider configurado en observability.py
    otel_logger = logger_provider.get_logger("ejemplo.log.estructurado")

    # 2. Definir el cuerpo estructurado (Diccionario Python)
    # OpenTelemetry lo convertirá automáticamente a kvlistValue en OTLP
    persona_body = {
        "nombre": "Juan Perez",
        "email": "juan.perez@example.com",
        "telefono": "+5512345678",
        "direccion": {"calle": "Av. Reforma 123", "ciudad": "CDMX", "cp": "06500"},
    }

    print("Enviando log con body estructurado...")

    # 3. Crear y emitir el LogRecord
    # Nota: Al usar el SDK directamente, podemos pasar un diccionario al 'body'
    log_record = LogRecord(
        timestamp=time.time_ns(),
        body=persona_body,
        severity_text="INFO",
        severity_number=9,
        attributes={
            "enduser.id": "user-123",
            "event.type": "manual_test",
            "description": "Log enviado desde script Python manual",
        },
    )

    otel_logger.emit(log_record)

    print("Log enviado correctamente.")

    # 4. Forzar el envío (Flush)
    # Al ser un script corto, debemos asegurar que el BatchProcessor envíe los datos
    logger_provider.force_flush()
    # Opcional: logger_provider.shutdown()


if __name__ == "__main__":
    main()
