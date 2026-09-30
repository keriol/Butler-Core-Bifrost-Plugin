from __future__ import annotations

from .ports import MidgardIngressPort
from .protocol import ErrorEnvelope, TextRequest, TextResponse


class BifrostIngress:
    """External/client ingress that delegates Butler routing to Midgard."""

    def __init__(self, midgard: MidgardIngressPort) -> None:
        self._midgard = midgard

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
