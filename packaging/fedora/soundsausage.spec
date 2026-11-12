Name:           soundsausage
Version:        %{ss_version}
Release:        1%{?dist}
Summary:        Intuïtieve audio-editor met vertrouwde gereedschappen
License:        GPL-3.0-or-later
URL:            https://github.com/rene-timmermans/SoundSausage
Source0:        soundsausage-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
Requires:       python3 >= 3.12
Requires:       python3-pyside6 >= 6.8
Requires:       qt6-qtmultimedia
Requires:       qt6-qttranslations
Requires:       python3-numpy
Requires:       python3-mutagen
Requires:       /usr/bin/ffmpeg
Requires:       rubberband-libs >= 3.3
Requires:       libsamplerate
Requires:       lilv
Requires:       libX11
Requires:       xcb-util-cursor
%global __brp_python_bytecompile %{nil}
%global __requires_exclude_from ^/usr/lib/soundsausage/src/.*$

%description
Een intuïtieve, eenvoudig te gebruiken audio-editor met alle tools op de plek
waar je ze verwacht.

%prep
%setup -q

%build
%make_build

%install
sh packaging/stage.sh %{buildroot}

%files
/usr/bin/soundsausage
/usr/lib/soundsausage/
%{_datadir}/applications/soundsausage.desktop
%{_datadir}/icons/hicolor/256x256/apps/soundsausage.png
%{_docdir}/soundsausage/
%{_datadir}/licenses/soundsausage/
