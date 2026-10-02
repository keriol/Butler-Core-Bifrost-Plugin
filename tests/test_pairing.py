from __future__ import annotations

import pytest

from butler_bifrost import (
    BifrostPairing,
    DeviceAuthentication,
    DeviceCredentialState,
    PairingHttpAdapter,
    PairingRequest,
    PairingResult,
    PairingState,
)


class FakePairingRuntime:
    def __init__(self) -> None:
        self.results: dict[str, PairingResult] = {}

    async def request_pairing(
        self,
        request: PairingRequest,
    ) -> PairingResult:
        result = PairingResult(
            request_id=request.request_id,
            pairing_id=f"pair-{request.client_id}",
            state=PairingState.PENDING,
        )
        self.results[result.pairing_id] = result
        return result

    async def get_pairing(
        self,
        pairing_id: str,
    ) -> PairingResult:
        return self.results[pairing_id]


class FakeCredentialAuthenticator:
    def __init__(self) -> None:
        self.credentials = {
            "token-a": DeviceAuthentication(
                state=DeviceCredentialState.AUTHENTICATED,
                client_id="client-a",
                credential_id="cred-a",
            ),
            "token-b": DeviceAuthentication(
                state=DeviceCredentialState.AUTHENTICATED,
                client_id="client-b",
                credential_id="cred-b",
            ),
        }

    async def authenticate_device(
        self,
        credential: str,
    ) -> DeviceAuthentication:
        return self.credentials.get(
            credential,
            DeviceAuthentication(
                state=DeviceCredentialState.INVALID,
            ),
        )


def build_pairing():
    runtime = FakePairingRuntime()
    authenticator = FakeCredentialAuthenticator()
    pairing = BifrostPairing(runtime, authenticator)
    return runtime, authenticator, pairing


@pytest.mark.asyncio
async def test_pairing_create_returns_pending_without_credential():
    runtime, _, pairing = build_pairing()
    adapter = PairingHttpAdapter(pairing)

    result = await adapter.handle_create({
        "request_id": "req-1",
        "client_id": "interphone-1",
        "display_name": "Example phone",
    })

    assert result.status_code == 202
    assert result.body == {
        "ok": True,
        "request_id": "req-1",
        "pairing_id": "pair-interphone-1",
        "state": "pending",
    }
    assert runtime.results["pair-interphone-1"].credential is None


@pytest.mark.asyncio
async def test_approved_pairing_returns_only_its_device_credential():
    runtime, _, pairing = build_pairing()
    adapter = PairingHttpAdapter(pairing)

    runtime.results["pair-interphone-1"] = PairingResult(
        request_id="req-1",
        pairing_id="pair-interphone-1",
        state=PairingState.APPROVED,
        credential="token-a",
        credential_id="cred-a",
    )

    result = await adapter.handle_status("pair-interphone-1")

    assert result.status_code == 200
    assert result.body["state"] == "approved"
    assert result.body["credential"] == {
        "type": "bearer",
        "id": "cred-a",
        "token": "token-a",
    }
    assert "token-b" not in repr(result.body)


@pytest.mark.asyncio
async def test_rejected_pairing_never_returns_credential():
    runtime, _, pairing = build_pairing()
    adapter = PairingHttpAdapter(pairing)

    runtime.results["pair-interphone-1"] = PairingResult(
        request_id="req-1",
        pairing_id="pair-interphone-1",
        state=PairingState.REJECTED,
        reason_code="approval_denied",
    )

    result = await adapter.handle_status("pair-interphone-1")

    assert result.status_code == 403
    assert result.body["ok"] is False
    assert result.body["state"] == "rejected"
    assert "credential" not in result.body


@pytest.mark.asyncio
async def test_revoked_pairing_never_returns_credential():
    runtime, _, pairing = build_pairing()
    adapter = PairingHttpAdapter(pairing)

    runtime.results["pair-interphone-1"] = PairingResult(
        request_id="req-1",
        pairing_id="pair-interphone-1",
        state=PairingState.REVOKED,
        reason_code="credential_revoked",
    )

    result = await adapter.handle_status("pair-interphone-1")

    assert result.status_code == 410
    assert result.body["ok"] is False
    assert result.body["state"] == "revoked"
    assert "credential" not in result.body


@pytest.mark.asyncio
async def test_device_credentials_can_be_revoked_independently():
    _, authenticator, pairing = build_pairing()

    before_a = await pairing.authenticate_device("token-a")
    before_b = await pairing.authenticate_device("token-b")

    assert before_a.state is DeviceCredentialState.AUTHENTICATED
    assert before_b.state is DeviceCredentialState.AUTHENTICATED

    authenticator.credentials["token-a"] = DeviceAuthentication(
        state=DeviceCredentialState.REVOKED,
        credential_id="cred-a",
    )

    after_a = await pairing.authenticate_device("token-a")
    after_b = await pairing.authenticate_device("token-b")

    assert after_a.state is DeviceCredentialState.REVOKED
    assert after_b.state is DeviceCredentialState.AUTHENTICATED
    assert after_b.credential_id == "cred-b"


@pytest.mark.asyncio
async def test_blank_device_credential_is_invalid_without_runtime_call():
    _, _, pairing = build_pairing()

    result = await pairing.authenticate_device("   ")

    assert result == DeviceAuthentication(
        state=DeviceCredentialState.INVALID,
    )


def test_approved_pairing_requires_device_credential():
    with pytest.raises(ValueError):
        PairingResult(
            request_id="req-1",
            pairing_id="pair-1",
            state=PairingState.APPROVED,
        )


def test_pending_pairing_cannot_leak_device_credential():
    with pytest.raises(ValueError):
        PairingResult(
            request_id="req-1",
            pairing_id="pair-1",
            state=PairingState.PENDING,
            credential="must-not-leak",
        )
