from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .ingress import BifrostIngress
from .protocol import (
    ButlerDirectoryEntry,
    ErrorEnvelope,
    SpeakerIdentity,
    TextRequest,
    TextResponse,
)


@dataclass(frozen=True, slots=True)
class HttpIngressResult:
    status_code: int
    body: dict[str, Any]


class HttpIngressAdapter:
    """Framework-neutral HTTP payload adapter for Bifröst."""

    def __init__(self, ingress: BifrostIngress) -> None:
        self._ingress = ingress

    async def handle_butlers(self) -> HttpIngressResult:
        result = await self._ingress.handle_butlers()
        if isinstance(result, ErrorEnvelope):
            return self._serialize_error(
                result,
                status_code=self._status_for_error(result.code),
            )

        return HttpIngressResult(
            status_code=200,
            body={
                "ok": True,
                "butlers": [
                    {
                        "canonical_name": entry.canonical_name,
                        "aliases": list(entry.aliases),
                        "available": entry.available,
                    }
                    for entry in result
                ],
            },
        )

    async def handle_json(
        self,
        payload: Mapping[str, Any] | Any,
    ) -> HttpIngressResult:
        parsed = self._parse_request(payload)
        if isinstance(parsed, ErrorEnvelope):
            return self._serialize_error(parsed, status_code=400)

        result = await self._ingress.handle_text(parsed)
        if isinstance(result, ErrorEnvelope):
            return self._serialize_error(
                result,
                status_code=self._status_for_error(result.code),
            )

        return HttpIngressResult(
            status_code=200,
            body={
                "ok": True,
                "request_id": result.request_id,
                "source_butler_name": result.source_butler_name,
                "response": result.response,
            },
        )

    def _parse_request(
        self,
        payload: Mapping[str, Any] | Any,
    ) -> TextRequest | ErrorEnvelope:
        if not isinstance(payload, Mapping):
            return ErrorEnvelope(
                request_id=None,
                code="invalid_request",
                message="Request body must be a JSON object.",
            )

        request_id = self._optional_text(payload.get("request_id"))
        message = self._optional_text(payload.get("message"))
        target = self._optional_text(payload.get("target_butler_name"))

        if request_id is None:
            return ErrorEnvelope(
                request_id=None,
                code="invalid_request",
                message="request_id must not be blank.",
            )
        if message is None:
            return ErrorEnvelope(
                request_id=request_id,
                code="invalid_request",
                message="message must not be blank.",
            )

        speaker_payload = payload.get("speaker")
        speaker = None
        if speaker_payload is not None:
            parsed_speaker = self._parse_speaker(
                speaker_payload,
                request_id=request_id,
            )
            if isinstance(parsed_speaker, ErrorEnvelope):
                return parsed_speaker
            speaker = parsed_speaker

        try:
            return TextRequest(
                request_id=request_id,
                message=message,
                target_butler_name=target,
                speaker=speaker,
            )
        except ValueError:
            return ErrorEnvelope(
                request_id=request_id,
                code="invalid_request",
                message="Request payload is invalid.",
            )

    def _parse_speaker(
        self,
        payload: Any,
        *,
        request_id: str,
    ) -> SpeakerIdentity | ErrorEnvelope:
        if not isinstance(payload, Mapping):
            return ErrorEnvelope(
                request_id=request_id,
                code="invalid_request",
                message="speaker must be a JSON object.",
            )

        speaker_id = self._optional_text(payload.get("speaker_id"))
        persistent = payload.get("persistent", False)
        if speaker_id is None or not isinstance(persistent, bool):
            return ErrorEnvelope(
                request_id=request_id,
                code="invalid_request",
                message="speaker metadata is invalid.",
            )

        try:
            return SpeakerIdentity(
                speaker_id=speaker_id,
                persistent=persistent,
                display_name=self._optional_text(payload.get("display_name")),
                call_me=self._optional_text(payload.get("call_me")),
                form_of_address=self._optional_text(
                    payload.get("form_of_address")
                ),
                language=self._optional_text(payload.get("language")),
            )
        except ValueError:
            return ErrorEnvelope(
                request_id=request_id,
                code="invalid_request",
                message="speaker metadata is invalid.",
            )

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if value is None or not isinstance(value, str):
            return None
        clean = value.strip()
        return clean or None

    @staticmethod
    def _status_for_error(code: str) -> int:
        if code in {"invalid_request"}:
            return 400
        if code == "butler_not_found":
            return 404
        if code in {"ambiguous_target", "correlation_mismatch", "source_identity_mismatch"}:
            return 409
        if code in {
            "target_unavailable",
            "target_failure",
            "midgard_unavailable",
        }:
            return 503
        return 500

    @staticmethod
    def _serialize_error(
        error: ErrorEnvelope,
        *,
        status_code: int,
    ) -> HttpIngressResult:
        body: dict[str, Any] = {
            "ok": False,
            "request_id": error.request_id,
            "error": {
                "code": error.code,
                "message": error.message,
            },
        }
        if error.notification is not None:
            body["notification"] = {
                key: value
                for key, value in asdict(error.notification).items()
                if value is not None
            }
            body["notification"]["kind"] = error.notification.kind.value
            body["notification"]["presentation"] = (
                error.notification.presentation.value
            )

        return HttpIngressResult(
            status_code=status_code,
            body=body,
        )
