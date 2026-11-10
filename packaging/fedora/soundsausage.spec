Name:           soundsausage
Version:        %{ss_version}
Release:        1%{?dist}
Summary:        Waveform and multitrack audio editor
License:        GPL-3.0-or-later
URL:            https://github.com/rene-timmermans/SoundSausage
Source0:        soundsausage-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
Requires:       python3 >= 3.12
Requires:       python3-pyside6 >= 6.8
Requires:       python3-numpy
Requires:       /usr/bin/ffplay
%global __brp_python_bytecompile %{nil}
%global __requires_exclude_from ^/usr/lib/soundsausage/src/.*$

%description
Edit WAV recordings, mix audio tracks and apply amplitude effects.
Includes channel mixing, dynamics processing and editable volume envelopes.

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
