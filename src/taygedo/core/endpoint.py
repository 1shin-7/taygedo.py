"""Endpoint decorator and runtime engine.

Turns a ``Service`` method declaration into a working HTTP call. Method body
is ``...`` — the decorator inspects the signature once at class-definition
time and uses it to assemble + sign + dispatch + parse at call time.

Parameter inference (per param besides ``self``):
  * ``Annotated[T, Path()|Query()|Header()|Body()]`` → that role explicitly.
  * Else: name in path template → Path; BaseModel subclass → Body; else Query.

Header merging order at call time (later wins): ``service.default_headers``
→ endpoint-param headers → ``client._auth_provider`` (Authorization).

401 retry: on HTTP 401 the engine awaits ``service.on_unauthorized()`` and,
if it returns ``True``, retries once.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import partial, wraps
from string import Formatter
from typing import (
    Annotated,
    Any,
    Literal,
    Union,
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
    form: bool = False


@dataclass(slots=True)
class EndpointSpec:
    """Compiled metadata for an endpoint, computed once at decoration time."""

    method: Method
    path: str
    sign: Any  # Signer | type[Signer] | Callable[[Service], Signer] | None
    return_annotation: Any
    bindings: list[_ParamBinding] = field(default_factory=list)
    path_vars: frozenset[str] = field(default_factory=frozenset)


def _extract_path_vars(path: str) -> frozenset[str]:
    return frozenset(
        name for _, name, _, _ in Formatter().parse(path) if name
    )


def _unwrap_optional_around_annotated(annotation: Any) -> Any:
    """Strip an outer ``Optional[...]`` so inner ``Annotated`` markers surface.

    Python 3.10's ``get_type_hints`` wraps ``Annotated[T, Marker] = None`` into
    ``Optional[Annotated[T, Marker]]``; 3.11+ keeps the ``Annotated`` at the
    top level. Normalise both to the 3.11+ shape.
    """
    import types

    origin = get_origin(annotation)
    is_union = origin is Union or origin is types.UnionType
    if not is_union:
        return annotation
    args = get_args(annotation)
    non_none = [a for a in args if a is not type(None)]
    if len(non_none) == 1 and get_origin(non_none[0]) is Annotated:
        return non_none[0]
    return annotation


def _classify_parameter(
    name: str,
    annotation: Any,
    path_vars: frozenset[str],
) -> _ParamBinding:
    annotation = _unwrap_optional_around_annotated(annotation)
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        inner_type = args[0]
        for meta in args[1:]:
            if isinstance(meta, _PARAM_KINDS):
                form = bool(getattr(meta, "form", False))
                return _ParamBinding(
                    name=name, kind=type(meta), alias=meta.alias,
                    annotation=inner_type, form=form,
                )
        annotation = inner_type
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
    sign: Any,
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
        return_annotation=hints.get("return", Any),
        bindings=bindings,
        path_vars=path_vars,
    )


def _assemble(
    spec: EndpointSpec,
    bound_args: inspect.BoundArguments,
    service_default_headers: dict[str, str],
) -> PreparedRequest:
    path_values: dict[str, Any] = {}
    query: dict[str, str | int | float | bool] = {}
    headers: dict[str, str] = dict(service_default_headers)
    body: Any = None
    body_form = False

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
            body_form = binding.form

    json_body: Any = None
    raw_data: bytes | str | None = None
    form = False
    if body is not None and body_form:
        # Form-urlencoded: project the body into params (where Signers can
        # mutate it) and let BaseClient.send urlencode at transport time.
        if isinstance(body, BaseModel):
            form_dict = body.model_dump(mode="json", by_alias=True, exclude_none=True)
        elif isinstance(body, dict):
            form_dict = body
        else:
            raise TypeError(
                f"Body(form=True) requires a BaseModel or dict, got {type(body).__name__}",
            )
        for k, v in form_dict.items():
            query[k] = v if isinstance(v, (str, int, float, bool)) else str(v)
        form = True
    elif isinstance(body, BaseModel):
        json_body = body.model_dump(mode="json", by_alias=True, exclude_none=True)
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
        form=form,
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
    from pydantic import TypeAdapter

    try:
        return TypeAdapter(annotation).validate_python(raw)
    except ValidationError as exc:
        raise ResponseValidationError(raw_data=raw, validation_error=exc) from exc


def _resolve_endpoint_signer(spec_sign: Any, fallback: Any, service: Any) -> Signer:
    """Pick the Signer for this call.

    Accepts:
      * Signer instance / Signer subclass / None
      * Factory: ``Callable[[Service], Signer]`` — invoked with the service
    """
    chosen = spec_sign if spec_sign is not None else fallback
    if chosen is None:
        return resolve_signer(None)
    # Distinguish factories from Signer instances/classes:
    #  - Signer instances expose `sign`
    #  - Signer classes are types
    if not isinstance(chosen, type) and not hasattr(chosen, "sign") and callable(chosen):
        chosen = chosen(service)
    return resolve_signer(chosen)


def _make_decorator(
    method: Method,
) -> Callable[..., Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]]:
    def deco(
        path: str,
        *,
        sign: Any = None,
    ) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
        return _endpoint_impl(method, path, sign=sign)

    return deco


def _endpoint_impl(
    method: Method,
    path: str,
    *,
    sign: Any = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        spec = _build_spec(func, method, path, sign)
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

            service_headers = getattr(type(self_obj), "default_headers", {}) or {}
            prepared = _assemble(spec, bound, service_headers)

            signer = _resolve_endpoint_signer(
                spec.sign, type(self_obj).signer, self_obj,
            )
            try:
                signed = signer.sign(prepared)
            except Exception as exc:
                raise SignError(str(exc)) from exc

            response = await self_obj.client.send(signed, service=self_obj)

            if response.status_code == 401:
                refreshed = await self_obj.on_unauthorized()
                if refreshed:
                    # Re-assemble + re-sign so a freshly-rotated session is
                    # picked up by both the signer and the auth provider.
                    prepared_retry = _assemble(spec, bound, service_headers)
                    try:
                        signed_retry = signer.sign(prepared_retry)
                    except Exception as exc:
                        raise SignError(str(exc)) from exc
                    response = await self_obj.client.send(signed_retry, service=self_obj)

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

            return _parse_response(spec, payload)

        return cast("Callable[P, Awaitable[R]]", wrapper)

    return decorator


class _EndpointDecoratorFactory:
    """Callable façade exposing both the legacy two-arg form and verb shortcuts.

    ``endpoint("GET", "/path", sign=...)`` is preserved for completeness;
    ``endpoint.get("/path")`` / ``.post`` / ``.put`` / ``.delete`` / ``.patch``
    are the idiomatic forms.
    """

    def __call__(
        self,
        method: Method,
        path: str,
        *,
        sign: Any = None,
    ) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
        return _endpoint_impl(method, path, sign=sign)

    get = staticmethod(partial(_endpoint_impl, "GET"))
    post = staticmethod(partial(_endpoint_impl, "POST"))
    put = staticmethod(partial(_endpoint_impl, "PUT"))
    delete = staticmethod(partial(_endpoint_impl, "DELETE"))
    patch = staticmethod(partial(_endpoint_impl, "PATCH"))


endpoint = _EndpointDecoratorFactory()
