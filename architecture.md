# Architecture diagrams for GSoC 2026 — BRL-CAD Python Bindings

## 1) Implemented stack 

This is the architecture **as shipped** in
[BRL-CAD/MOOSE](https://github.com/BRL-CAD/MOOSE) and
[AWaleed-Ahmed/brlcad-python-bindings](https://github.com/AWaleed-Ahmed/brlcad-python-bindings).

```mermaid
flowchart TB
    subgraph USER["Python code"]
        APP["scripts / tests"]
    end

    subgraph PY["Python package — brlcad/"]
        WRAP["Typed wrappers<br/>Sphere · Arb8 · Cone · Torus · Combinations · …"]
        DB["Database facade<br/>ConstDatabase · FileDatabase · MemoryDatabase"]
        HANDLE["Handle / Object<br/>ownership · SetName · attributes"]
        BIND["_bindings.py<br/>ctypes signatures · CDLL('libbrlcad.so')"]
    end

    subgraph CABI["MOOSE C bridge — libbrlcad.so"]
        CAPI["Flat C API<br/>BrlNewSphere · BrlConstDatabaseLoad · BrlObjectSetName · …"]
        CASTS["casts.cpp<br/>safe handle validation / magic tokens"]
    end

    subgraph MOOSE["MOOSE C++ API"]
        CXX["Database / Object / Primitives<br/>Sphere.cpp · Arb8.cpp · Combination.cpp · …"]
    end

    subgraph BRL["BRL-CAD core"]
        CORE["librt · libbn · libbu · ray-trace engine"]
        GEOM[".g geometry<br/>on disk / in memory"]
    end

    APP --> WRAP
    APP --> DB
    WRAP --> HANDLE
    DB --> HANDLE
    HANDLE --> BIND
    BIND --> CAPI
    CAPI --> CASTS
    CASTS --> CXX
    CXX --> CORE
    CORE --> GEOM

    classDef py fill:#6B4C9A,color:#fff,stroke:#3d2a5c
    classDef c fill:#D97706,color:#fff,stroke:#92400e
    classDef cxx fill:#E8A598,color:#1f2937,stroke:#b45309
    classDef core fill:#60A5FA,color:#0f172a,stroke:#1d4ed8
    classDef geom fill:#86EFAC,color:#14532d,stroke:#166534

    class WRAP,DB,HANDLE,BIND py
    class CAPI,CASTS c
    class CXX cxx
    class CORE core
    class GEOM geom
```

## 2) Proposal-style vertical abstraction layers

Aligned with your proposal diagram (Python → adapter → C bridge → MOOSE → BRL-CAD → .g).

```mermaid
flowchart TB
    L1["Python interface<br/><i>user-facing API — Sphere, Arb8, Combinations, databases</i>"]
    L2["ctypes adapter<br/><i>_bindings.py — type marshalling · CDLL</i>"]
    L3["C bridge<br/><i>libbrlcad.so — stable C ABI · Brl* entry points</i>"]
    L4["MOOSE C++ API<br/><i>mesh ops · geometry · solid modelling</i>"]
    L5["BRL-CAD core DB<br/><i>librt · libbn · libbu · ray-trace engine</i>"]
    L6["BRL-CAD geometry<br/><i>on disk / in memory (.g)</i>"]

    L1 --> L2 --> L3 --> L4 --> L5 --> L6

    style L1 fill:#7C3AED,color:#fff
    style L2 fill:#0D9488,color:#fff
    style L3 fill:#EA580C,color:#fff
    style L4 fill:#FDBA74,color:#1f2937
    style L5 fill:#93C5FD,color:#0f172a
    style L6 fill:#86EFAC,color:#14532d
```

## 3) Read / write data flow (user workflow)

```mermaid
flowchart LR
    subgraph WRITE["Write / model path"]
        P1["Create primitives<br/>Sphere / Arb8 / Torus / …"]
        P2["Build CSG<br/>Combinations · leaf ops"]
        P3["Set names & attributes"]
    end

    subgraph STACK["Software stack"]
        S1["Python wrappers"]
        S2["_bindings.py ctypes"]
        S3["libbrlcad.so C ABI"]
        S4["MOOSE C++"]
        S5["BRL-CAD engine"]
    end

    subgraph STORE["Persistence"]
        G[".g database file"]
    end

    subgraph READ["Read / verify path"]
        R1["ConstDatabase.Load"]
        R2["Get(name) → typed wrapper"]
        R3["MGED inspection / rt"]
    end

    P1 --> S1
    P2 --> S1
    P3 --> S1
    S1 --> S2 --> S3 --> S4 --> S5 --> G
    G --> R1 --> R2
    G --> R3
```
