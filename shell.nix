{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "ars-shell";

  buildInputs = [
    pkgs.python3
    pkgs.mdbtools
    pkgs.gnumake # optional: for helper scripts
  ];

  shellHook = ''
    echo ">> Entering Nix Shell with Python and MDBTools..."

    if [ ! -d .venv ]; then
      echo ">> Creating virtualenv in .venv"
      python3 -m venv .venv
    fi

    source .venv/bin/activate

    # Install requirements if not already installed
    if [ -f requirements.txt ]; then
      if ! pip freeze | grep -q requests; then
        echo ">> Installing Python packages from requirements.txt"
        pip install --upgrade pip
        pip install -r requirements.txt
      fi
    else
      echo ">> No requirements.txt found — skipping pip install"
    fi

    echo ">> Virtualenv activated ✔"
  '';
}
