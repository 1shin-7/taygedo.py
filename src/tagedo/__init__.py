"""tagedo — a Pythonic, LSP-friendly HTTP API client framework."""

from .client import TajiduoClient
from .core import (
    ApiError,
    BaseClient,
    Body,
    Header,
    NullSigner,
    Path,
    PreparedRequest,
    Query,
    Response,
    ResponseValidationError,
    Service,
    Signer,
    SignError,
    TagedoError,
    endpoint,
    service,
)

__all__ = [
    "ApiError",
    "BaseClient",
    "Body",
    "Header",
    "NullSigner",
    "Path",
    "PreparedRequest",
    "Query",
    "Response",
    "ResponseValidationError",
    "Service",
    "SignError",
    "Signer",
    "TagedoError",
    "TajiduoClient",
    "endpoint",
    "service",
]
