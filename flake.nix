{
  description = "A replacement for SteelSeries GG software, to manage your Arctis device on Linux!";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;
      in
      {
        packages.default = pythonPackages.buildPythonApplication {
          pname = "linux-arctis-manager";
          version = "2.3.0-dev";
          pyproject = true;

          src = ./.;

          postPatch = ''
            substituteInPlace pyproject.toml \
              --replace-fail 'uv_build>=0.10.9' 'uv_build>=0.10.0'
          '';

          nativeBuildInputs = [
            pkgs.qt6.wrapQtAppsHook
          ];

          build-system = [
            pythonPackages.uv-build
            pythonPackages.setuptools
          ];

          dependencies = with pythonPackages; [
            dbus-next
            pulsectl
            pyside6
            pyudev
            pyusb
            ruamel-yaml
          ];

          # pyside6 and other libs might need these
          buildInputs = [
            pkgs.libusb1
            pkgs.libpulseaudio
            pkgs.qt6.qtbase
          ];

          dontWrapQtApps = true;

          makeWrapperArgs = [
            "\${qtWrapperArgs[@]}"
            "--prefix LD_LIBRARY_PATH : ${pkgs.libusb1}/lib"
            "--prefix LD_LIBRARY_PATH : ${pkgs.libpulseaudio}/lib"
          ];

          meta = with pkgs.lib; {
            description = "A replacement for SteelSeries GG software, to manage your Arctis device on Linux!";
            homepage = "https://github.com/haysidney/Linux-Arctis-Manager";
            license = licenses.gpl3;
            platforms = platforms.linux;
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            uv
            libusb1
            libpulseaudio
            qt6.qtbase
            qt6.wrapQtAppsHook
          ] ++ (with pythonPackages; [
            dbus-next
            pulsectl
            pyside6
            pyudev
            pyusb
            ruamel-yaml
          ]);

          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.libusb1}/lib:${pkgs.libpulseaudio}/lib:$LD_LIBRARY_PATH
          '';
        };
      }
    );
}
