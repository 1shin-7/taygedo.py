"""The endpoint decorator and its runtime engine.

``@endpoint(method, path, *, sign=None, strict=True)`` turns a Service method
declaration into a fully working HTTP call. The method body is irrelevant
(typically ``...``); the decorator inspects the signature to build an
``EndpointSpec`` once at class-definition time, and at call time uses the spec
to assemble a request, sign it, dispatch it, and parse the response.

Type discipline
---------------
The decorator is typed as ``Callable[P, Awaitable[R]] -> Callable[P, Awaitable[R]]``,
so the wrapped method's signature is preserved verbatim for LSP and mypy. There
are no injected parameters, no ``Depends(...)``, no ``ctx``: the method's
declared signature *is* its public contract.

Parameter inference
-------------------
For each parameter (besides ``self``):
  * If annotated as ``Annotated[T, Path()]`` → URL path variable.
  * If annotated as ``Annotated[T, Query(alias=...)]`` → query string entry.
  * If annotated as ``Annotated[T, Header(name=...)]`` → HTTP header.
  * If annotated as ``Annotated[T, Body()]`` → request body.
  * Otherwise:
      - if its name appears in the path template → Path
      - if its type is a BaseModel subclass → Body
      - else → Query
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import wraps
from string import Formatter
from typing import (
    Annotated,
    Any,
    Literal,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel, ValidationError

from .exceptions import ApiError, ResponseValidationError, SignError
from .params import Body, Header, ParamMarker, Path, Query
from .signing import PreparedRequest, Signer, resolve_signer
from .types import P, R

__all__ = ["EndpointSpec", "Method", "endpoint"]

Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

_PARAM_KINDS = (Path, Query, Header, Body)


@dataclass(slots=True)
class _ParamBinding:
    name: str
    kind: type[ParamMarker]
    alias: str | None
    annotation: Any


@dataclass(slots=True)
class EndpointSpec:
    """Compiled metadata for an endpoint, computed once at decoration time."""

    method: Method
    path: str
    sign: Signer | type[Signer] | None
    strict: bool
    return_annotation: Any
    bindings: list[_ParamBinding] = field(default_factory=list)
    path_vars: frozenset[str] = field(default_factory=frozenset)


def _extract_path_vars(path: str) -> frozenset[str]:
    return frozenset(
        name for _, name, _, _ in Formatter().parse(path) if name
    )


def _classify_parameter(
    name: str,
    annotation: Any,
    path_vars: frozenset[str],
) -> _ParamBinding:
    # Explicit Annotated[T, Marker(...)] takes precedence.
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        inner_type = args[0]
        for meta in args[1:]:
            if isinstance(meta, _PARAM_KINDS):
                return _ParamBinding(
                    name=name, kind=type(meta), alias=meta.alias, annotation=inner_type,
                )
        annotation = inner_type  # fall through to inference
    # Inference fallback.
    if name in path_vars:
        kind: type[ParamMarker] = Path
    elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
        kind = Body
    else:
        kind = Query
    return _ParamBinding(name=name, kind=kind, alias=None, annotation=annotation)


def _build_spec(
    func: Callable[..., Any],
    method: Method,
    path: str,
    sign: Signer | type[Signer] | None,
    strict: bool,
) -> EndpointSpec:
    sig = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)
    path_vars = _extract_path_vars(path)

    bindings: list[_ParamBinding] = []
    seen_body = False
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise TypeError(
                f"Endpoint {func.__qualname__}: *args/**kwargs are not allowed",
            )
        annotation = hints.get(pname, param.annotation)
        if annotation is inspect.Parameter.empty:
            raise TypeError(
                f"Endpoint {func.__qualname__}: parameter '{pname}' must be annotated",
            )
        binding = _classify_parameter(pname, annotation, path_vars)
        if binding.kind is Body:
            if seen_body:
                raise TypeError(
                    f"Endpoint {func.__qualname__}: at most one Body parameter allowed",
                )
            seen_body = True
        bindings.append(binding)

    declared_path_params = {b.name for b in bindings if b.kind is Path}
    missing = path_vars - declared_path_params
    if missing:
        raise TypeError(
            f"Endpoint {func.__qualname__}: path variables {sorted(missing)} "
            "have no matching parameter",
        )

    return EndpointSpec(
        method=method,
        path=path,
        sign=sign,
        strict=strict,
        return_annotation=hints.get("return", Any),
        bindings=bindings,
        path_vars=path_vars,
    )


def _assemble(
    spec: EndpointSpec,
    bound_args: inspect.BoundArguments,
) -> PreparedRequest:
    path_values: dict[str, Any] = {}
    query: dict[str, str | int | float | bool] = {}
    headers: dict[str, str] = {}
    body: Any = None

    for binding in spec.bindings:
        if binding.name not in bound_args.arguments:
            continue
        value = bound_args.arguments[binding.name]
        if binding.kind is Path:
            path_values[binding.alias or binding.name] = value
        elif binding.kind is Query:
            if value is not None:
                query[binding.alias or binding.name] = value
        elif binding.kind is Header:
            if value is not None:
                headers[binding.alias or binding.name] = str(value)
        elif binding.kind is Body:
            body = value

    json_body: Any = None
    raw_data: bytes | str | None = None
    if isinstance(body, BaseModel):
        json_body = body.model_dump(mode="json")
    elif isinstance(body, (dict, list)):
        json_body = body
    elif isinstance(body, (bytes, str)):
        raw_data = body

    return PreparedRequest(
        method=spec.method,
        url=spec.path.format(**path_values),
        headers=headers,
        params=query,
        json_body=json_body,
        data=raw_data,
    )


def _parse_response(
    spec: EndpointSpec,
    raw: Any,
) -> Any:
    annotation = spec.return_annotation
    if annotation is None or annotation is type(None) or annotation is Any:
        return raw
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        try:
            return annotation.model_validate(raw)
        except ValidationError as exc:
            raise ResponseValidationError(raw_data=raw, validation_error=exc) from exc
    # For non-pydantic annotations (list[X], TypeAdapter etc.) fall back to TypeAdapter.
    from pydantic import TypeAdapter

    try:
        return TypeAdapter(annotation).validate_python(raw)
    except ValidationError as exc:
        raise ResponseValidationError(raw_data=raw, validation_error=exc) from exc


def endpoint(
    method: Method,
    path: str,
    *,
    sign: Signer | type[Signer] | None = None,
    strict: bool = True,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Decorate a Service method to drive it through the HTTP engine.

    The wrapped method's signature is preserved exactly (LSP-friendly). The
    method body is ignored — declare it as ``...``.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        spec = _build_spec(func, method, path, sign, strict)
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from .service import Service as _Service

            if not args or not isinstance(args[0], _Service):
                raise TypeError(
                    f"@endpoint must wrap a Service method (self missing): {func.__qualname__}",
                )
            self_obj = args[0]
            bound = sig.bind(self_obj, *args[1:], **kwargs)
            bound.apply_defaults()

            prepared = _assemble(spec, bound)

            chosen = spec.sign if spec.sign is not None else type(self_obj).signer
            signer = resolve_signer(chosen)
            try:
                prepared = signer.sign(prepared)
            except Exception as exc:
                raise SignError(str(exc)) from exc

            response = await self_obj.client.send(prepared)
            if response.status_code >= 400:
                try:
                    payload = response.json()
                except Exception:
                    payload = response.text
                raise ApiError(response.status_code, payload)

            try:
                payload = response.json()
            except Exception:
                payload = response.text

            if not strict and not isinstance(spec.return_annotation, type):
                return payload
            return _parse_response(spec, payload)

        return cast("Callable[P, Awaitable[R]]", wrapper)

    return decorator
