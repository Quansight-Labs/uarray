{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python3Packages }:

pkgs.mkShell {
  buildInputs = with pythonPackages; [
    pytest nbval pytestcov numba # test packages
    matchpy numpy astunparse typing-extensions black # propagated packages
  ];

  shellHook = ''
    echo "uarray virtualenv created"
  '';
}
