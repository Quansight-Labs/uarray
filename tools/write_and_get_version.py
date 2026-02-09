import versioningit

def main():
    vig = versioningit.Versioningit.from_project_dir(".")
    print(vig.get_version(write=True, fallback=False))


if __name__ == "__main__":
    main()
