"""Framework core — transport, signing, services, endpoints."""

from taygedo.core.auth_provider import AuthProvider, BearerProvider
from taygedo.core.client import BaseClient, Response
from taygedo.core.endpoint import EndpointSpec, Method, endpoint
from taygedo.core.exceptions import ApiError, ResponseValidationError, SignError, TagedoError
from taygedo.core.params import Body, Header, ParamMarker, Path, Query
from taygedo.core.service import BearerAuthService, Service, ServiceDescriptor, service
from taygedo.core.signing import NullSigner, PreparedRequest, Signer, resolve_signer

__all__ = [
    "ApiError",
    "AuthProvider",
    "BaseClient",
    "BearerAuthService",
    "BearerProvider",
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
