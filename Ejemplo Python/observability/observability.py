import logging
import grpc
import os
from dotenv import load_dotenv

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# ================================
# CARGA DE SETTINGS
# ================================
load_dotenv()

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")
OTEL_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "localhost:4317")
OTEL_BEARER_TOKEN = os.getenv("OTEL_BEARER_TOKEN", "")
APP_ENV = os.getenv("APP_ENV", "development").lower()

HEADERS = (("authorization", f"Bearer {OTEL_BEARER_TOKEN}"),)

# ================================
# CERTIFICADO
# ================================
if APP_ENV == "local":
    print("Modo local: Usando credenciales inseguras (sin SSL/TLS).")
    ssl_credentials = None  # None indicates insecure/plain text
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if APP_ENV in ["development", "dev", "test"]:
        CERT_FILE = os.path.join(current_dir, "otel-test-ca.pem")
    else:
        CERT_FILE = os.path.join(current_dir, "otel-prod-ca.pem")

    try:
        with open(CERT_FILE, "rb") as f:
            trusted_certs = f.read()
        ssl_credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
    except FileNotFoundError:
        print(
            f"Advertencia: No se encontro el certificado en {CERT_FILE}. Usando credenciales inseguras si aplica o fallara."
        )
        # Fallback to system certificates or default SSL
        ssl_credentials = grpc.ssl_channel_credentials()

# ================================
# RESOURCE
# ================================
resource = Resource.create(
    {"service.name": SERVICE_NAME, "service.namespace": "intuitosa"}
)

# ================================
# TRACES
# ================================
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(
    endpoint=OTEL_ENDPOINT,
    headers=HEADERS,
    credentials=ssl_credentials,
    insecure=True if ssl_credentials is None else False,
)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(SERVICE_NAME)

# ================================
# METRICS
# ================================
metric_exporter = OTLPMetricExporter(
    endpoint=OTEL_ENDPOINT,
    headers=HEADERS,
    credentials=ssl_credentials,
    insecure=True if ssl_credentials is None else False,
)

metric_reader = PeriodicExportingMetricReader(metric_exporter)

meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(SERVICE_NAME)

# ================================
# LOGS
# ================================
logger_provider = LoggerProvider(resource=resource)

log_exporter = OTLPLogExporter(
    endpoint=OTEL_ENDPOINT,
    headers=HEADERS,
    credentials=ssl_credentials,
    insecure=True if ssl_credentials is None else False,
)


ENABLE_CONSOLE_LOGS = os.getenv("ENABLE_CONSOLE_LOGS", "true").lower() == "true"

logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

if ENABLE_CONSOLE_LOGS:
    logger_provider.add_log_record_processor(
        SimpleLogRecordProcessor(ConsoleLogExporter())
    )

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)

# Removed StreamHandler to avoid duplicate/plain text logs
logger.addHandler(LoggingHandler(logger_provider=logger_provider))
