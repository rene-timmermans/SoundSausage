#!/bin/sh
# Run from the source root after make; writes only inside the supplied package tree.
set -eu
destination=${1:?Usage: packaging/stage.sh DESTINATION}
install -d "$destination/usr/lib/soundsausage/src" "$destination/usr/lib/soundsausage/build"
cp -R src/soundsausage "$destination/usr/lib/soundsausage/src/"
find "$destination/usr/lib/soundsausage/src" -type d -name __pycache__ -prune -exec rm -rf {} +
install -m755 build/libsoundsausage_dsp.so "$destination/usr/lib/soundsausage/build/"
install -m755 build/libsoundsausage_vst3.so "$destination/usr/lib/soundsausage/build/"
install -Dm644 third_party/vst3/pluginterfaces/LICENSE.txt "$destination/usr/share/licenses/soundsausage/VST3-MIT.txt"
install -Dm755 packaging/soundsausage-launcher.sh "$destination/usr/bin/soundsausage"
install -Dm644 packaging/soundsausage.desktop "$destination/usr/share/applications/soundsausage.desktop"
install -Dm644 src/soundsausage/assets/soundsausage.png "$destination/usr/share/icons/hicolor/256x256/apps/soundsausage.png"
install -Dm644 README.md "$destination/usr/share/doc/soundsausage/README.md"
install -Dm644 docs/AMPLITUDE.md "$destination/usr/share/doc/soundsausage/AMPLITUDE.md"
install -Dm644 docs/HANDLEIDING.md "$destination/usr/lib/soundsausage/docs/HANDLEIDING.md"
install -Dm644 docs/HANDLEIDING.md "$destination/usr/share/doc/soundsausage/HANDLEIDING.md"
if [ -f LICENSE ]; then
    install -Dm644 LICENSE "$destination/usr/share/licenses/soundsausage/LICENSE"
fi
