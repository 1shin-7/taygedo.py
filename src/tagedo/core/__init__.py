"""Framework core — transport, signing, services, endpoints."""

from .client import BaseClient, Response
from .endpoint import EndpointSpec, Method, endpoint
from .exceptions import ApiError, ResponseValidationError, SignError, TagedoError
from .params import Body, Header, ParamMarker, Path, Query
from .service import Service, ServiceDescriptor, service
from .signing import NullSigner, PreparedRequest, Signer, resolve_signer

__all__ = [
    "ApiError",
    "BaseClient",
    "Body",
    "EndpointSpec",
    "Header",
    "Method",
    "NullSigner",
    "ParamMarker",
    "Path",
    "PreparedRequest",
    "Query",
    "Response",
    "ResponseValidationError",
    "Service",
    "ServiceDescriptor",
    "SignError",
    "Signer",
    "TagedoError",
    "endpoint",
    "resolve_signer",
    "service",
]
