# Nix Development Workflow

Nix works differently than other development workflows but has much to
offer. Installation is [simple on OSX and all linux distributions](https://nixos.org/nix/download.html) and will not conflict with other package managers.

 - all builds/tests/commands are run isolated
 - can fix version of dependencies and tests dependencies
 - idempodent (if code doesn't change no need to rebuild or run tests)
 
Currently waiting for a [PR #51080](https://github.com/NixOS/nixpkgs/pull/51080 ) to be merged which adds necissary packages.

## Run all tests and build package

```bash
nix-build .nix/build.nix -A uarray
```
