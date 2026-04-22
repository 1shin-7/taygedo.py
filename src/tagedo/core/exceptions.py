"""Exception hierarchy for the tagedo framework."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic import ValidationError


class TagedoError(Exception):
    """Base class for every error raised by the framework."""


class SignError(TagedoError):
    """Raised when a Signer fails to sign a request."""


class ApiError(TagedoError):
    """Raised when the remote API responds with a non-2xx status."""

    def __init__(self, status_code: int, body: Any, message: str | None = None) -> None:
        super().__init__(message or f"API request failed with status {status_code}")
        self.status_code = status_code
        self.body = body


class ResponseValidationError(TagedoError):
    """Raised when the response body cannot be parsed into the declared model."""

    def __init__(self, raw_data: object, validation_error: ValidationError) -> None:
        super().__init__(
            f"Response payload failed validation: {validation_error.error_count()} error(s)",
        )
        self.raw_data = raw_data
        self.validation_error = validation_error
