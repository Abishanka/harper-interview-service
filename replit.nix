{pkgs}: {
  deps = [
    pkgs.libuv
    pkgs.glibcLocales
    pkgs.rustc
    pkgs.cargo
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cacert
  ];
}
