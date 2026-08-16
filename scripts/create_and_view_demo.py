#!/usr/bin/env python3
"""
GSoC 2026 demo helper — create a BRL-CAD .g database and open it in MGED.

What this script does
---------------------
1. Builds a small CSG scene (sphere + box + torus region) into a .g file via MGED.
2. Optionally exercises the MOOSE Python bindings (create primitives in-memory,
   then Load/inspect the .g file) when libbrlcad.so is available.
3. Launches MGED so you can take screenshots for the final report.

Usage
-----
  python3 create_and_view_demo.py
  python3 create_and_view_demo.py --out ~/Desktop/gsoc_demo.g
  python3 create_and_view_demo.py --no-mged          # only create the .g
  python3 create_and_view_demo.py --skip-bindings    # skip Python binding smoke test

Environment
-----------
  MGED         path to mged (default: mged on PATH, or BRL-CAD install below)
  LD_LIBRARY_PATH should include moose build/src if you want the bindings check
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_MGED_CANDIDATES = [
    os.environ.get("MGED", ""),
    shutil.which("mged") or "",
    "/home/home/brlcad-dev/brlcad_install/bin/mged",
    "/usr/brlcad/bin/mged",
]

DEFAULT_LIB_PATHS = [
    "/home/home/brlcad-dev/moose/build/src",
    "/home/home/brlcad-dev/moose_install/lib",
]


def find_mged() -> str:
    for candidate in DEFAULT_MGED_CANDIDATES:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise FileNotFoundError(
        "Could not find mged. Install BRL-CAD or set MGED=/path/to/mged"
    )


def ensure_ld_library_path() -> None:
    parts = [p for p in os.environ.get("LD_LIBRARY_PATH", "").split(":") if p]
    for path in DEFAULT_LIB_PATHS:
        if Path(path).is_dir() and path not in parts:
            parts.insert(0, path)
    os.environ["LD_LIBRARY_PATH"] = ":".join(parts)


def create_geometry_database(out_path: Path, mged: str) -> None:
    """Create a polished demo .g file using MGED's command interface."""
    if out_path.exists():
        out_path.unlink()

    # MGED script: units mm, named primitives, a region, draw for wireframe view
    script = f"""units mm
title GSoC 2026 Python Bindings Demo — Abdullah Waleed Ahmed
in ball.s sph 0 0 0 40
in box.s rpp -60 -20 -25 25 -20 20
in torus.s tor 80 0 0 0 0 1 30 8
r scene.r u ball.s u box.s u torus.s
attr set scene.r rgb 70/140/220
B scene.r
ae 35 25
"""

    print(f"[1/3] Creating database with MGED:\n      {out_path}")
    proc = subprocess.run(
        [mged, "-c", str(out_path)],
        input=script,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0 and not out_path.exists():
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise RuntimeError(f"MGED failed to create {out_path}")

    size = out_path.stat().st_size
    print(f"      OK — wrote {size} bytes")


def smoke_test_python_bindings(out_path: Path) -> None:
    """Create primitives via MOOSE Python wrappers and Load the .g file."""
    ensure_ld_library_path()

    # Prefer the working tree package if present
    candidates = [
        Path("/home/home/Documents/work/Python/main-brlcad"),
        Path("/tmp/brlcad-python-bindings"),
    ]
    for root in candidates:
        if (root / "brlcad" / "__init__.py").is_file():
            sys.path.insert(0, str(root))
            break

    try:
        from brlcad import Sphere, Arb8, Torus, ConstDatabase
    except Exception as exc:  # noqa: BLE001 — demo helper; any bind/load failure is skippable
        print(f"[2/3] Python bindings skipped ({type(exc).__name__}): {exc}")
        print("      Tip: rebuild MOOSE so libbrlcad.so matches _bindings.py, then re-run.")
        return

    print("[2/3] Exercising MOOSE Python bindings…")
    ball = Sphere((0.0, 0.0, 0.0), 40.0)
    ball.SetName("ball.s")
    print(f"      Sphere  name={ball.GetName()!r}  type={ball.GetType()!r}  "
          f"radius={ball.GetRadius()}  valid={ball.IsValid()}")

    box = Arb8((-60.0, -25.0, -20.0), (-20.0, 25.0, 20.0), is_rpp=True)
    box.SetName("box.s")
    print(f"      Arb8    name={box.GetName()!r}  type={box.GetType()!r}  "
          f"vertices={box.GetVertexCount()}  valid={box.IsValid()}")

    ring = Torus((80.0, 0.0, 0.0), (0.0, 0.0, 1.0), 30.0, 8.0)
    ring.SetName("torus.s")
    print(f"      Torus   name={ring.GetName()!r}  type={ring.GetType()!r}  "
          f"valid={ring.IsValid()}")

    with ConstDatabase() as db:
        if not db.Load(str(out_path)):
            print(f"      WARNING: could not Load({out_path})")
            return
        print(f"      Loaded .g title: {db.Title()!r}")
        for name in ("ball.s", "box.s", "torus.s", "scene.r"):
            obj = db.Get(name)
            if obj is None:
                print(f"      Get({name!r}) → None")
            else:
                print(f"      Get({name!r}) → type={obj.GetType()!r} name={obj.GetName()!r}")


def open_in_mged(out_path: Path, mged: str) -> None:
    """Open MGED on the demo database and draw the top-level region."""
    print(f"[3/3] Opening MGED — take your screenshots, then close the window.")
    print("      If the view looks empty, type in MGED:")
    print("        B scene.r")
    print("        ae 35 25")
    print("        Z")
    print("        rt     # optional raytrace preview")

    env = os.environ.copy()
    brlcad_bin = str(Path(mged).parent)
    env["PATH"] = brlcad_bin + os.pathsep + env.get("PATH", "")

    # Pre-draw via -c, then reopen GUI on the same database.
    # (MGED remembers display lists inconsistently across modes, so we also
    # print the manual draw commands above.)
    subprocess.run(
        [mged, "-c", str(out_path)],
        input="B scene.r\nae 35 25\nZ\n",
        text=True,
        capture_output=True,
        env=env,
    )

    # Interactive GUI session (blocks until you close MGED)
    subprocess.run([mged, str(out_path)], env=env, check=False)

    print("\nScreenshot checklist — drop files into images/:")
    print("  1. mged-wireframe.png     (wireframe of scene.r)")
    print("  2. mged-raytrace.png      (optional rt preview)")
    print("  3. python-demo-terminal.png (this script's terminal output)")
    print("  4. architecture-moose-stack.png (export from mermaid.live)")
    print(f"  Database path: {out_path}")


def parse_args() -> argparse.Namespace:
    report_default = Path(
        "/home/home/Documents/Internships and Jobs stuff/"
        "gsoc-report-python-bindings/images/gsoc_demo_scene.g"
    )
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=report_default, help="Output .g path")
    p.add_argument("--no-mged", action="store_true", help="Create .g only; do not open MGED")
    p.add_argument("--skip-bindings", action="store_true", help="Skip Python bindings smoke test")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out = args.out.expanduser().resolve()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    mged = find_mged()
    print(f"Using MGED: {mged}")

    create_geometry_database(args.out, mged)

    if not args.skip_bindings:
        smoke_test_python_bindings(args.out)
    else:
        print("[2/3] Skipping Python bindings smoke test")

    if args.no_mged:
        print("[3/3] Skipping MGED launch (--no-mged)")
        print(f"Open manually with:\n  {mged} {args.out}")
        return 0

    open_in_mged(args.out, mged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
