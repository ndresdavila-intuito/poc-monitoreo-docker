import logging
import grpc
import os
from dotenv import load_dotenv

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Import exporters for both protocols
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGRPC,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterHTTP,
)

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter as OTLPMetricExporterGRPC,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as OTLPMetricExporterHTTP,
)

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter as OTLPLogExporterGRPC,
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as OTLPLogExporterHTTP,
)

# ================================
# CARGA DE SETTINGS
# ================================
load_dotenv()

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "localhost:4317")
OTEL_BEARER_TOKEN = os.getenv("OTEL_BEARER_TOKEN", "")
APP_ENV = os.getenv("APP_ENV", "development").lower()
OTEL_EXPORTER_PROTOCOL = os.getenv(
    "OTEL_EXPORTER_PROTOCOL", "grpc"
).lower()  # grpc or http

HEADERS = (("authorization", f"Bearer {OTEL_BEARER_TOKEN}"),)

print(
    f"--> Configurando OpenTelemetry: Protocolo={OTEL_EXPORTER_PROTOCOL}, Endpoint={OTEL_COLLECTOR_ENDPOINT}"
)

# ================================
# CERTIFICADO (Solo relevante para gRPC o HTTPS)
# ================================
ssl_credentials = None
if OTEL_EXPORTER_PROTOCOL == "grpc":
    if APP_ENV == "local":
        print("Modo local (gRPC): Usando credenciales inseguras.")
        ssl_credentials = None
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if APP_ENV in ["development", "dev", "test"]:
            CERT_FILE = os.path.join(current_dir, "otel-test-ca.pem")
        else:
            CERT_FILE = os.path.join(current_dir, "otel-prod-ca.pem")

        try:
            with open(CERT_FILE, "rb") as f:
                trusted_certs = f.read()
            ssl_credentials = grpc.ssl_channel_credentials(
                root_certificates=trusted_certs
            )
        except FileNotFoundError:
            print(
                f"Advertencia: No se encontro el certificado en {CERT_FILE}. Usando credenciales inseguras."
            )
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

if OTEL_EXPORTER_PROTOCOL == "http":
    # HTTP Exporter
    trace_exporter = OTLPSpanExporterHTTP(
        endpoint=f"{OTEL_COLLECTOR_ENDPOINT}/v1/traces",
        headers=dict(HEADERS),  # HTTP headers expects dict usually
    )
else:
    # gRPC Exporter
    trace_exporter = OTLPSpanExporterGRPC(
        endpoint=OTEL_COLLECTOR_ENDPOINT,
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
if OTEL_EXPORTER_PROTOCOL == "http":
    metric_exporter = OTLPMetricExporterHTTP(
        endpoint=f"{OTEL_COLLECTOR_ENDPOINT}/v1/metrics", headers=dict(HEADERS)
    )
else:
    metric_exporter = OTLPMetricExporterGRPC(
        endpoint=OTEL_COLLECTOR_ENDPOINT,
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

if OTEL_EXPORTER_PROTOCOL == "http":
    log_exporter = OTLPLogExporterHTTP(
        endpoint=f"{OTEL_COLLECTOR_ENDPOINT}/v1/logs", headers=dict(HEADERS)
    )
else:
    log_exporter = OTLPLogExporterGRPC(
        endpoint=OTEL_COLLECTOR_ENDPOINT,
        headers=HEADERS,
        credentials=ssl_credentials,
        insecure=True if ssl_credentials is None else False,
    )

ENABLE_CONSOLE_LOGS = os.getenv("ENABLE_CONSOLE_LOGS", "false").lower() == "true"

logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

if ENABLE_CONSOLE_LOGS:
    logger_provider.add_log_record_processor(
        SimpleLogRecordProcessor(ConsoleLogExporter())
    )

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(LoggingHandler(logger_provider=logger_provider))
