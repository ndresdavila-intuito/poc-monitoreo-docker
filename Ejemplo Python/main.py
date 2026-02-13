import time
import random
import uuid
import string
import json

from observability.observability import logger
import observability.metrics as metrics
from observability.decorator import instrument
from opentelemetry import trace

# 1. Inicializar métricas
logger.info("Inicializando metricas...")
metrics.init_metrics()


class Usuario:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.nombre = (
            "".join(random.choices(string.ascii_uppercase, k=5))
            + " "
            + "".join(random.choices(string.ascii_uppercase, k=5))
        )
        self.email = f"{self.nombre.replace(' ', '.').lower()}@example.com"

        # Contexto Técnico (Simulado)
        self.contexto = {
            "ip": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "user_agent": random.choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                ]
            ),
            "device": random.choice(["Desktop", "Mobile", "Tablet"]),
        }

        # Carrito de Compras (Lista de Objetos)
        self.carrito = []
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            item = {
                "producto_id": str(uuid.uuid4()),
                "producto_nombre": f"Item-{random.randint(100, 999)}",
                "cantidad": random.randint(1, 3),
                "precio_unitario": round(random.uniform(10.0, 100.0), 2),
            }
            item["total_linea"] = round(item["cantidad"] * item["precio_unitario"], 2)
            self.carrito.append(item)

        self.total_carrito = sum(i["total_linea"] for i in self.carrito)
        self.cantidad_items = sum(i["cantidad"] for i in self.carrito)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "contexto": self.contexto,
            "carrito": self.carrito,
            "total_carrito": self.total_carrito,
            "cantidad_items": self.cantidad_items,
        }


@instrument(operation_name="procesar_transaccion")
def procesar_transaccion(usuario: Usuario):
    """Simula el procesamiento de una transacción de e-commerce real."""

    # 1. Enriquecer Span con Semantic Conventions
    current_span = trace.get_current_span()

    if current_span.is_recording():
        # General Identity
        current_span.set_attribute("enduser.id", usuario.id)
        current_span.set_attribute("enduser.email", usuario.email)

        # HTTP / Network Context
        current_span.set_attribute("http.client_ip", usuario.contexto["ip"])
        current_span.set_attribute(
            "user_agent.original", usuario.contexto["user_agent"]
        )
        current_span.set_attribute("device.type", usuario.contexto["device"])

        # Business Logic Attributes
        current_span.set_attribute("ecommerce.cart.total", usuario.total_carrito)
        current_span.set_attribute("ecommerce.cart.items_count", usuario.cantidad_items)

    # 2. Log Estructurado Complejo
    # Enviamos todo el objeto usuario como un string JSON en el body o como atributos
    # Aquí usamos 'extra' para que se mapee a atributos del log.
    logger.info(
        f"Checkout iniciado por {usuario.nombre}",
        extra={
            "usuario.json": json.dumps(
                usuario.to_dict()
            ),  # Serializado para que quepa en un campo string si es necesario
            "usuario.id": usuario.id,
            "ecommerce.total": usuario.total_carrito,
        },
    )

    # Simular procesamiento
    sleep_time = random.uniform(0.2, 0.8)
    time.sleep(sleep_time)

    # 3. Registrar Métricas de Negocio
    if metrics.transacciones_usuario_counter:
        metrics.transacciones_usuario_counter.add(
            1,
            {
                "device.type": usuario.contexto["device"],
                "payment.method": random.choice(["credit_card", "paypal", "apple_pay"]),
            },
        )

    if metrics.ecommerce_cart_value:
        metrics.ecommerce_cart_value.record(
            usuario.total_carrito, {"device.type": usuario.contexto["device"]}
        )

    if metrics.ecommerce_items_sold:
        metrics.ecommerce_items_sold.add(
            usuario.cantidad_items, {"device.type": usuario.contexto["device"]}
        )

    # Simular error de tarjeta rechazada (Business Error)
    if random.random() < 0.1:
        logger.error(
            f"Error: Pago rechazado para usuario {usuario.id}",
            extra={"usuario.id": usuario.id, "error.code": "PAYMENT_DECLINED"},
        )
        # No lanzamos excepción para no detener el loop, pero marcamos el error en el span si quisiéramos
        current_span.set_status(
            trace.Status(trace.StatusCode.ERROR, "Payment Declined")
        )


@instrument(operation_name="process_legacy_task")
def process_data(user_id):
    """Simula una tarea legacy."""
    time.sleep(0.1)


def main():
    logger.info(
        "Iniciando simulacion de E-Commerce Real (Presiona Ctrl+C para detener)..."
    )
    try:
        while True:
            # 1. Gauge: Usuarios activos fluctuando
            if metrics.active_users_gauge:
                metrics.active_users_gauge.add(random.randint(-5, 10))

            try:
                # 2. Generar usuario complejo y procesar
                usuario = Usuario()
                procesar_transaccion(usuario)

                # Tráfico legacy ocasional
                if random.random() < 0.2:
                    process_data(random.randint(1000, 9999))
                    if metrics.request_counter:
                        metrics.request_counter.add(1, {"endpoint": "/api/legacy"})

            except Exception as e:
                logger.error(f"Error en loop principal: {e}")

            # 4. Ping Simulado
            ping = random.uniform(20, 150)
            metrics.current_ping_value = ping

            time.sleep(1.5)

    except KeyboardInterrupt:
        logger.info("\nDeteniendo simulacion...")


if __name__ == "__main__":
    main()
