import httpx

from butler_bifrost import (
    ErrorEnvelope,
    HttpTransport,
    HttpTransportConfig,
    SpeakerIdentity,
    TextRequest,
    TextResponse,
)


def _client(handler):
    return httpx.Client(
        transport=httpx.MockTransport(handler)
    )


def test_http_transport_preserves_correlation():
    def handler(request: httpx.Request):
        body = request.read().decode()
        assert '"request_id":"req-1"' in body
        return httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "req-1",
                "response": "At your service.",
            },
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request"
        ),
        client=_client(handler),
    )

    result = transport.send_text(
        TextRequest(
            request_id="req-1",
            message="hello",
        )
    )

    assert result == TextResponse(
        request_id="req-1",
        response="At your service.",
    )


def test_http_transport_serializes_safe_speaker_metadata():
    def handler(request: httpx.Request):
        payload = __import__("json").loads(
            request.read()
        )
        assert payload["speaker"] == {
            "speaker_id": "unknown-1",
            "persistent": False,
            "language": "it",
        }
        return httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "req-2",
                "response": "Buongiorno.",
            },
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request"
        ),
        client=_client(handler),
    )

    result = transport.send_text(
        TextRequest(
            request_id="req-2",
            message="ciao",
            speaker=SpeakerIdentity(
                speaker_id="unknown-1",
                persistent=False,
                language="it",
            ),
        )
    )

    assert isinstance(result, TextResponse)


def test_http_transport_injects_optional_bearer_token():
    def handler(request: httpx.Request):
        assert (
            request.headers["Authorization"]
            == "Bearer secret"
        )
        return httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "req-3",
                "response": "ok",
            },
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request",
            token="secret",
        ),
        client=_client(handler),
    )

    assert isinstance(
        transport.send_text(
            TextRequest(
                request_id="req-3",
                message="hello",
            )
        ),
        TextResponse,
    )


def test_http_transport_preserves_structured_remote_error():
    def handler(_request: httpx.Request):
        return httpx.Response(
            403,
            json={
                "ok": False,
                "request_id": "req-4",
                "error": {
                    "code": "forbidden",
                    "message": "Request not allowed.",
                },
            },
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request"
        ),
        client=_client(handler),
    )

    result = transport.send_text(
        TextRequest(
            request_id="req-4",
            message="hello",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-4",
        code="forbidden",
        message="Request not allowed.",
    )


def test_http_transport_rejects_correlation_mismatch():
    def handler(_request: httpx.Request):
        return httpx.Response(
            200,
            json={
                "ok": True,
                "request_id": "wrong",
                "response": "ok",
            },
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request"
        ),
        client=_client(handler),
    )

    result = transport.send_text(
        TextRequest(
            request_id="req-5",
            message="hello",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-5",
        code="correlation_mismatch",
        message="Butler endpoint returned a mismatched request id.",
    )


def test_http_transport_maps_timeout_to_stable_error():
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout(
            "timeout",
            request=request,
        )

    transport = HttpTransport(
        HttpTransportConfig(
            endpoint="http://asgard.test/v1/request"
        ),
        client=_client(handler),
    )

    result = transport.send_text(
        TextRequest(
            request_id="req-6",
            message="hello",
        )
    )

    assert result == ErrorEnvelope(
        request_id="req-6",
        code="transport_unavailable",
        message="Bifröst transport could not reach the Butler endpoint.",
    )
