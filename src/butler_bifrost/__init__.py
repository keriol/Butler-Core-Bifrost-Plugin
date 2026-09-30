"""Public Bifröst protocol contracts."""

from .discovery import DNS_SD_FQDN, DNS_SD_SERVICE_TYPE, discovery_txt_record
from .http_ingress import HttpIngressAdapter, HttpIngressResult
from .ingress import BifrostIngress
from .ports import MidgardIngressPort
from .protocol import (
    PROTOCOL_VERSION,
    ButlerIdentity,
    ClientNotification,
    ClientNotificationKind,
    ClientNotificationPresentation,
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
    "BifrostIngress",
    "ButlerIdentity",
    "ClientNotification",
    "ClientNotificationKind",
    "ClientNotificationPresentation",
    "ErrorEnvelope",
    "Hello",
    "HttpIngressAdapter",
    "HttpIngressResult",
    "MidgardIngressPort",
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
