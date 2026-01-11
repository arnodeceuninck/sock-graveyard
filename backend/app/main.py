from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.database import engine, Base
from app.routers import auth, singles, matches
from app.config import get_settings
from app.logging_config import setup_logging, log_request, log_error, trace_id_var, span_id_var

settings = get_settings()
logger = setup_logging(service_name=settings.service_name, level="INFO")

# Configure OpenTelemetry tracing
if settings.enable_tracing:
    resource = Resource.create({
        "service.name": settings.service_name,
        "deployment.environment": settings.environment,
    })
    
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otlp_endpoint,
        timeout=5
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    logger.info(f"OpenTelemetry tracing enabled, sending to {settings.otlp_endpoint}")


# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Sock Graveyard API",
    description="A minimal API for matching lost socks",
    version="1.0.0",
    root_path="/api"
)

# Request timing and logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            # Inject current trace/span IDs for correlation
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx and ctx.trace_id:
                try:
                    trace_id_var.set(format(ctx.trace_id, '032x'))
                    span_id_var.set(format(ctx.span_id, '016x'))
                except Exception:
                    # Best-effort; skip if formatting fails
                    pass
            
            log_request(
                logger,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_host=request.client.host if request.client else None
            )
            
            return response
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            # Inject current trace/span even on errors
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx and ctx.trace_id:
                try:
                    trace_id_var.set(format(ctx.trace_id, '032x'))
                    span_id_var.set(format(ctx.span_id, '016x'))
                except Exception:
                    pass
            log_error(
                logger,
                f"Request failed: {request.method} {request.url.path}",
                exc=exc,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms
            )
            raise

app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(singles.router)
app.include_router(matches.router)

# Instrument with OpenTelemetry
if settings.enable_tracing:
    FastAPIInstrumentor().instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
    RequestsInstrumentor().instrument()

@app.get("/")
def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Sock Graveyard API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
