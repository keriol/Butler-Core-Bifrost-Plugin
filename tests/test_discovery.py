from butler_bifrost import DNS_SD_FQDN, DNS_SD_SERVICE_TYPE, discovery_txt_record


def test_dns_sd_service_is_stable():
    assert DNS_SD_SERVICE_TYPE == "_butler-bifrost._tcp"
    assert DNS_SD_FQDN == "_butler-bifrost._tcp.local."


def test_discovery_metadata_exposes_protocol_only():
    record = discovery_txt_record()
    assert record == {"protocol": "1"}


def test_discovery_metadata_contains_no_pairing_or_authentication_secret():
    record = discovery_txt_record()
    serialized = repr(record).casefold()
    assert "token" not in serialized
    assert "credential" not in serialized
    assert "secret" not in serialized
