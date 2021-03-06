# Eolie

Eolie is a new GNOME web browser.

- For users: https://wiki.gnome.org/Apps/Eolie

- For translators: https://hosted.weblate.org/projects/gnumdk

It provides:
- Firefox Sync support
- Secret password store
- A modern UI

## Depends on

- gtk3 >= 3.22
- gobject-introspection
- python3
- meson >= 0.40
- python (make)
- python-cairo
- python-dateutil
- python-gobject
- python-sqlite
- WebKit2GTK >= 2.16
- Webkit introspection support

## Special python modules
For full support, please install these Python modules:
```
# pip3 install requests-hawk PyFxA pycrypto beautifulsoup4 cryptography
```

## For packagers
Full list of dependencies here: https://github.com/flathub/org.gnome.Eolie

## Building from Git

```
$ git clone https://gitlab.gnome.org/World/eolie.git
$ cd eolie
$ meson build
$ sudo ninja -C build install
```

### On Ubuntu

```
$ git clone https://gitlab.gnome.org/World/eolie.git
$ cd eolie
$ sudo apt-get install gir1.2-gtkspell3-3.0 libglib2.0-dev libgirepository1.0-dev libgtk-3-dev python-gobject-dev python3-dev libwebkit2gtk-4.0-dev gir1.2-webkit2-4.0 autoconf-archive python3-dateutil
$ meson build
$ sudo ninja -C build install
```

Instead of `make install` you might want to use `checkinstall`

```
# apt-get install checkinstall
# checkinstall
```

This will allow you to uninstall Eolie as a package, for example with `apt-get uninstall eolie`.

### On Fedora

```
$ git clone https://gitlab.gnome.org/World/eolie.git
$ cd eolie
$ sudo dnf install autoconf glib2-devel intltool yelp-tools gtk3-devel gobject-introspection-devel python3 itstool pygobject3-devel python3-devel webkitgtk4-devel gtkspell3 python3-dateutil meson
$ meson build
$ sudo ninja -C build install
```
