from __future__ import annotations

from dataclasses import dataclass


PROTOCOL_VERSION = 1


def _required(value: str, field_name: str) -> str:
    clean = str(value or "").strip()
    if not clean:
        raise ValueError(f"{field_name} must not be blank.")
    return clean


@dataclass(frozen=True, slots=True)
class Hello:
    request_id: str
    client_id: str
    protocol_version: int = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "client_id", _required(self.client_id, "client_id"))


@dataclass(frozen=True, slots=True)
class ButlerIdentity:
    request_id: str
    butler_name: str
    instance_id: str
    pairing_required: bool
    protocol_version: int = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "butler_name", _required(self.butler_name, "butler_name"))
        object.__setattr__(self, "instance_id", _required(self.instance_id, "instance_id"))


@dataclass(frozen=True, slots=True)
class SpeakerIdentity:
    """Safe session identity asserted by the client.

    This is contextual identity for personalization and conversation routing.
    It is not authentication and contains no biometric material.
    """

    speaker_id: str
    persistent: bool
    display_name: str | None = None
    call_me: str | None = None
    form_of_address: str | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "speaker_id", _required(self.speaker_id, "speaker_id"))

        for field_name in (
            "display_name",
            "call_me",
            "form_of_address",
            "language",
        ):
            value = getattr(self, field_name)
            if value is not None:
                clean = str(value).strip()
                object.__setattr__(
                    self,
                    field_name,
                    clean or None,
                )


@dataclass(frozen=True, slots=True)
class TextRequest:
    request_id: str
    message: str
    speaker: SpeakerIdentity | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "message", _required(self.message, "message"))


@dataclass(frozen=True, slots=True)
class TextResponse:
    request_id: str
    response: str
    ok: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    request_id: str | None
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.request_id is not None:
            object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "code", _required(self.code, "code"))
        object.__setattr__(self, "message", _required(self.message, "message"))
