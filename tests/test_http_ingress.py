from __future__ import annotations

import pytest

from butler_bifrost import (
    BifrostIngress,
    ClientNotification,
    ClientNotificationKind,
    ErrorEnvelope,
    HttpIngressAdapter,
    TextResponse,
)


class FakeMidgard:
    def __init__(self, result):
        self.result = result
        self.requests = []

    async def route_text(self, request):
        self.requests.append(request)
        return self.result


@pytest.mark.asyncio
async def test_http_adapter_parses_and_serializes_success():
    midgard = FakeMidgard(
        TextResponse(
            request_id="req-1",
            response="Ready.",
            source_butler_name="Butler-A",
        )
    )
    adapter = HttpIngressAdapter(BifrostIngress(midgard))

    result = await adapter.handle_json({
        "request_id": "req-1",
        "target_butler_name": "Butler-A",
        "message": "hello",
        "speaker": {
            "speaker_id": "user-1",
            "persistent": False,
            "language": "it",
        },
    })

    assert result.status_code == 200
    assert result.body == {
        "ok": True,
        "request_id": "req-1",
        "source_butler_name": "Butler-A",
        "response": "Ready.",
    }
    assert midgard.requests[0].target_butler_name == "Butler-A"
    assert midgard.requests[0].speaker.speaker_id == "user-1"


@pytest.mark.asyncio
async def test_http_adapter_preserves_neutral_notification():
    notification = ClientNotification(
        kind=ClientNotificationKind.BUTLER_UNAVAILABLE,
        documentation_url="https://docs.example.test/doctor",
    )
    midgard = FakeMidgard(
        ErrorEnvelope(
            request_id="req-2",
            code="butler_not_found",
            message="The requested Butler could not be found.",
            notification=notification,
        )
    )
    adapter = HttpIngressAdapter(BifrostIngress(midgard))

    result = await adapter.handle_json({
        "request_id": "req-2",
        "target_butler_name": "Missing",
        "message": "hello",
    })

    assert result.status_code == 404
    assert result.body["notification"] == {
        "kind": "butler_unavailable",
        "presentation": "system_neutral",
        "documentation_url": "https://docs.example.test/doctor",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("payload", "expected_request_id"),
    [
        ([], None),
        ({"message": "hello", "target_butler_name": "Butler-A"}, None),
        ({"request_id": "req-3", "target_butler_name": "Butler-A"}, "req-3"),
        ({"request_id": "req-4", "message": "hello"}, "req-4"),
        ({
            "request_id": "req-5",
            "message": "hello",
            "target_butler_name": "Butler-A",
            "speaker": "wrong",
        }, "req-5"),
    ],
)
async def test_http_adapter_returns_stable_validation_error(
    payload,
    expected_request_id,
):
    adapter = HttpIngressAdapter(
        BifrostIngress(FakeMidgard(None))
    )

    result = await adapter.handle_json(payload)

    assert result.status_code == 400
    assert result.body["ok"] is False
    assert result.body["request_id"] == expected_request_id
    assert result.body["error"]["code"] == "invalid_request"


@pytest.mark.asyncio
async def test_http_adapter_maps_unavailable_to_503():
    adapter = HttpIngressAdapter(
        BifrostIngress(
            FakeMidgard(
                ErrorEnvelope(
                    request_id="req-6",
                    code="target_unavailable",
                    message="Unavailable.",
                )
            )
        )
    )

    result = await adapter.handle_json({
        "request_id": "req-6",
        "target_butler_name": "Butler-A",
        "message": "hello",
    })

    assert result.status_code == 503
