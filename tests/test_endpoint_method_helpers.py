"""endpoint.get/post/put/delete/patch shortcut methods."""

from __future__ import annotations

import pytest

from tagedo.core import Service, endpoint
from tagedo.core.endpoint import EndpointSpec  # noqa: F401  (used for instance check)

from ._helpers import MockClient


class _Svc(Service):
    @endpoint.get("/g")
    async def g(self) -> dict[str, object]: ...

    @endpoint.post("/p")
    async def p(self) -> dict[str, object]: ...

    @endpoint.put("/u")
    async def u(self) -> dict[str, object]: ...

    @endpoint.delete("/d")
    async def d(self) -> dict[str, object]: ...

    @endpoint.patch("/pa")
    async def pa(self) -> dict[str, object]: ...


@pytest.mark.parametrize(
    ("method_name", "expected_method", "expected_url"),
    [
        ("g", "GET", "/g"),
        ("p", "POST", "/p"),
        ("u", "PUT", "/u"),
        ("d", "DELETE", "/d"),
        ("pa", "PATCH", "/pa"),
    ],
)
async def test_verb_shortcuts_set_correct_method(
    method_name: str, expected_method: str, expected_url: str,
) -> None:
    client = MockClient()
    svc = _Svc(client)
    await getattr(svc, method_name)()
    assert client.sent[0].method == expected_method
    assert client.sent[0].url == expected_url


async def test_legacy_two_arg_form_still_works() -> None:
    class Legacy(Service):
        @endpoint("GET", "/old")
        async def call(self) -> dict[str, object]: ...

    client = MockClient()
    svc = Legacy(client)
    await svc.call()
    assert client.sent[0].method == "GET"
    assert client.sent[0].url == "/old"
