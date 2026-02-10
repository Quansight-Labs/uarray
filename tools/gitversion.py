#!/usr/bin/env python3

from pathlib import Path
import versioningit

def main():
    project_dir = Path(__file__).parents[1]
    vig = versioningit.Versioningit.from_project_dir(project_dir)
    print(vig.get_version(write=True, fallback=False))


if __name__ == "__main__":
    main()
