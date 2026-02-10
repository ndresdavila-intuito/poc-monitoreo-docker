-- Create otel_logs table
CREATE TABLE IF NOT EXISTS default.otel_logs (
    Timestamp DateTime64(9),
    TraceId String,
    SpanId String,
    TraceFlags UInt32,
    SeverityText String,
    SeverityNumber Int32,
    ServiceName String,
    Body String,
    ResourceSchemaUrl String,
    ResourceAttributes Map(String, String),
    ScopeSchemaUrl String,
    ScopeName String,
    ScopeVersion String,
    ScopeAttributes Map(String, String),
    LogAttributes Map(String, String)
) ENGINE = MergeTree()
PARTITION BY toDate(Timestamp)
ORDER BY (ServiceName, SeverityText, Timestamp);

-- Create otel_traces table
CREATE TABLE IF NOT EXISTS default.otel_traces (
    Timestamp DateTime64(9),
    TraceId String,
    SpanId String,
    ParentSpanId String,
    TraceState String,
    SpanName String,
    SpanKind String,
    ServiceName String,
    ResourceAttributes Map(String, String),
    ScopeName String,
    ScopeVersion String,
    SpanAttributes Map(String, String),
    Duration UInt64,
    StatusCode String,
    StatusMessage String,
    Events Nested(
        Timestamp DateTime64(9),
        Name String,
        Attributes Map(String, String)
    ),
    Links Nested(
        TraceId String,
        SpanId String,
        TraceState String,
        Attributes Map(String, String)
    )
) ENGINE = MergeTree()
PARTITION BY toDate(Timestamp)
ORDER BY (ServiceName, SpanName, Timestamp);
