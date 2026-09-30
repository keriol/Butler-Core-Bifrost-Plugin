from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import httpx

from .protocol import ErrorEnvelope, TextRequest, TextResponse


@dataclass(frozen=True, slots=True)
class HttpTransportConfig:
    endpoint: str
    token: str | None = None
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        endpoint = str(self.endpoint or "").strip()
        if not endpoint:
            raise ValueError("endpoint must not be blank.")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
        object.__setattr__(self, "endpoint", endpoint)


class HttpTransport:
    """Concrete HTTP bridge to an Asgard-compatible endpoint."""

    def __init__(
        self,
        config: HttpTransportConfig,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._config = config
        self._client = client or httpx.Client(
            timeout=config.timeout_seconds,
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "HttpTransport":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def send_text(
        self,
        request: TextRequest,
    ) -> TextResponse | ErrorEnvelope:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._config.token:
            headers["Authorization"] = (
                f"Bearer {self._config.token}"
            )

        payload: dict[str, Any] = {
            "request_id": request.request_id,
            "message": request.message,
        }
        if request.speaker is not None:
            payload["speaker"] = {
                key: value
                for key, value in asdict(
                    request.speaker
                ).items()
                if value is not None
            }

        try:
            response = self._client.post(
                self._config.endpoint,
                json=payload,
                headers=headers,
                timeout=self._config.timeout_seconds,
            )
            body = response.json()
        except (
            httpx.TimeoutException,
            httpx.NetworkError,
        ):
            return ErrorEnvelope(
                request_id=request.request_id,
                code="transport_unavailable",
                message="Bifröst transport could not reach the Butler endpoint.",
            )
        except ValueError:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="invalid_transport_response",
                message="Butler endpoint returned an invalid response.",
            )

        if not isinstance(body, dict):
            return ErrorEnvelope(
                request_id=request.request_id,
                code="invalid_transport_response",
                message="Butler endpoint returned an invalid response.",
            )

        response_request_id = body.get(
            "request_id",
            request.request_id,
        )

        if not body.get("ok", False):
            error = body.get("error")
            if not isinstance(error, dict):
                return ErrorEnvelope(
                    request_id=response_request_id,
                    code="remote_error",
                    message="Butler endpoint rejected the request.",
                )
            return ErrorEnvelope(
                request_id=response_request_id,
                code=str(
                    error.get("code")
                    or "remote_error"
                ),
                message=str(
                    error.get("message")
                    or "Butler endpoint rejected the request."
                ),
            )

        if response_request_id != request.request_id:
            return ErrorEnvelope(
                request_id=request.request_id,
                code="correlation_mismatch",
                message="Butler endpoint returned a mismatched request id.",
            )

        text = body.get("response")
        if not isinstance(text, str):
            return ErrorEnvelope(
                request_id=request.request_id,
                code="invalid_transport_response",
                message="Butler endpoint returned an invalid response.",
            )

        return TextResponse(
            request_id=request.request_id,
            response=text,
        )
