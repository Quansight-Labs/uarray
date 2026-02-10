#!/usr/bin/env python3

import os
from pathlib import Path
import shutil

def main():
    project_dir = Path(__file__).resolve().parents[1]
    source_version_path = project_dir / "src" / "uarray" / "_version.py"
    if source_version_path.exists():
        namespace = {}
        with open(source_version_path, "r", encoding="utf-8") as f:
            exec(f.read(), namespace)
        print(namespace["__version__"])
    else:
        import versioningit
        vig = versioningit.Versioningit.from_project_dir(project_dir)
        print(vig.get_version(write=True, fallback=True))

    if meson_dist_root := os.environ.get("MESON_DIST_ROOT"):
        staged_version_path = Path(meson_dist_root) / "src" / "uarray" / "_version.py"
        shutil.copy(source_version_path, staged_version_path)

if __name__ == "__main__":
    main()
