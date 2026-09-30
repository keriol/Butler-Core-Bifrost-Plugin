import pytest

from butler_bifrost import (
    BifrostIngress,
    ClientNotification,
    ClientNotificationKind,
    ErrorEnvelope,
    TextRequest,
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
async def test_ingress_passes_target_butler_metadata_to_midgard():
    midgard = FakeMidgard(
        TextResponse(
            request_id="req-1",
            response="Ready.",
            source_butler_name="Butler-B",
        )
    )
    ingress = BifrostIngress(midgard)

    request = TextRequest(
        request_id="req-1",
        message="hello",
        target_butler_name="Butler-B",
    )
    result = await ingress.handle_text(request)

    assert midgard.requests == [request]
    assert midgard.requests[0].target_butler_name == "Butler-B"
    assert result == TextResponse(
        request_id="req-1",
        response="Ready.",
        source_butler_name="Butler-B",
    )


@pytest.mark.asyncio
async def test_ingress_propagates_butler_unavailable_notification_unchanged():
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

    result = await BifrostIngress(midgard).handle_text(
        TextRequest(
            request_id="req-2",
            message="hello",
            target_butler_name="Missing",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-2",
        code="butler_not_found",
        message="The requested Butler could not be found.",
        notification=notification,
    )
    assert result.notification is notification


@pytest.mark.asyncio
async def test_ingress_rejects_correlation_mismatch():
    midgard = FakeMidgard(
        TextResponse(
            request_id="wrong",
            response="Ready.",
            source_butler_name="Butler-A",
        )
    )

    result = await BifrostIngress(midgard).handle_text(
        TextRequest(
            request_id="req-3",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-3",
        code="correlation_mismatch",
        message="The routing layer returned a mismatched request id.",
    )


@pytest.mark.asyncio
async def test_ingress_maps_midgard_exception_to_stable_error():
    class BrokenMidgard:
        async def route_text(self, request):
            raise RuntimeError("private detail")

    result = await BifrostIngress(BrokenMidgard()).handle_text(
        TextRequest(
            request_id="req-4",
            message="hello",
            target_butler_name="Butler-A",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-4",
        code="midgard_unavailable",
        message="Bifröst could not reach the routing layer.",
    )
    assert "private detail" not in result.message
