"""Prepares the interface for the app: local libraries (works without internet).
AutoSculpt Studio - © 2026 Enrico Migliorati. All rights reserved.

Usage: python prepare_ui.py <source AutoSculptStudio.html> <destination ui folder> <version>
"""
import sys
from pathlib import Path

REPLACE = {
    "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js": "/vendor/three/build/three.module.js",
    "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/": "/vendor/three/examples/jsm/",
}


def main():
    src, dest, version = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    html = src.read_text(encoding="utf-8")
    for a, b in REPLACE.items():
        if a in html:
            html = html.replace(a, b)
        elif b not in html:   # (the published page already has the local addresses)
            sys.exit(f"Warning: {a} not found in the interface")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / src.name).write_text(html, encoding="utf-8")
    (dest / "VERSION").write_text(version + "\n")
    print("Interface ready:", dest / src.name)


if __name__ == "__main__":
    main()
