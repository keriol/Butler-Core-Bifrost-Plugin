from __future__ import annotations

import pytest

from butler_bifrost import (
    BifrostIngress,
    ButlerDescriptor,
    ButlerDirectoryEntry,
    CallableDescriptor,
    CoreStackDescriptor,
    DependencyDescriptor,
    EntityDescriptor,
    NodeManifest,
    PluginDescriptor,
    ReadinessDescriptor,
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

    async def get_node_manifest(self):
        return NodeManifest(
            core=CoreStackDescriptor(
                version="1.2.3",
                plugins=(
                    PluginDescriptor(
                        name="routing-plugin",
                        version="0.4.0",
                        available=True,
                    ),
                ),
            ),
            butlers=(
                ButlerDescriptor(
                    canonical_name="Butler-A",
                    aliases=("A",),
                    description="Example Butler",
                    version="2.0.0",
                    available=True,
                    asgard_version="0.1.0",
                    entities=(
                        EntityDescriptor(
                            name="Example Entity",
                            methods=(
                                CallableDescriptor(
                                    name="inspect",
                                    readiness=ReadinessDescriptor(
                                        state="usable",
                                    ),
                                    dependencies=(
                                        DependencyDescriptor(
                                            name="shared-provider",
                                            version="3.0.0",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

    async def list_butlers(self):
        return (
            ButlerDirectoryEntry(
                canonical_name="Butler-A",
                aliases=("A", "Alpha"),
                available=True,
            ),
            ButlerDirectoryEntry(
                canonical_name="Butler-B",
                aliases=(),
                available=False,
            ),
        )


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
async def test_http_adapter_allows_targetless_core_request():
    midgard = FakeMidgard(
        TextResponse(
            request_id="req-core",
            response="Done.",
            source_butler_name=None,
        )
    )
    adapter = HttpIngressAdapter(BifrostIngress(midgard))

    result = await adapter.handle_json({
        "request_id": "req-core",
        "message": "run provider capability",
    })

    assert result.status_code == 200
    assert result.body == {
        "ok": True,
        "request_id": "req-core",
        "source_butler_name": None,
        "response": "Done.",
    }
    assert midgard.requests[0].target_butler_name is None


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


@pytest.mark.asyncio
async def test_http_adapter_serializes_read_only_butler_directory():
    adapter = HttpIngressAdapter(BifrostIngress(FakeMidgard(None)))

    result = await adapter.handle_butlers()

    assert result.status_code == 200
    assert result.body == {
        "ok": True,
        "butlers": [
            {
                "canonical_name": "Butler-A",
                "aliases": ["A", "Alpha"],
                "available": True,
            },
            {
                "canonical_name": "Butler-B",
                "aliases": [],
                "available": False,
            },
        ],
    }



@pytest.mark.asyncio
async def test_http_adapter_serializes_composed_node_manifest():
    adapter = HttpIngressAdapter(
        BifrostIngress(
            FakeMidgard(None),
            bifrost_version="0.9.0",
        )
    )

    result = await adapter.handle_manifest()

    assert result.status_code == 200
    assert result.body["protocol_version"] == 1
    assert result.body["bifrost"] == {"version": "0.9.0"}
    assert result.body["core"]["version"] == "1.2.3"
    assert result.body["core"]["plugins"][0]["name"] == "routing-plugin"

    butler = result.body["butlers"][0]
    assert butler["canonical_name"] == "Butler-A"
    assert butler["asgard"] == {"version": "0.1.0"}
    assert butler["entities"][0]["methods"][0]["name"] == "inspect"
    assert butler["entities"][0]["methods"][0]["dependencies"] == [
        {
            "name": "shared-provider",
            "version": "3.0.0",
        }
    ]
