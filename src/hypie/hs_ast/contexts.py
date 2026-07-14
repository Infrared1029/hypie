from contextvars import ContextVar

TEMPLATE_CONTEXT = ContextVar("TEMPLATE_CONTEXT", default=False)
