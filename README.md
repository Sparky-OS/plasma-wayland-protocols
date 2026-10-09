<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/sparky-stereo-os/sparkyos-swirl-light-128.png">
  <img src=".github/sparky-stereo-os/sparkyos-swirl-dark-128.png" alt="SparkyOS" width="128" height="128">
</picture>

## Sparky Stereo OS

This is the stereo version of Plasma Wayland Protocols by Sparky Stereo OS, forked from [KDE/plasma-wayland-protocols](https://github.com/KDE/plasma-wayland-protocols).
It adds protocols for stereo outputs and for surfaces that declare stereo content, and a small C library with which X11 and Wayland programs make that declaration.

Where it comes from:

- [Plasma Wayland Protocols](https://invent.kde.org/libraries/plasma-wayland-protocols) is made by the KDE community. Its authors include Martin Gräßlin, Aleix Pol Gonzalez, Sebastian Kügler, Marco Martin and Xaver Hugl.
- [Debian](https://www.debian.org/) is the base of the system.
- [SparkyLinux](https://sparkylinux.org/), by Paweł "pavroo" Pijanowski, builds on Debian.
- [Sparky Stereo OS](https://github.com/Sparky-OS/sparky-stereo-os) is the stereo 3D edition of SparkyLinux: SparkyOS, powered by Debian.

The `stereo3d` branch holds the version the distribution builds.
KDE develops Plasma Wayland Protocols on invent.kde.org.
The canonical version of this work is there too, on the [`stereo3d-6.7`](https://invent.kde.org/danielcamposramos/plasma-wayland-protocols/-/tree/stereo3d-6.7) branch.
The licences are unchanged; see [COPYING.LIB](COPYING.LIB) and [LICENSES](LICENSES).

Sparky Stereo OS, Daniel Ramos's edition of SparkyLinux (by Paweł "pavroo" Pijanowski).

---

# Plasma Wayland Protocols

This project provides the xml files of the non-standard wayland
protocols we use in Plasma.

They are installed to $PREFIX/share/plasma-wayland-protocols.

## Usage
You can get the directory where they're installed by using

    find_package(PlasmaWaylandProtocols)

Then they can be accessed using `${PLASMA_WAYLAND_PROTOCOLS_DIR}`.

You can learn more about such protocol files in
https://wayland.freedesktop.org/docs/html/ch04.html.
