from __future__ import annotations

from collections.abc import Callable, Coroutine
from functools import wraps
from inspect import iscoroutine, iscoroutinefunction
from typing import Any, ParamSpec, Protocol, TypeVar, cast, overload

from pydantic import BaseModel, ValidationError

P = ParamSpec("P")
ModelT = TypeVar("ModelT", bound=BaseModel)

type RawDict = dict[str, object]
type ParsedDict[M: BaseModel] = M | RawDict


class _ParseWithModelDecorator(Protocol[ModelT]):
    @overload
    def __call__(self, func: Callable[P, RawDict]) -> Callable[P, ParsedDict[ModelT]]:
        ...

    @overload
    def __call__(
        self,
        func: Callable[P, Coroutine[Any, Any, RawDict]],
    ) -> Callable[P, Coroutine[Any, Any, ParsedDict[ModelT]]]:
        ...


def _parse_dict(model: type[ModelT], data: RawDict) -> ParsedDict[ModelT]:
    try:
        return model.model_validate(data)
    except ValidationError:
        return data


def parse_with_model(model: type[ModelT]) -> _ParseWithModelDecorator[ModelT]:
    """Validate function payloads with a pydantic model.

    The decorated function must return a dict.
    Valid payloads are converted into model instances; invalid payloads are
    returned as original dict data.
    """

    @overload
    def decorator(func: Callable[P, RawDict]) -> Callable[P, ParsedDict[ModelT]]:
        ...

    @overload
    def decorator(
        func: Callable[P, Coroutine[Any, Any, RawDict]],
    ) -> Callable[P, Coroutine[Any, Any, ParsedDict[ModelT]]]:
        ...

    def decorator(
        func: Callable[P, RawDict]
        | Callable[P, Coroutine[Any, Any, RawDict]],
    ) -> (
        Callable[P, ParsedDict[ModelT]]
        | Callable[P, Coroutine[Any, Any, ParsedDict[ModelT]]]
    ):
        if iscoroutinefunction(func):
            async_func = cast(Callable[P, Coroutine[Any, Any, RawDict]], func)

            async def async_wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> ParsedDict[ModelT]:
                result = async_func(*args, **kwargs)
                if iscoroutine(result):
                    payload_obj = await result
                else:
                    payload_obj = result
                if not isinstance(payload_obj, dict):
                    raise TypeError("Decorated async function must return a dict payload.")
                payload = cast(RawDict, payload_obj)
                return _parse_dict(model, payload)

            return cast(
                Callable[P, Coroutine[Any, Any, ParsedDict[ModelT]]],
                wraps(async_func)(async_wrapper),
            )

        sync_func = cast(Callable[P, RawDict], func)

        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> ParsedDict[ModelT]:
            result = sync_func(*args, **kwargs)
            if iscoroutine(result):
                result.close()
                message = (
                    f"Function '{sync_func.__qualname__}' returned a coroutine in sync mode; "
                    "declare it as async."
                )
                raise TypeError(message)
            if not isinstance(result, dict):
                raise TypeError("Decorated sync function must return a dict payload.")
            payload = cast(RawDict, result)
            return _parse_dict(model, payload)

        return cast(Callable[P, ParsedDict[ModelT]], wraps(sync_func)(sync_wrapper))

    return cast(_ParseWithModelDecorator[ModelT], decorator)
