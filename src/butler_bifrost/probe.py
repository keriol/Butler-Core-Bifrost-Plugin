from __future__ import annotations

import argparse
import json
import sys
import uuid

from .http_transport import HttpTransport, HttpTransportConfig
from .protocol import ErrorEnvelope, SpeakerIdentity, TextRequest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bifrost-probe",
        description="Exercise the Bifröst HTTP transport against Asgard.",
    )
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--token")
    parser.add_argument("--message", required=True)
    parser.add_argument("--request-id")
    parser.add_argument("--speaker-id")
    parser.add_argument(
        "--speaker-persistent",
        action="store_true",
    )
    parser.add_argument("--language")
    parser.add_argument("--call-me")
    parser.add_argument("--form-of-address")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    speaker = None
    if args.speaker_id:
        speaker = SpeakerIdentity(
            speaker_id=args.speaker_id,
            persistent=bool(args.speaker_persistent),
            language=args.language,
            call_me=args.call_me,
            form_of_address=args.form_of_address,
        )

    request = TextRequest(
        request_id=args.request_id or str(uuid.uuid4()),
        message=args.message,
        speaker=speaker,
    )

    try:
        with HttpTransport(
            HttpTransportConfig(
                endpoint=args.endpoint,
                token=args.token,
            )
        ) as transport:
            result = transport.send_text(request)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "request_id": request.request_id,
                    "error": {
                        "code": "probe_failure",
                        "message": str(exc),
                    },
                }
            )
        )
        return 2

    if isinstance(result, ErrorEnvelope):
        print(
            json.dumps(
                {
                    "ok": False,
                    "request_id": result.request_id,
                    "error": {
                        "code": result.code,
                        "message": result.message,
                    },
                }
            )
        )
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "request_id": result.request_id,
                "response": result.response,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
