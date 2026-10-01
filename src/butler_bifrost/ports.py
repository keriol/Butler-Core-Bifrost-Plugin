from __future__ import annotations

from typing import Protocol

from .protocol import (
    ButlerDirectoryEntry,
    ErrorEnvelope,
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
