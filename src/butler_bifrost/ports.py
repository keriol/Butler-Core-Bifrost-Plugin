from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .pairing import DeviceAuthentication, PairingRequest, PairingResult

from .protocol import (
    ButlerDirectoryEntry,
    ErrorEnvelope,
    NodeManifest,
    TextRequest,
    TextResponse,
)


class MidgardIngressPort(Protocol):
    """Midgard-facing route used by the external Bifröst ingress."""

    async def route_text(
        self,
        request: TextRequest,
    ) -> TextResponse | ErrorEnvelope:
        ...

    async def list_butlers(self) -> tuple[ButlerDirectoryEntry, ...]:
        """Return the Butler directory projected by Midgard."""
        ...

    async def get_node_manifest(self) -> NodeManifest:
        """Return the safe node manifest projected by Midgard."""
        ...


class PairingRuntimePort(Protocol):
    """Runtime-owned pairing approval and credential issuer boundary."""

    async def request_pairing(
        self,
        request: "PairingRequest",
    ) -> "PairingResult":
        ...

    async def get_pairing(
        self,
        pairing_id: str,
    ) -> "PairingResult":
        ...


class DeviceCredentialAuthenticatorPort(Protocol):
    """Runtime-owned authentication boundary for device credentials."""

    async def authenticate_device(
        self,
        credential: str,
    ) -> "DeviceAuthentication":
        ...
