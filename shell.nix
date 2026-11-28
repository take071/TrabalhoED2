{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "globalsim-ed2-env";
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.flask
  ];

  shellHook = ''
    echo "=========================================="
    echo "   Ambiente GlobalSIM - ED2 Carregado!   "
    echo "   Python: $(python3 --version)           "
    echo "   Para rodar a aplicação:               "
    echo "     python3 app.py                       "
    echo "=========================================="
  '';
}

