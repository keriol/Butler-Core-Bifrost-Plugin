"""Public Bifröst protocol contracts."""

from .discovery import DNS_SD_FQDN, DNS_SD_SERVICE_TYPE, discovery_txt_record
from .protocol import (
    PROTOCOL_VERSION,
    ButlerIdentity,
    ErrorEnvelope,
    Hello,
    SpeakerIdentity,
    TextRequest,
    TextResponse,
)

__all__ = [
    "PROTOCOL_VERSION",
    "DNS_SD_FQDN",
    "DNS_SD_SERVICE_TYPE",
    "ButlerIdentity",
    "ErrorEnvelope",
    "Hello",
    "SpeakerIdentity",
    "TextRequest",
    "TextResponse",
    "discovery_txt_record",
    "HttpTransport",
    "HttpTransportConfig",
]

try:
    from .http_transport import HttpTransport, HttpTransportConfig
except ModuleNotFoundError:
    HttpTransport = None  # type: ignore[assignment]
    HttpTransportConfig = None  # type: ignore[assignment]
