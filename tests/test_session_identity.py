from butler_bifrost import SpeakerIdentity, TextRequest


def test_known_persistent_speaker_can_travel_with_request():
    speaker = SpeakerIdentity(
        speaker_id="marco",
        persistent=True,
        display_name="Marco",
        call_me="zio",
        form_of_address="sir",
        language="it",
    )

    request = TextRequest(
        request_id="req-1",
        message="Accendi la luce.",
        speaker=speaker,
    )

    assert request.speaker is speaker
    assert request.speaker.persistent is True
    assert request.speaker.call_me == "zio"


def test_named_guest_is_explicitly_temporary():
    speaker = SpeakerIdentity(
        speaker_id="guest-a73f",
        persistent=False,
        display_name="Luca",
        language="it",
    )

    assert speaker.persistent is False
    assert speaker.display_name == "Luca"


def test_anonymous_unknown_user_needs_no_personal_name():
    speaker = SpeakerIdentity(
        speaker_id="unknown-1",
        persistent=False,
    )

    assert speaker.display_name is None
    assert speaker.call_me is None
    assert speaker.form_of_address is None


def test_optional_presentation_fields_normalize_blank_to_none():
    speaker = SpeakerIdentity(
        speaker_id="unknown-1",
        persistent=False,
        display_name="   ",
        call_me=" ",
        form_of_address="",
        language=" ",
    )

    assert speaker.display_name is None
    assert speaker.call_me is None
    assert speaker.form_of_address is None
    assert speaker.language is None
