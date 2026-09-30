# Architecture

Bifröst is the replaceable communication bridge between client-side Butler
interfaces and runtime-side Butler boundaries.

## Topology

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

## Ownership

Bifröst owns protocol versioning, correlation, transport/session concerns,
safe handshake messages, discovery conventions and transport-level errors.

Bifröst does not own domain behavior, planning, tool execution policy,
provider semantics, notification significance or household configuration.

## Discovery boundary

DNS-SD / mDNS discovery advertises only endpoint compatibility metadata.
Runtime identity is returned during handshake. Trust and authorization happen
later through pairing/authentication.

Discovery must never imply authorization.
