"""taygedo — a Pythonic, LSP-friendly HTTP API client framework."""

from taygedo.client import TaygedoClient
from taygedo.core import (
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
    "TaygedoClient",
    "endpoint",
    "service",
]
