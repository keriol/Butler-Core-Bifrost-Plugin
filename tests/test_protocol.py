import pytest

from butler_bifrost import (
    PROTOCOL_VERSION,
    ButlerIdentity,
    ErrorEnvelope,
    Hello,
    TextRequest,
    TextResponse,
)


def test_hello_defaults_to_current_protocol_version():
    hello = Hello(request_id="req-1", client_id="interphone-1")
    assert hello.protocol_version == PROTOCOL_VERSION


def test_identity_preserves_safe_handshake_fields():
    identity = ButlerIdentity(
        request_id="req-1",
        butler_name="Wilfred",
        instance_id="demo",
        pairing_required=True,
    )
    assert identity.request_id == "req-1"
    assert identity.butler_name == "Wilfred"
    assert identity.instance_id == "demo"
    assert identity.pairing_required is True


def test_text_request_requires_non_blank_message():
    with pytest.raises(ValueError):
        TextRequest(request_id="req-1", message="   ")


def test_text_response_preserves_correlation():
    response = TextResponse(request_id="req-7", response="At your service.")
    assert response.request_id == "req-7"
    assert response.ok is True


def test_error_envelope_allows_missing_request_id():
    error = ErrorEnvelope(
        request_id=None,
        code="invalid_handshake",
        message="Handshake rejected.",
    )
    assert error.request_id is None
