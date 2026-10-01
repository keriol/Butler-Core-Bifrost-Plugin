# Architecture

Bifröst is the external/client bridge of the Butler ecosystem.

## Canonical topology

Bifröst transports client requests into Midgard. Midgard may then use either
its Core-facing channel or cross-Butler routing depending on the request.

Core-owned capability:

```text
external client
      |
    Bifröst
      |
    Midgard
      |
 Butler Core
      |
provider/plugin capability
```

Explicit Butler target:

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

Bifröst does not address Alfred, Wilfred or another Butler directly, and it
does not decide whether a request belongs to Core or a concrete Butler.

## HTTP ingress ownership

Bifröst owns the HTTP payload contract through a framework-neutral adapter.

```text
HTTP JSON
   |
HttpIngressAdapter
   |
BifrostIngress
   |
Midgard-facing port
```

The concrete host owns web-framework mounting, network binding and
authentication policy. The reusable Bifröst package therefore does not depend
on FastAPI, Flask or Starlette.

The adapter validates and serializes:

- request correlation;
- optional target Butler name;
- safe speaker metadata;
- source Butler identity when a concrete Butler answers;
- structured errors;
- neutral client-notification descriptors.

A client omits `target_butler_name` for requests intended for the Core-facing
path. When a target name is supplied, Bifröst preserves it unchanged for
Midgard.

## Ownership

Bifröst owns:

- external/client protocol versioning;
- request correlation at the client boundary;
- transport/session concerns;
- safe handshake messages;
- discovery conventions;
- transport-level errors;
- transport of optional target Butler metadata;
- propagation of Butler-originated response identity;
- propagation of synchronous neutral client-notification descriptors.

Bifröst does not own:

- Core-vs-Butler routing policy;
- cross-Butler target resolution;
- Butler identity;
- Asgard;
- domain behavior;
- planning;
- tool execution policy;
- provider semantics;
- notification significance;
- household configuration.

## Historical direct-Asgard transport

The current `HttpTransport` is lower-layer proving evidence created before
Midgard existed.

```text
Bifröst -> Asgard
```

is historical/proving topology only, not the final client architecture.
