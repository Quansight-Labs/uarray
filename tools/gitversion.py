#!/usr/bin/env python3

import os
from pathlib import Path
import shutil
import versioningit

def main():
    sdist_version_path = Path(os.environ.get("MESON_DIST_ROOT", ".")) / "_version.py"
    project_dir = Path(__file__).parents[1]
    version_path = project_dir / "src/uarray/_version.py"
    vig = versioningit.Versioningit.from_project_dir(project_dir)
    print(vig.get_version(write=True, fallback=True))
    if sdist_version_path.exists():
        shutil.copy(sdist_version_path, version_path)
    if version_path.exists():
        shutil.copy(version_path, sdist_version_path)


if __name__ == "__main__":
    main()
