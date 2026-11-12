# VST3 interfaces

The interface files in `pluginterfaces/` are from
https://github.com/steinbergmedia/vst3_pluginterfaces at commit
`4f547e8e102b47de4a8b8aaf343c73b700786372` (VST3 3.8 interfaces).
Only the host's include dependencies and base UID implementation are included,
including the plug-in view, Linux run loop, content scaling and keyboard interfaces.
Their MIT license is in `pluginterfaces/LICENSE.txt` and is installed alongside
the application's GPL-3.0-or-later license. No VST2 SDK is included.

Local change: `base/funknown.cpp` uses an unsigned temporary for `%2x` parsing
in `fromString8`, matching the C format type and removing a compiler warning.

VST is a trademark of Steinberg Media Technologies GmbH.
The generic parameter editor and host integration are part of SoundSausage.
