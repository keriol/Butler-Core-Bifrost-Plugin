from dataclasses import fields

from butler_bifrost import SpeakerIdentity


def test_speaker_identity_has_no_biometric_transport_fields():
    names = {field.name for field in fields(SpeakerIdentity)}

    forbidden = {
        "audio",
        "raw_audio",
        "voiceprint",
        "voice_embedding",
        "embedding",
        "biometric_template",
        "confidence_vector",
    }

    assert names.isdisjoint(forbidden)


def test_speaker_identity_is_context_not_authentication_contract():
    names = {field.name for field in fields(SpeakerIdentity)}

    assert "authenticated" not in names
    assert "authorized" not in names
    assert "permissions" not in names
