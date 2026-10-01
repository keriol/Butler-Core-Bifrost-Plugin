from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


PROTOCOL_VERSION = 1


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


class ClientNotificationKind(str, Enum):
    BUTLER_UNAVAILABLE = "butler_unavailable"


class ClientNotificationPresentation(str, Enum):
    SYSTEM_NEUTRAL = "system_neutral"


@dataclass(frozen=True, slots=True)
class ClientNotification:
    kind: ClientNotificationKind
    presentation: ClientNotificationPresentation = (
        ClientNotificationPresentation.SYSTEM_NEUTRAL
    )
    documentation_url: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "documentation_url",
            _optional(self.documentation_url),
        )


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
            object.__setattr__(
                self,
                field_name,
                _optional(getattr(self, field_name)),
            )


@dataclass(frozen=True, slots=True)
class ButlerDirectoryEntry:
    canonical_name: str
    aliases: tuple[str, ...] = ()
    available: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "canonical_name",
            _required(self.canonical_name, "canonical_name"),
        )
        object.__setattr__(
            self,
            "aliases",
            tuple(
                clean
                for alias in self.aliases
                if (clean := _optional(alias)) is not None
            ),
        )


@dataclass(frozen=True, slots=True)
class TextRequest:
    request_id: str
    message: str
    speaker: SpeakerIdentity | None = None
    target_butler_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "message", _required(self.message, "message"))
        object.__setattr__(
            self,
            "target_butler_name",
            _optional(self.target_butler_name),
        )


@dataclass(frozen=True, slots=True)
class TextResponse:
    request_id: str
    response: str
    ok: bool = True
    source_butler_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(
            self,
            "source_butler_name",
            _optional(self.source_butler_name),
        )


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    request_id: str | None
    code: str
    message: str
    notification: ClientNotification | None = None

    def __post_init__(self) -> None:
        if self.request_id is not None:
            object.__setattr__(self, "request_id", _required(self.request_id, "request_id"))
        object.__setattr__(self, "code", _required(self.code, "code"))
        object.__setattr__(self, "message", _required(self.message, "message"))
