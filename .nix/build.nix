{ pkgs ? import <nixpkgs> { }
, pythonPackages ? pkgs.python36Packages
}:

pythonPackages.buildPythonPackage rec {
  pname = "uarray";
  version = "0.4";
  format = "flit";

  src = ../.;

  checkInputs = with pythonPackages; [ pytest nbval pytestcov numba ];
  propagatedBuildInputs = with pythonPackages; [ matchpy numpy astunparse typing-extensions black ];

  checkPhase = ''
    ${pythonPackages.python.interpreter} extract_readme_tests.py
    pytest
  '';

  meta = with pkgs.lib; {
    description = "Universal array library";
    homepage = https://github.com/Quansight-Labs/uarray;
    license = licenses.bsd0;
    maintainers = [ maintainers.costrouc ];
  };
}
