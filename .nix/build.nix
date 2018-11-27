{ pkgs ? import <nixpkgs> { }
, pythonPackages ? pkgs.python36Packages
}:

rec {
  uarray = pythonPackages.buildPythonPackage rec {
    pname = "uarray";
    version = "0.4";
    format = "flit";

    src = with builtins; filterSource
        (path: _:
           !elem (baseNameOf path) [".git" "result" ".nix"])
        ../.;

    checkInputs = with pythonPackages; [
      pytest nbval pytestcov numba mypy
    ];
    propagatedBuildInputs = with pythonPackages; [
      matchpy numpy astunparse typing-extensions black
    ];

    checkPhase = ''
      # static type checking
      mypy uarray
      # build python source from readme
      ${pythonPackages.python.interpreter} extract_readme_tests.py
      pytest
    '';

    meta = with pkgs.lib; {
      description = "Universal array library";
      homepage = https://github.com/Quansight-Labs/uarray;
      license = licenses.bsd0;
      maintainers = [ maintainers.costrouc ];
    };
  };
}
