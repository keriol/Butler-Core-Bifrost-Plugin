import json

from butler_bifrost import ErrorEnvelope, TextResponse
import butler_bifrost.probe as probe


class _FakeTransport:
    result = TextResponse(
        request_id="req-1",
        response="At your service.",
    )
    captured_request = None
    captured_config = None

    def __init__(self, config):
        type(self).captured_config = config

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return None

    def send_text(self, request):
        type(self).captured_request = request
        return type(self).result


def test_probe_uses_real_contract_shapes(monkeypatch, capsys):
    monkeypatch.setattr(probe, "HttpTransport", _FakeTransport)

    rc = probe.main([
        "--endpoint",
        "http://asgard.test/asgard/v1/request",
        "--token",
        "secret",
        "--message",
        "hello",
        "--request-id",
        "req-1",
        "--speaker-id",
        "unknown-1",
        "--language",
        "it",
    ])

    payload = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert payload == {
        "ok": True,
        "request_id": "req-1",
        "response": "At your service.",
    }
    assert _FakeTransport.captured_request.speaker.speaker_id == "unknown-1"
    assert _FakeTransport.captured_request.speaker.persistent is False
    assert _FakeTransport.captured_config.token == "secret"


def test_probe_returns_structured_transport_error(monkeypatch, capsys):
    monkeypatch.setattr(probe, "HttpTransport", _FakeTransport)
    _FakeTransport.result = ErrorEnvelope(
        request_id="req-2",
        code="transport_unavailable",
        message="Bifröst transport could not reach the Butler endpoint.",
    )

    rc = probe.main([
        "--endpoint",
        "http://asgard.test/asgard/v1/request",
        "--message",
        "hello",
        "--request-id",
        "req-2",
    ])

    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["ok"] is False
    assert payload["error"]["code"] == "transport_unavailable"


def test_probe_never_echoes_token_on_internal_failure(monkeypatch, capsys):
    class ExplodingTransport:
        def __init__(self, config):
            assert config.token == "super-secret-token"

        def __enter__(self):
            raise RuntimeError("super-secret-token")

        def __exit__(self, *_exc):
            return None

    monkeypatch.setattr(probe, "HttpTransport", ExplodingTransport)

    rc = probe.main([
        "--endpoint",
        "http://asgard.test/asgard/v1/request",
        "--token",
        "super-secret-token",
        "--message",
        "hello",
        "--request-id",
        "req-3",
    ])

    output = capsys.readouterr().out

    assert rc == 2
    assert "super-secret-token" not in output
    assert json.loads(output)["error"]["code"] == "probe_failure"
