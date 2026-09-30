from __future__ import annotations

from .protocol import PROTOCOL_VERSION


DNS_SD_SERVICE_TYPE = "_butler-bifrost._tcp"
DNS_SD_FQDN = f"{DNS_SD_SERVICE_TYPE}.local."


def discovery_txt_record() -> dict[str, str]:
    """Return only public compatibility metadata for discovery."""
    return {"protocol": str(PROTOCOL_VERSION)}
