"""Public Bifröst protocol contracts."""

from .discovery import DNS_SD_FQDN, DNS_SD_SERVICE_TYPE, discovery_txt_record
from .http_ingress import HttpIngressAdapter, HttpIngressResult
from .ingress import BifrostIngress
from .ports import (
    DeviceCredentialAuthenticatorPort,
    MidgardIngressPort,
    PairingRuntimePort,
)
from .pairing import (
    BifrostPairing,
    DeviceAuthentication,
    DeviceCredentialState,
    PairingHttpAdapter,
    PairingHttpResult,
    PairingRequest,
    PairingResult,
    PairingState,
)
from .protocol import (
    PROTOCOL_VERSION,
    BifrostNodeManifest,
    ButlerDescriptor,
    ButlerDirectoryEntry,
    CallableDescriptor,
    CoreStackDescriptor,
    DependencyDescriptor,
    EntityDescriptor,
    NodeManifest,
    PluginDescriptor,
    ReadinessDescriptor,
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
    "BifrostNodeManifest",
    "ButlerDescriptor",
    "ButlerDirectoryEntry",
    "CallableDescriptor",
    "CoreStackDescriptor",
    "DependencyDescriptor",
    "EntityDescriptor",
    "NodeManifest",
    "PluginDescriptor",
    "ReadinessDescriptor",
    "ButlerIdentity",
    "ClientNotification",
    "ClientNotificationKind",
    "ClientNotificationPresentation",
    "ErrorEnvelope",
    "Hello",
    "HttpIngressAdapter",
    "HttpIngressResult",
    "DeviceCredentialAuthenticatorPort",
    "MidgardIngressPort",
    "PairingRuntimePort",
    "BifrostPairing",
    "DeviceAuthentication",
    "DeviceCredentialState",
    "PairingHttpAdapter",
    "PairingHttpResult",
    "PairingRequest",
    "PairingResult",
    "PairingState",
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
