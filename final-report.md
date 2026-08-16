# GSoC 2026 — Final Report

## Organization: [BRL-CAD](https://brlcad.org/)

**Project:** BRL-CAD Python Bindings  
**Contributor:** Abdullah Waleed Ahmed · Islamabad, Pakistan (UTC+05:00)  
**Mentor:** Daniel Rossberg  
**Period:** May – August 2026  

| Resource | URL |
|----------|-----|
| Upstream repository | https://github.com/BRL-CAD/MOOSE |
| Development repository | https://github.com/AWaleed-Ahmed/brlcad-python-bindings |
| Contributor profile | https://github.com/AWaleed-Ahmed |
| Project log (this folder) | [README.md](README.md) |

---

## Abstract

This project delivers a practical Python path into BRL-CAD through the MOOSE interface layer. Instead of binding the C++ ABI directly, the work establishes a stable C bridge (`libbrlcad.so`), then a handcrafted `ctypes` adapter and typed Python wrappers. The result is a clearer modeling workflow, create primitives, compose CSG combinations, manage database modes, and inspect geometry while preserving BRL-CAD semantics and remaining easy for mentors and maintainers to review incrementally.

---

## Motivation

BRL-CAD’s strength has historically lived behind C and C++ APIs. Python users needed a path that felt natural without sacrificing correctness or forcing a redesign of the geometry core. MOOSE already provided a cleaner C++ object model; this project completed and widened the C exposure of that model and layered a pythonic package on top so that everyday scripts can drive solid modeling and verify results in MGED.

---

## Scope and deliverables

### Delivered

1. **C ABI expansion on MOOSE** — casts, database title/name APIs, const-database helpers, and a wide set of primitive wrappers.
2. **CSG / Combinations** — combination construction and related object plumbing needed for boolean assemblies.
3. **Bag of Triangles (BoT)** — mesh-oriented interface support.
4. **Python package** — `brlcad/` wrappers (`Sphere`, `Arb8`, `Cone`, databases, `Combinations`, …) with `ctypes` bindings to `libbrlcad.so`.
5. **Extended primitive families** — torus family, particle / quadric-style solids, sketch, pipe, vector list, and related types.
6. **Verification workflow** — demo `.g` geometry inspected in MGED (see figure below).

### Design constraints kept in scope

- Prefer a **thin C bridge** over direct pybind11 / SWIG for this cycle.
- Keep **one operation ≈ one MOOSE call ≈ one `.g` representation**.
- Grow the API **pull request by pull request** under mentor review.

---

## Work completed and remaining

### Completed

The MOOSE C bridge is mapped into Python for the surfaces needed to model and inspect geometry from scripts: **databases**, **primitives**, **combinations**, **VectorList**, and related object helpers. The layering is concrete and reviewable—**`ctypes` bindings** in `_bindings.py` plus **object-oriented wrappers** in `brlcad/`—and was landed upstream through thirteen merged pull requests on [BRL-CAD/MOOSE](https://github.com/BRL-CAD/MOOSE), with ongoing development mirrored at [brlcad-python-bindings](https://github.com/AWaleed-Ahmed/brlcad-python-bindings).

In addition, key production-readiness milestones have been completed:
- **Installation & packaging** — CMake and `pip` installation cleanly ship every module, and `libbrlcad` is discoverable without manual `LD_LIBRARY_PATH` workarounds.
- **End-to-end workflows** — Verified **create → add → save `.g` → load / inspect** from Python as a first-class, documented path (including exposing previously missing write/`Add` bridge pieces).
- **Testing & CI** — Automated smoke tests ensure that installs and symbol drift cannot fail silently.
- **Version alignment** — The Python package versioning is strictly aligned with MOOSE.

In short: the binding *contract* (C ABI → ctypes → OO API) and a broad primitive/CSG surface are in place, usable for development, fully tested, and easily installable.

### Remaining

The bindings are functionally complete and structurally sound. The final piece of intentional follow-on work is focused on user onboarding:

1. **Documentation** — A short getting-started guide plus a few tutorials (hello sphere, CSG combination, open an existing `.g`).

---

## Architecture

The shipped stack matches the proposal’s layered idea, expressed concretely in MOOSE and the Python package:

```text
Your Python code
        │
        ▼
 Python wrappers   (Sphere, Arb8, Combinations, FileDatabase, …)
        │
        ▼
 _bindings.py      (ctypes · CDLL("libbrlcad.so"))
        │
        ▼
 libbrlcad.so      (flat C API · casts / handle validation)
        │
        ▼
 MOOSE C++ API     (Database / Object / primitives)
        │
        ▼
 BRL-CAD core      (librt · libbn · libbu · ray-trace)
        │
        ▼
 .g geometry       (on disk / in memory)
```

**Why this shape matters**

- **Python wrappers** hide pointer ownership and present familiar constructors (`Sphere(center, radius)`, `Arb8` as RPP, and so on).
- **`ctypes` bindings** marshal arguments and keep the Python side free of compiler-specific C++ ABI coupling.
- **The C bridge** is the maintenance boundary: named `Brl*` entry points plus magic-token casting so File/Memory databases validate correctly (see PR [#7](https://github.com/BRL-CAD/MOOSE/pull/7)).
- **MOOSE C++** remains the semantic source of truth for objects and databases.
- **BRL-CAD core** executes geometry behavior; MGED remains the visual verifier for `.g` output.

Mermaid sources for publication-quality exports live in [architecture-mermaid.md](architecture-mermaid.md). Proposal-era diagrams are archived under `images/proposal-architecture-*.png`.

---

## Demonstration

A demo scene (`sphere` + rectangular box + `torus`, combined as `scene.r`) was written to a `.g` database and opened in MGED:

<p align="center">
  <img src="images/mged-wireframe.png" alt="MGED wireframe of GSoC demo scene" width="780" />
</p>

<p align="center"><em>Figure — Wireframe view of the GSoC demo database in MGED.</em></p>

The helper script used to recreate and view the scene is [`scripts/create_and_view_demo.py`](scripts/create_and_view_demo.py).

---

## Work narrative by phase

### May — Foundations

Community bonding and deep reading of MOOSE’s C and C++ layers. First merges fixed handle casting for writable database variants, introduced the Arb8 C wrapper, and exposed `SetName` / `SetTitle` so objects and databases could be labeled from the bridge—prerequisites for any serious Python facade.

### June — Core geometry and CSG

Expanded const-database and vector-list support, landed Sphere / Ellipsoid / Cone, completed Arb8 and Object behavior, and delivered Combinations so boolean structure could be expressed through the C API.

### July — Python package and broader primitives

Implemented Bag of Triangles support, then merged the first full Python bindings tree into MOOSE ([PR #15](https://github.com/BRL-CAD/MOOSE/pull/15)). Immediately afterward, extended both C and Python surfaces for Torus, EllipticalTorus, HyperbolicCylinder, and NonManifoldGeometry helpers, then Particle / Paraboloid / Hyperboloid / Halfspace.

### August — Coverage, polish, and submission

Completed Unknown, VectorList, Sketch, ParabolicCylinder, and Pipe ([PR #18](https://github.com/BRL-CAD/MOOSE/pull/18)), fixed remaining VectorList and Sketch issues while introducing Python wheel support for `pip` installation ([PR #19](https://github.com/BRL-CAD/MOOSE/pull/19)), tightened wrappers, prepared demo geometry for MGED screenshots, and assembled this final submission package.

---

## Pull requests in detail

### [#7 — Expand CastConstDatabase](https://github.com/BRL-CAD/MOOSE/pull/7) · merged 2026-05-21

**Problem.** `CastConstDatabase` only accepted the base ConstDatabase magic token, so FileDatabase and MemoryDatabase handles failed validation and blocked wrappers.

**Work.** Extended casting/validation and related database sources so variant database handles cast safely for downstream Python and C clients.

**Files (high level).** `src/C/casts.cpp`, `FileDatabase.cpp`, `MemoryDatabase.cpp`, `Handle.h`.

---

### [#8 — Arb8 C API wrapper](https://github.com/BRL-CAD/MOOSE/pull/8) · merged 2026-05-27

Introduced dedicated `arb8.h` / `arb8.cpp` C entry points for the eight-vertex polyhedron family and wired them into the C build. Validated early with a small Python ctypes experiment.

---

### [#9 — SetName and SetTitle](https://github.com/BRL-CAD/MOOSE/pull/9) · merged 2026-05-30

Exposed object naming and database title mutation through the C API (`object` / `database` headers and sources, cast updates). Essential for readable `.g` contents and MGED inspection.

---

### [#10 — ConstDatabase C methods](https://github.com/BRL-CAD/MOOSE/pull/10) · merged 2026-06-04

Grew the read-side const-database surface and VectorList-related C support so Python could load databases, query titles, and interact with plot/selection-oriented helpers more completely.

---

### [#11 — Sphere, Ellipsoid, Cone](https://github.com/BRL-CAD/MOOSE/pull/11) · merged 2026-06-11

Added C headers/sources for Sphere, Ellipsoid, and Cone, integrated casts/globals/object plumbing, and established the pattern later primitives would follow.

---

### [#12 — Arb8 and Object completion](https://github.com/BRL-CAD/MOOSE/pull/12) · merged 2026-06-21

Finished remaining Arb8 and Object C API gaps (attributes, validity, typing helpers) so wrappers could present a consistent object base class.

---

### [#13 — Combination](https://github.com/BRL-CAD/MOOSE/pull/13) · merged 2026-06-28

Landed Combination support for CSG assembly—region flags, leaf operations, and related cast/global integration—connecting individual primitives into boolean trees.

---

### [#14 — Bag of Triangles](https://github.com/BRL-CAD/MOOSE/pull/14) · merged 2026-07-18

Added BoT C/C++ interface pieces (faces, casts, const-database touchpoints) to support triangle-mesh style geometry through the same bridge.

---

### [#15 — Python Bindings](https://github.com/BRL-CAD/MOOSE/pull/15) · merged 2026-07-22

**Landmark merge.** Introduced `src/Python/` into MOOSE: `_bindings.py`, Handle/Object/Database wrappers, core primitives, Combinations, usage notes, and initial tests. This is the user-facing package path aligned with https://github.com/AWaleed-Ahmed/brlcad-python-bindings.

---

### [#16 — Torus family](https://github.com/BRL-CAD/MOOSE/pull/16) · merged 2026-07-26

C + Python support for Torus, EllipticalTorus, and HyperbolicCylinder, plus NonManifoldGeometry-related bridge work and binding updates.

---

### [#17 — Particle and quadrics / halfspace](https://github.com/BRL-CAD/MOOSE/pull/17) · merged 2026-08-01

C and Python coverage for Particle, Paraboloid, Hyperboloid, and Halfspace, with wrapper polish across existing modules.

---

### [#18 — Sketch, Pipe, and companions](https://github.com/BRL-CAD/MOOSE/pull/18) · merged 2026-08-09

Added Unknown, VectorList, Sketch, ParabolicCylinder, and Pipe across C headers/sources and Python wrappers—rounding out a broad primitive surface for the binding layer.

---

### [#19 — Python Wheel](https://github.com/BRL-CAD/MOOSE/pull/19) · unmerged 2026-08-16

Introduced Python wheel support to allow for standard `pip` installation of the bindings. This pull request also included crucial fixes for `VectorList` and `Sketch` to ensure their proper functioning.

---

## Milestones (high level)

| Window | Milestone |
|--------|-----------|
| May 19–30 | Casting fix; Arb8 C API; SetName / SetTitle |
| Jun 2–11 | ConstDatabase growth; Sphere / Ellipsoid / Cone |
| Jun 18–28 | Object/Arb8 completion; Combinations |
| Jul 6–22 | BoT; Python package landed in MOOSE |
| Jul 23–Aug 1 | Torus family; Particle / Paraboloid / Hyperboloid / Halfspace |
| Aug 7–16 | Sketch / Pipe / VectorList / Unknown; Python wheel; demo + final report |

---

## Acknowledgements

I am grateful to Google Summer of Code and to the BRL-CAD community for the chance to contribute to a codebase with real depth and history. Working from Islamabad across mentor time zones taught me to communicate clearly, ship in reviewable slices, and treat every cast and naming choice as part of a public API.

Special thanks to my mentor **Daniel Rossberg** for patient reviews, design guidance, and insisting that the C bridge stay honest to MOOSE semantics. Those comments shaped both the code and how I think about maintainable bindings.

On a personal note: this summer stretched my systems skills like C ABI boundaries, ctypes ownership, CSG structure, and the discipline of upstream review. The project was demanding, and I am proud of the steady sequence of merges from the first casting fix to a usable Python surface on MOOSE. I look forward to staying involved with BRL-CAD beyond GSoC.

---

## Useful links

- BRL-CAD — https://brlcad.org/
- MOOSE — https://github.com/BRL-CAD/MOOSE
- Python bindings (dev) — https://github.com/AWaleed-Ahmed/brlcad-python-bindings
- Daily logs — [May](reports-may-2026.md) · [June](reports-june-2026.md) · [July](reports-july-2026.md) · [August](reports-august-2026.md)
