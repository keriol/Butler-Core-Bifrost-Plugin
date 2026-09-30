# Butler Core Bifröst Plugin 🌈

**The replaceable external/client bridge for the Butler ecosystem.**

Bifröst is the boundary external clients attach to. Android/Interphone and future clients should not know concrete Butler runtimes or Butler-owned entities such as Asgard.

The project is currently in private incubation and is being developed with a future public release in mind.

## Canonical role

```text
Client / Interphone
       |
     Bifröst
       |
     Midgard
       |
 cross-Butler routing
       |
 Butler-owned Asgard
       |
 concrete Butler
```

Midgard asks the available Butler-owned Asgard entities which Butler identity they represent and routes to the unique matching Butler universe.

Bifröst transports the requested Butler identity but does not resolve it.

## Identity flow

Request-side:

```text
target_butler_name
```

is carried from the client into Midgard.

Response-side:

```text
source_butler_name
```

comes from the responding Butler's Asgard and is propagated back to the client.

Bifröst must not fabricate, rewrite or silently substitute either identity.

## Current protocol scope

The current development line establishes:

- protocol versioning;
- request correlation;
- client HELLO messages;
- safe Butler identity responses;
- text request/response envelopes;
- stable error envelopes;
- safe speaker/session metadata;
- LAN discovery conventions based on DNS-SD / mDNS.

## Butler unavailable

A synchronous routing failure may carry a neutral client-notification descriptor such as:

```text
kind = butler_unavailable
presentation = system_neutral
documentation_url = optional
```

Bifröst transports that descriptor. The client owns localized rendering.

This is request/response UX, not proactive Butler communication.

## Historical HTTP proving adapter

The existing `HttpTransport` and `bifrost-probe` were created to prove the lower-layer Bifröst -> Asgard path before Midgard existed.

They remain useful as historical/lower-layer proving tools, but **direct Bifröst -> Asgard HTTP routing is not the canonical final architecture**.

New client integration work must target the Bifröst -> Midgard path.

## Multi-user session identity

A client may attach safe speaker identity metadata to a request.

Speaker identity is contextual information, not authentication. Raw audio, voiceprints and speaker embeddings are not part of the Bifröst protocol.

## LAN discovery

Bifröst defines the DNS-SD service type:

```text
_butler-bifrost._tcp
```

Discovery exists only to locate compatible Bifröst endpoints. It is not authorization.

```text
DISCOVER -> IDENTIFY -> PAIR/AUTH -> TRUSTED SESSION
```

Manual endpoint configuration remains a supported fallback.

See [Architecture](docs/architecture.md) for the ownership boundary.

## Development

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

## Project status

Current development version: **0.0.1.dev0**.

Bifröst is pre-release and under active contract proving.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Active work is tracked in GitHub Issues.

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
