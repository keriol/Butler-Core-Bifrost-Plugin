from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .ports import MidgardIngressPort
from .protocol import (
    BifrostNodeManifest,
    ButlerDirectoryEntry,
    ErrorEnvelope,
    TextRequest,
    TextResponse,
)


class BifrostIngress:
    """External/client ingress that delegates Butler routing to Midgard."""

    def __init__(
        self,
        midgard: MidgardIngressPort,
        *,
        bifrost_version: str | None = None,
    ) -> None:
        self._midgard = midgard
        self._bifrost_version = (
            bifrost_version or _installed_bifrost_version()
        )

    async def handle_text(
        self,
        request: TextRequest,
    ) -> TextResponse | ErrorEnvelope:
        try:
            result = await self._midgard.route_text(request)
        except Exception:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="midgard_unavailable",
                message="Bifröst could not reach the routing layer.",
            )

        if result.request_id is not None and result.request_id != request.request_id:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="correlation_mismatch",
                message="The routing layer returned a mismatched request id.",
            )

        return result

    async def handle_butlers(
        self,
    ) -> tuple[ButlerDirectoryEntry, ...] | ErrorEnvelope:
        try:
            return await self._midgard.list_butlers()
        except Exception:
            return ErrorEnvelope(
                request_id=None,
                code="midgard_unavailable",
                message="Bifröst could not reach the routing layer.",
            )



    async def handle_manifest(
        self,
    ) -> BifrostNodeManifest | ErrorEnvelope:
        try:
            manifest = await self._midgard.get_node_manifest()
        except Exception:
            return ErrorEnvelope(
                request_id=None,
                code="midgard_unavailable",
                message="Bifröst could not reach the routing layer.",
            )

        return BifrostNodeManifest(
            bifrost_version=self._bifrost_version,
            node=manifest,
        )


def _installed_bifrost_version() -> str:
    try:
        return version("butler-core-bifrost-plugin")
    except PackageNotFoundError:
        return "0.0.1.dev0"
