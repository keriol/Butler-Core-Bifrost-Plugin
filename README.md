# Butler Core Bifröst Plugin 🌈

**A replaceable bridge between Butler clients and Butler runtimes.**

Bifröst is a transport-oriented plugin for the Butler ecosystem. It defines the
shared protocol surface used to connect client-side interfaces to runtime-side
Butler boundaries without coupling those clients to a concrete Butler
implementation.

The project is currently in private incubation and is being developed with a
public release in mind. Public/private boundaries are therefore enforced from
the first development commit.

## Why Bifröst?

A Butler client should not need to know how a runtime is implemented.

```text
Client / Interphone
       |
    Midgard
       |
    Bifröst
       |
    Asgard
       |
 active Butler
```

Bifröst is the bridge between the two sides. It is deliberately **not** the
Butler itself, not a domain runtime, and not an application plugin registry.

## Current scope

The first development line establishes:

- protocol versioning;
- request correlation;
- client HELLO messages;
- safe Butler identity responses;
- text request/response envelopes;
- stable error envelopes;
- safe session speaker identity metadata;
- a LAN discovery convention based on DNS-SD / mDNS.

The first optional HTTP transport adapter can send text requests to an
Asgard-compatible endpoint. No server implementation or Android client is
shipped yet.

Install the HTTP adapter dependencies with:

```bash
python -m pip install -e ".[http]"
```

## Multi-user session identity

A client may attach safe speaker identity metadata to a request:

```text
known user       -> speaker_id="marco", persistent=true
temporary guest  -> speaker_id="guest-a73f", persistent=false
anonymous guest  -> speaker_id="unknown-1", persistent=false
```

Optional presentation preferences such as display name, `call_me`, form of
address and language may travel with that session identity.

Speaker identity is **context, not authentication**. It must never bypass
normal Butler permissions or confirmation policy.

Biometric material stays outside Bifröst: raw audio, voiceprints and speaker
embeddings are not part of the protocol.

## LAN discovery

Bifröst defines the DNS-SD service type:

```text
_butler-bifrost._tcp
```

A compatible service may therefore appear on the local multicast domain as:

```text
_butler-bifrost._tcp.local.
```

Discovery exists only to locate compatible endpoints. It is **not**
authorization.

```text
DISCOVER -> IDENTIFY -> PAIR/AUTH -> TRUSTED SESSION
```

Discovery advertisements must not expose household capabilities, private entity
identifiers, provider payloads, credentials, or deployment topology.

Manual endpoint configuration remains a supported fallback.

See [Architecture](docs/architecture.md) for the ownership boundary.

## Development

Python 3.10 or newer is required.

```bash
git clone https://github.com/keriol/Butler-Core-Bifrost-Plugin.git
cd Butler-Core-Bifrost-Plugin

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

python -m pytest
python -m build
```

## Project status

Current development version: **0.0.1.dev0**.

Bifröst is pre-release and under active contract proving. Public availability
will follow only after the protocol, security boundary, discovery behavior and
cross-runtime compatibility have been validated.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Active work is tracked in GitHub Issues.

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
