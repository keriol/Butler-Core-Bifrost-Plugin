# Butler Core Bifröst Plugin 🌈

**The replaceable external/client bridge for the Butler ecosystem.**

Bifröst is the public boundary where external clients attach to a Butler
network. It transports requests, correlation identity and safe routing metadata
without owning Butler selection or concrete runtime behavior.

```text
Client / Interphone
       |
     Bifröst
       |
     Midgard
       |
   Butler Core
```

When a request explicitly targets a concrete Butler, Midgard may continue
through that Butler's own Asgard ingress boundary.

## Current release

**Public Alpha: 0.1.0 — Ignition**

Bifröst 0.1.0 is the first network-capable release validated in
**IGNITION-001**, the coordinated Butler-to-Android baseline.

## Responsibilities

Bifröst owns:

- external/client protocol envelopes;
- request correlation;
- text request/response transport;
- optional Butler target metadata;
- source-Butler identity propagation;
- safe speaker/session metadata;
- read-only Butler directory transport;
- node-manifest transport;
- LAN discovery conventions.

Bifröst does **not** own:

- Butler routing policy;
- concrete Butler behavior;
- household configuration;
- authorization policy;
- Home Assistant semantics.

## Canonical paths

Core-facing request:

```text
Client
  -> Bifröst
  -> Midgard
  -> Butler Core
  -> provider/plugin
```

Explicit Butler request:

```text
Client
  -> Bifröst
  -> Midgard
  -> Butler-owned Asgard
  -> concrete Butler
```

Bifröst carries `target_butler_name` but does not resolve it.

Concrete Butler responses may return `source_butler_name`, sourced by the
responding Butler boundary and propagated back to the client unchanged.

## Discovery and trust

Bifröst defines the DNS-SD service type:

```text
_butler-bifrost._tcp
```

Discovery locates endpoints. It is **not** authentication.

```text
DISCOVER -> IDENTIFY -> PAIR/AUTH -> TRUSTED SESSION
```

Pairing/device credentials remain post-0.1.0 work.

## Development

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

The package deliberately contains no concrete Butler or household dependency.

## Historical proving adapter

The repository still contains the earlier HTTP proving transport and
`bifrost-probe`. They remain useful lower-layer diagnostic tools, but direct
Bifröst -> Asgard routing is **not** the canonical final architecture.

New integrations target Bifröst -> Midgard.

## Public boundary

Public tests explicitly guard against:

- Alfred-specific imports;
- Asgard ownership leaking into Bifröst;
- household-specific entity identifiers;
- biometric speaker material.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0.
