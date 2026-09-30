# Architecture

Bifröst is the external/client bridge of the Butler ecosystem.

## Canonical topology

```text
external client
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

Bifröst does not address Alfred, Wilfred or another Butler directly.

## Ownership

Bifröst owns:

- external/client protocol versioning;
- request correlation at the client boundary;
- transport/session concerns;
- safe handshake messages;
- discovery conventions;
- transport-level errors;
- transport of target Butler metadata;
- propagation of Butler-originated response identity;
- propagation of synchronous neutral client-notification descriptors.

Bifröst does not own:

- cross-Butler target resolution;
- Butler identity;
- Asgard;
- domain behavior;
- planning;
- tool execution policy;
- provider semantics;
- notification significance;
- household configuration.

## Butler identity

The client may request:

```text
target_butler_name
```

Bifröst transports that metadata to Midgard.

Midgard owns cross-Butler routing by asking Butler-owned Asgard entities which Butler identity they represent.

A successful response carries:

```text
source_butler_name
```

That identity originates from the selected Butler's Asgard. Bifröst only propagates it.

## Synchronous unavailable notification

When Midgard cannot reach the requested Butler because the Butler is missing, offline, unavailable, misconfigured or non-responsive, the structured error may include:

```text
kind = butler_unavailable
presentation = system_neutral
documentation_url = optional
```

Bifröst transports this descriptor to the client. It does not localize or reinterpret it.

## Historical direct-Asgard transport

The current `HttpTransport` is lower-layer proving evidence created before Midgard existed.

```text
Bifröst -> Asgard
```

is therefore historical/proving topology only, not the final client architecture.

It must not be used as justification for new direct client-to-Asgard coupling.

## Discovery boundary

DNS-SD / mDNS discovery advertises only endpoint compatibility metadata.

Discovery must never imply authorization.

## Multi-user identity boundary

Bifröst may transport client-asserted speaker/session identity so the Butler can preserve conversational context.

Speaker identity is not authentication and must not authorize privileged or dangerous operations by itself.
