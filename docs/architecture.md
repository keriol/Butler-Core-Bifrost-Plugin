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


## Multi-user identity boundary

Bifröst can transport a client-asserted speaker/session identity so the Butler
can preserve per-person conversational context.

A speaker identity may be persistent, temporary and named, or temporary and
anonymous. For example, a client may use `unknown-1` when a person declines
to identify themselves.

The bridge does not determine who is speaking. Speaker recognition, voice
enrollment and temporary voice embeddings belong to the client-side identity
layer. Bifröst carries only safe identity metadata.

Temporary-session lifetime is also host policy. A client may choose a sliding
30-minute idle timeout, but Bifröst does not implement or enforce that timer.

Speaker identity is never authentication and must not authorize privileged or
dangerous operations by itself.
