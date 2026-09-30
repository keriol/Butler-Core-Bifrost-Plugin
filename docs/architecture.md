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

The concrete Butler host owns web-framework mounting, network binding and authentication policy. The reusable Bifröst package therefore does not depend on FastAPI, Flask or Starlette.

The adapter validates and serializes:

- request correlation;
- target Butler name;
- safe speaker metadata;
- source Butler identity;
- structured errors;
- neutral client-notification descriptors.

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

## Historical direct-Asgard transport

The current `HttpTransport` is lower-layer proving evidence created before Midgard existed.

```text
Bifröst -> Asgard
```

is historical/proving topology only, not the final client architecture.
