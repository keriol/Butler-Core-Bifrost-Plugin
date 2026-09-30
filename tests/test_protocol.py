import pytest

from butler_bifrost import (
    PROTOCOL_VERSION,
    ButlerIdentity,
    ClientNotification,
    ClientNotificationKind,
    ClientNotificationPresentation,
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
        butler_name="Butler-A",
        instance_id="demo",
        pairing_required=True,
    )
    assert identity.request_id == "req-1"
    assert identity.butler_name == "Butler-A"
    assert identity.instance_id == "demo"
    assert identity.pairing_required is True


def test_text_request_requires_non_blank_message():
    with pytest.raises(ValueError):
        TextRequest(request_id="req-1", message="   ")


def test_text_request_carries_target_butler_name():
    request = TextRequest(
        request_id="req-2",
        message="hello",
        target_butler_name="  Butler-A  ",
    )
    assert request.target_butler_name == "Butler-A"


def test_text_response_preserves_source_butler_identity():
    response = TextResponse(
        request_id="req-7",
        response="At your service.",
        source_butler_name="Butler-A",
    )
    assert response.request_id == "req-7"
    assert response.source_butler_name == "Butler-A"
    assert response.ok is True


def test_error_envelope_allows_neutral_client_notification():
    notification = ClientNotification(
        kind=ClientNotificationKind.BUTLER_UNAVAILABLE,
        presentation=ClientNotificationPresentation.SYSTEM_NEUTRAL,
        documentation_url=" https://docs.example.test/doctor ",
    )
    error = ErrorEnvelope(
        request_id=None,
        code="butler_not_found",
        message="The requested Butler could not be found.",
        notification=notification,
    )
    assert error.request_id is None
    assert error.notification is not None
    assert error.notification.documentation_url == "https://docs.example.test/doctor"
