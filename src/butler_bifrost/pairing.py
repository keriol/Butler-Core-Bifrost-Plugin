from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .ports import DeviceCredentialAuthenticatorPort, PairingRuntimePort
from .protocol import ErrorEnvelope


def _required(value: str, field_name: str) -> str:
    clean = str(value or "").strip()
    if not clean:
        raise ValueError(f"{field_name} must not be blank.")
    return clean


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    clean = str(value).strip()
    return clean or None


class PairingState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


class DeviceCredentialState(str, Enum):
    AUTHENTICATED = "authenticated"
    INVALID = "invalid"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class PairingRequest:
    request_id: str
    client_id: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "request_id",
            _required(self.request_id, "request_id"),
        )
        object.__setattr__(
            self,
            "client_id",
            _required(self.client_id, "client_id"),
        )
        object.__setattr__(
            self,
            "display_name",
            _optional(self.display_name),
        )


@dataclass(frozen=True, slots=True)
class PairingResult:
    request_id: str
    pairing_id: str
    state: PairingState
    credential: str | None = None
    credential_id: str | None = None
    reason_code: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "request_id",
            _required(self.request_id, "request_id"),
        )
        object.__setattr__(
            self,
            "pairing_id",
            _required(self.pairing_id, "pairing_id"),
        )
        object.__setattr__(
            self,
            "credential",
            _optional(self.credential),
        )
        object.__setattr__(
            self,
            "credential_id",
            _optional(self.credential_id),
        )
        object.__setattr__(
            self,
            "reason_code",
            _optional(self.reason_code),
        )

        if self.state is PairingState.APPROVED:
            if self.credential is None or self.credential_id is None:
                raise ValueError(
                    "approved pairing requires credential and credential_id."
                )
        elif self.credential is not None:
            raise ValueError(
                "credential must only be present for approved pairing."
            )


@dataclass(frozen=True, slots=True)
class DeviceAuthentication:
    state: DeviceCredentialState
    client_id: str | None = None
    credential_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "client_id",
            _optional(self.client_id),
        )
        object.__setattr__(
            self,
            "credential_id",
            _optional(self.credential_id),
        )

        if self.state is DeviceCredentialState.AUTHENTICATED:
            if self.client_id is None or self.credential_id is None:
                raise ValueError(
                    "authenticated credential requires client_id and credential_id."
                )


@dataclass(frozen=True, slots=True)
class PairingHttpResult:
    status_code: int
    body: dict[str, Any]


class BifrostPairing:
    """Pairing boundary backed by runtime-owned policy and credentials."""

    def __init__(
        self,
        runtime: PairingRuntimePort,
        authenticator: DeviceCredentialAuthenticatorPort,
    ) -> None:
        self._runtime = runtime
        self._authenticator = authenticator

    async def request_pairing(
        self,
        request: PairingRequest,
    ) -> PairingResult | ErrorEnvelope:
        try:
            result = await self._runtime.request_pairing(request)
        except Exception:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="pairing_unavailable",
                message="Bifröst could not reach the pairing runtime.",
            )

        if result.request_id != request.request_id:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="correlation_mismatch",
                message="The pairing runtime returned a mismatched request id.",
            )

        return result

    async def get_pairing(
        self,
        pairing_id: str,
    ) -> PairingResult | ErrorEnvelope:
        clean_pairing_id = _required(pairing_id, "pairing_id")
        try:
            return await self._runtime.get_pairing(clean_pairing_id)
        except Exception:
            return ErrorEnvelope(
                request_id=None,
                code="pairing_unavailable",
                message="Bifröst could not reach the pairing runtime.",
            )

    async def authenticate_device(
        self,
        credential: str,
    ) -> DeviceAuthentication | ErrorEnvelope:
        clean = str(credential or "").strip()
        if not clean:
            return DeviceAuthentication(
                state=DeviceCredentialState.INVALID,
            )

        try:
            return await self._authenticator.authenticate_device(clean)
        except Exception:
            return ErrorEnvelope(
                request_id=None,
                code="authentication_unavailable",
                message="Bifröst could not validate the device credential.",
            )


class PairingHttpAdapter:
    """Framework-neutral HTTP payload adapter for pairing enrollment."""

    def __init__(self, pairing: BifrostPairing) -> None:
        self._pairing = pairing

    async def handle_create(
        self,
        payload: Mapping[str, Any] | Any,
    ) -> PairingHttpResult:
        parsed = self._parse_request(payload)
        if isinstance(parsed, ErrorEnvelope):
            return self._serialize_error(parsed, status_code=400)

        result = await self._pairing.request_pairing(parsed)
        if isinstance(result, ErrorEnvelope):
            return self._serialize_error(
                result,
                status_code=self._status_for_error(result.code),
            )

        return self._serialize_pairing(result)

    async def handle_status(
        self,
        pairing_id: str,
    ) -> PairingHttpResult:
        try:
            clean_pairing_id = _required(pairing_id, "pairing_id")
        except ValueError:
            return self._serialize_error(
                ErrorEnvelope(
                    request_id=None,
                    code="invalid_request",
                    message="pairing_id must not be blank.",
                ),
                status_code=400,
            )

        result = await self._pairing.get_pairing(clean_pairing_id)
        if isinstance(result, ErrorEnvelope):
            return self._serialize_error(
                result,
                status_code=self._status_for_error(result.code),
            )

        return self._serialize_pairing(result)

    @staticmethod
    def _parse_request(
        payload: Mapping[str, Any] | Any,
    ) -> PairingRequest | ErrorEnvelope:
        if not isinstance(payload, Mapping):
            return ErrorEnvelope(
                request_id=None,
                code="invalid_request",
                message="Request body must be a JSON object.",
            )

        request_id = payload.get("request_id")
        client_id = payload.get("client_id")
        display_name = payload.get("display_name")

        if not isinstance(request_id, str) or not request_id.strip():
            return ErrorEnvelope(
                request_id=None,
                code="invalid_request",
                message="request_id must not be blank.",
            )
        if not isinstance(client_id, str) or not client_id.strip():
            return ErrorEnvelope(
                request_id=request_id.strip(),
                code="invalid_request",
                message="client_id must not be blank.",
            )
        if display_name is not None and not isinstance(display_name, str):
            return ErrorEnvelope(
                request_id=request_id.strip(),
                code="invalid_request",
                message="display_name must be text when supplied.",
            )

        try:
            return PairingRequest(
                request_id=request_id,
                client_id=client_id,
                display_name=display_name,
            )
        except ValueError:
            return ErrorEnvelope(
                request_id=request_id.strip(),
                code="invalid_request",
                message="Pairing request is invalid.",
            )

    @staticmethod
    def _serialize_pairing(result: PairingResult) -> PairingHttpResult:
        body: dict[str, Any] = {
            "ok": result.state
            in {
                PairingState.PENDING,
                PairingState.APPROVED,
            },
            "request_id": result.request_id,
            "pairing_id": result.pairing_id,
            "state": result.state.value,
        }

        if result.reason_code is not None:
            body["reason_code"] = result.reason_code

        if result.state is PairingState.APPROVED:
            body["credential"] = {
                "type": "bearer",
                "id": result.credential_id,
                "token": result.credential,
            }

        return PairingHttpResult(
            status_code={
                PairingState.PENDING: 202,
                PairingState.APPROVED: 200,
                PairingState.REJECTED: 403,
                PairingState.REVOKED: 410,
            }[result.state],
            body=body,
        )

    @staticmethod
    def _status_for_error(code: str) -> int:
        if code == "invalid_request":
            return 400
        if code == "correlation_mismatch":
            return 409
        if code in {
            "pairing_unavailable",
            "authentication_unavailable",
        }:
            return 503
        return 500

    @staticmethod
    def _serialize_error(
        error: ErrorEnvelope,
        *,
        status_code: int,
    ) -> PairingHttpResult:
        return PairingHttpResult(
            status_code=status_code,
            body={
                "ok": False,
                "request_id": error.request_id,
                "error": {
                    "code": error.code,
                    "message": error.message,
                },
            },
        )
