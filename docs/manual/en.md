# SoundSausage — manual

Version 0.19.0. An intuitive, easy-to-use audio editor with all the tools where you expect them. This manual covers the complete available workflow, effects and practical limits.

## 1. Language and help

Choose **Options → Language** and select Nederlands, English, Deutsch, Français or Español. Menus, windows, tips and the open manual change immediately. The choice is remembered for the next start. File names, track names and plug-in names retain their original spelling.

**Help → Manual** or **F1** opens this manual offline, alongside the editor. **Ctrl+F** focuses search; **F3** finds the next occurrence and **Shift+F3** the previous one. The previous/next buttons wrap at the ends. Only an explicitly clicked website link needs internet. **About** shows the version, author, license, website and components.

## 2. Quick start and workspace

Open a WAV or MP3 with **File → Open**. Press **Space** to listen or stop. Drag over a fragment, choose **Transform → Amplitude → Normalize**, listen with **Preview**, then confirm with **OK**. **Ctrl+Z** undoes the edit. Use **Save As** to keep a separate result. For several recordings, create a **New Multitrack Session**, import WAV or MP3 files and finish with **Mix Down**.

**Edit Waveform View** edits one recording; **Multitrack View** combines clips. Switch with **Tab**, the top buttons or **View**. Both documents remain available. Tooltips explain buttons; **Show Toolbar Labels** adds text and **Options → Show Status Bar** shows or hides the thin information line at the very bottom, below the level meter. It displays playback state and file details; the choice is remembered for the next start. **F11** toggles full screen. The lower clock follows audio; selection fields show start, end and length, and view fields the visible time range. Red peaks indicate output overload. A star before a document name means unsaved changes.

Windows and graph scales adapt to the desktop font size and chosen language. If a form is too large for the screen, scroll through its settings; confirmation and cancel buttons remain accessible.

Two thin horizontal lines mark the bottom edge of the left channel and the top edge of the right channel. They end at the sides of the waveform plot, also during live recording.

## 3. Files, projects and recovery

**New** creates an empty mono or stereo waveform at the chosen sample rate. **Open** reads WAV and MP3. **Save** updates the current file; **Save As** chooses another name/encoding; **Save Selection** writes only the chosen time and channels. WAV export supports PCM 8/16/24/32-bit and float32. PCM16 is a useful exchange format; float32 also preserves internal peaks above 0 dBFS. Extra bit depth cannot restore lost detail. Ambiguous older 32-bit WAV files ask for PCM or legacy-float interpretation; cancelling leaves the file intact.

WAV text, cues and labels are retained. Cues follow editing, pasting and selection export; the destination title is kept. Recorder-specific fields are preserved verbatim, not recalculated after effects. Extra metadata is limited to 16 MiB; oversized input is rejected and omitted output fields require confirmation. Mixdown does not merge all source markers. Large WAV exports use RF64 when necessary.

**New Multitrack Session**, **Open Session**, **Save Session** and **Save Session As** manage editable projects. A SoundSausage project (`.celp`) contains the audio, clips, lines, track settings, effect order/bypass/tails and VST3 settings. Save a project as well as the final WAV or MP3 to retain separate tracks. Older SoundSausage versions remain readable; newly saved projects need app 0.19.0 or newer. Legacy `.ses` import is limited; use a new SoundSausage project for continued work.

**Close / Ctrl+W** closes the current waveform; in multitrack it is **Close Session**. Save, discard or cancel when asked. The other view and clipboard remain available. **Exit / Ctrl+Q** closes the application and checks unsaved work.

Long files are processed in blocks on disk, without the former 128 MiB limit. Reserve free space for source copies, results and Undo. Sessions are limited to 24 hours and 32 tracks. Long operations show progress and cancellation; cancelling preserves audio, selection, history and the old export target. One applied effect is one Undo step.

After an unexpected exit, recovery offers the latest checkpoint: restore, remove or later. **File → Recover Work** opens retained copies. Original files remain intact; waveform, session, channels, clips, lines and racks return, but Undo starts afresh. Confirmed edits are checkpointed, cursor/selection about once per second. Active instances are skipped. Ordinary save/confirmed close clears that instance's recovery. Keep your own backups; a disk error can leave an older checkpoint.

### MP3 and WAV

Open MP3 files through **File → Open**, import them into multitrack or drag them onto the timeline. All selection, editing and effect tools work on the decoded audio. **Save As**, **Save Selection** and **Mix Down** offer WAV and MP3; the file extension follows the selected format. Saving an existing MP3 uses the chosen MP3 encoding; Save As can make a WAV copy.

MP3 offers 128, 192, 256 and 320 kb/s. Higher bitrates use more space and usually retain more detail. MP3 is lossy: recompression may lose more detail. WAV avoids another MP3 compression step, but cannot recover detail already lost. Use float32 WAV for continued editing or PCM16 for exchange. MP3 export uses the closest of 32,000, 44,100 and 48,000 Hz, preserving duration while the document retains its own rate. Use WAV for selections shorter than 2 ms.

ID3 text and embedded cover images are retained, including through WAV and embedded projects. The duration tag is updated; chapter positions, ReplayGain and other derived tags are not recalculated. Unsupported WAV markers/file data require confirmation before MP3 export. Extra metadata remains limited to 16 MiB; mixdown does not merge all track metadata. Long conversions show progress and can be cancelled without replacing an existing destination. Reserve disk space for conversion and editing.

## 4. Playback, zoom and audio devices

**Space** starts/stops; **P** pauses/resumes; **Esc** stops. A selection plays its range; otherwise playback starts at the cursor. **Loop** repeats that range, with a possible short boundary transition. **Home/End** go to start/end; skip buttons move five seconds. Navigating or applying a waveform edit stops playback. **Zoom In / Zoom Out**, **Ctrl+wheel**, the wheel and horizontal scrollbar navigate the display. **Zoom Full / Ctrl+0** shows everything; **Zoom to Selection / Ctrl+Shift+A** fills the view with the selection. Their icons differ. At close zoom samples join continuously; further out each screen column retains minimum/maximum peaks.

In **Options → Audio Hardware**, select an output or **System Default**; it is remembered and used for playback and Preview. The playback buffer defaults to 100 ms: larger tolerates interruptions, smaller responds faster. Actual device buffers can differ. Changes stop playback/previews. If a device disappears, reconnect or select an available output and restart. Check system volume, route, Mute and Solo when silent. Output-rate conversion does not change the recording.

## 5. Recording

Connect a microphone/interface, choose the recording device in **Audio Hardware**, then press **R**. The setup window selects input, destination, mono/stereo, first input channel and maximum duration. New waveform records separately; insert at cursor or replace selection edits an existing waveform; multitrack adds a new clip on the chosen track at the cursor. A mono input can feed both stereo channels. An existing waveform determines rate/channels; differing input rate is converted after Stop. **Until Stop** continues until stopped or storage is exhausted.

**Start Recording** opens the microphone; nothing opens before that. The live waveform shows the last 20 seconds, the clock the total captured duration and meters the input. **P** pauses/resumes without including paused time. **Stop**, **Esc**, **Space** or **R** keeps the take. Insertion/replacement or a new multitrack clip is one Undo step; a new waveform still needs Save. **Discard Recording** asks before removing only this take. Closing asks to keep, discard or continue. Other edits are locked during recording.

The input is not monitored through speakers. Adjust gain on the interface/microphone or Linux sound settings; clipped input cannot be repaired by lowering it later. Device loss stops and retains captured audio rather than switching microphones. Takes are written in blocks, checkpointed roughly each second. Recovery opens the last checkpoint as a separate waveform. Cancelling conversion after Stop leaves the take available under **Recover Work** and the old document unchanged.

**Skip at start** removes the first input milliseconds once per take to exclude a startup click. The initial value is 50 ms, adjustable from 0 to 500 ms and remembered. At 0 ms the full start is kept; a nonzero cut is followed by a 5 ms fade-in. Removed audio is not recorded. Clock, live view, meters and maximum duration follow retained audio. Pause/resume does not repeat the cut. With backing playback, clip placement accounts for the removed time to retain alignment.

## 6. Selection, channels and editing

Click for a cursor; drag for a time range. In stereo, drag inside L or R to select that channel, across both for stereo. **Channels** or **Edit → Select Channels** changes channels without losing the time range: **Alt+B / Alt+L / Alt+R** choose both/left/right. Shift-click extends the range while retaining channels; double-click selects visible audio in the clicked channel; **Ctrl+A** selects the whole duration of the current channels. Mono has one channel. **Set Selection** enters exact frame positions; at 44,100 Hz, 44,100 frames equal a second. **F4** moves boundaries inward to zero crossings (left when both channels are chosen).

**Cut / Ctrl+X** removes and copies; **Copy / Ctrl+C** copies; **Paste / Ctrl+V** replaces the selection or inserts at the cursor. **Mix Paste / Ctrl+M** adds clipboard audio from that position and may raise peaks. **Delete** removes the range; **Trim / Ctrl+T** keeps only it. **Ctrl+Z / Ctrl+Shift+Z** undo/redo. Pasting converts sample rate, leaving the clipboard intact. With both channels, channel counts must match. Left/right Copy or Save Selection produces mono, while Save/Save As always retains the full stereo waveform.

A stereo waveform shares one timeline: duration-changing edits (cut/delete/trim, Stretch, insertion and added tails) require both channels. A mono paste into one stereo channel must exactly replace that range; Mix Paste must stay inside the existing duration. **Silence** clears one selected channel without moving the other. Pitch Shift, delay, echo, reverb and convolution can change one channel while preserving length. Recording into an existing stereo waveform also requires both channels. Undo/recovery retain channel choice.

### Editing individual samples

Zoom with **+** or **Ctrl+wheel** until square sample points appear (at least eight screen pixels apart). The horizontal axis now shows sample indices starting at 0. Drag a point vertically to change only that sample in that channel. Its sample position stays fixed even when the pointer crosses other points or channels. Dragging previews the change; release commits it, **Escape** cancels. **Shift+drag** still selects audio.

Double-click or right-click a point for **Edit Sample**, or use **Edit → Edit Sample** at any zoom level. It starts at the cursor and first selected channel; the index and channel can be changed. Enter a normalized value or display it as signed 8-, 16- or 24-bit. Zero is silence; −1/+1 are normal full scale. For example, −16384 in the 16-bit display equals −0.5 normalized. Switching display ranges changes neither audio nor file encoding. **OK** applies one value; **Cancel** preserves the original.

Each completed drag or accepted value is one Undo/Redo step. Every other sample, the other channel, duration and metadata remain intact. Dragging is limited to −1 … +1; existing float headroom remains available numerically. Playback stops when editing begins; editing is locked during recording. For multitrack clips, edit a waveform copy and explicitly apply it back to the clip. Listen after each correction: for a click spanning several samples, adjust each point towards the surrounding waveform. An abrupt jump to zero can itself click. Save as WAV float32 for an exact internal-value round trip; MP3 saving recompresses the whole file with loss.

## 7. Applying effects

Waveform effects under **Transform** affect the selected range/channels, or their whole duration without a time selection. The other channel remains unchanged and audible in stereo Preview. **Preview** plays at most the first eight seconds without committing; click again, change a setting or close to stop. **OK** applies one Undo step; **Cancel** preserves the waveform. **F2 / Repeat Last Command** repeats the last settings on the current selection/channels. Some effects analyse the full selection before previewing: Normalize, time/pitch and high-quality distortion.

### Amplitude

**Amplify / Fade** uses initial/final amplification: 100% unchanged, 50% half amplitude, 200% double. Lock left/right ties channels; equal initial/final gives constant gain, untick for a fade. Linear fades can reach zero, logarithmic fades need positive endpoints. Presets include ±6 dB and fades. Direct **Fade In / Fade Out** apply a linear fade immediately. Example: select a quiet introduction, choose a fade-in, preview and confirm.

**Channel Mixer** is stereo only. Each output combines percentages of the original L/R; negatives invert input polarity and output inversion flips the sum. Presets swap channels, copy one to both, average to mono (still two channels) or subtract channels. Mixing can exceed 0 dBFS. A one-channel selection changes only that output, though both originals can feed it.

**Dynamics Processing** maps input dB to output dB. Below the diagonal reduces levels, above boosts. Click/drag points; edit exact values below; right-click, Remove Point or Delete removes interior points. End positions stay fixed. Attack controls response to peaks, Release recovery, Output gain the result. Stereo linking keeps common gain. Start with 3:1 above −18 dB for speech. Compressor reduces loud passages; limiter restrains peaks; gate/expander reduces quiet passages. There is no look-ahead, so slow attack can let transients through.

**Envelope** draws gain over 0–100% of the fragment, with 0–200% amplitude (100% neutral). Click/drag or enter positions/gains; remove interior points. Presets provide fades, both-end fades and a central dip. Logarithmic interpolation needs positive gains. To lower one word, place points around it and draw a dip. This writes audio; multitrack clip lines stay separately editable.

**Normalize** moves the highest peak to a target (default 98%) using one gain factor. It does not equalize words. Equal left/right normalization preserves balance; unlink for independent peaks. DC removal recentres the signal first; silence remains silence. Use after mixing to leave PCM headroom. **Invert** reverses polarity, **Reverse** reverses time, and **Silence** zeros the chosen range without removing time. They apply immediately.

### EQ and filters

Under **Filters**, **Graphic Equalizer** has ten octave bands, 31.5 Hz–16 kHz, each −24…+24 dB. Unusable bands at low sample rates are disabled. Flat resets, Bass lift adds low end, Voice presence emphasizes speech, Gentle smile lightly lifts lows/highs. The graph combines overlapping bands and Output gain (display −36…+36 dB). Boosting can exceed 0 dBFS: lower Output gain before PCM export.

**Parametric Equalizer** has five bell bands plus low/high shelves, individually enabled. Frequency chooses the centre/transition, Gain is −24…+24 dB, and higher Q narrows a bell. Shelves have fixed smooth transitions and no Q control. For a resonance, use a narrow negative bell; for broad tone, use a wide bell/shelf with small gain. Flat/Reset zeros gains; voice clarity and warmth are starting points.

**Filters** offers high-pass (remove low rumble, starts 80 Hz), low-pass (soften highs, starts 8 kHz), band-pass and notch. High/low-pass use Butterworth 12/24/36/48 dB/oct, about −3 dB at cutoff; steeper can ring more. Band-pass/notch use Q. Telephone is a broad band-pass; 50/60 Hz notches remove only the fundamental hum, not its harmonics. Reset restores the rumble preset. Filters keep state between blocks, but start empty at the selection boundary, preserve length and change phase. Abrupt short selections can click; use a wider range.

### Delay, echo and reverb

**Delay Effects → Delay** adds one copy after 1–2,000 ms. Left/mono controls the first delay; unlink channels for a separate right time. Presets include single delay 250 ms, slapback 80 ms, doubling 25 ms and stereo widening. **Echo** repeats via Feedback (0–95%); higher means longer decay. High-frequency damping darkens feedback repeats, not the first copy. Ping-pong alternates stereo repeats. Warm echo and long repeats are useful starts; high feedback can build excessive levels.

**Reverb** uses Room size for reflection spacing, Decay for approximate RT60 (0.1–10 s), Predelay (0–250 ms) before the wet signal, high-frequency damping and stereo width (0 same wet signal both sides, 100 full spread; disabled for mono). Small room, studio, large hall and long ambient presets vary space/decay. For speech start with low Wet, short decay and some predelay. This is algorithmic reverb, not an exact hall model.

Dry and Wet are independent percentages added together; Output gain (−24…+24 dB) scales the sum without automatic limiting. Default length is unchanged: later repeats are cut. Add effect tail inserts 0.01–60 s, shifting following waveform audio and later cues. The last 10 ms fades to silence. Presets untick the tail; set it after choosing one. Suggested tail can exceed the limit with extreme echo; lower feedback/delay. Example: 2 s voice + 3 s tail becomes 5 s. A single stereo channel cannot add time.

### Noise reduction and click repair

Select background-only audio (typically half a second to several seconds), choose **Capture Noise Profile**, then select the audio to clean and reopen **Noise Reduction**. Capture from selection in the dialog also works; capturing changes no audio. A profile averages at most the first 30 s. Minimum duration depends on sample rate; rate/channel count must match. For one selected stereo channel the corresponding profile channel is used. Save/Load Profile uses `.ssnoise`, a spectrum rather than an audio recording. Reuse only for a matching setup.

Maximum reduction is 0–36 dB; begin at 6–12 dB. Sensitivity treats more background as noise; smoothing softens changing suppression but may let noise through after sounds. Stereo linking retains balance. “Keep removed noise only” auditions the removed material: disable it before applying a cleaned result. Gentle/Balanced are useful starts. Best for steady hiss/ventilation; it cannot separate voices or restore lost detail. Excess reduction or a musical profile can damage sound. Length/cues stay fixed; this is offline processing.

**Click Removal** joins undamaged samples around short isolated impulses. Higher threshold multiplier is more conservative; lower minimum jump dBFS detects quieter clicks. Maximum click width is 0.02–2 ms. Conservative, small-click and wider-click presets are starting points. Preview percussion carefully: sharp attacks can resemble damage. Long crackles, clipping and damaged boundary samples need separate treatment.

### Time and pitch

**Time/Pitch → Stretch** changes duration (25–400%) while keeping pitch: 200% doubles length, 50% halves it. Tempo fields calculate old/new BPM (120→100 gives 120%); they do not detect tempo. Cues inside follow the scale; later audio/cues shift by the difference. Stereo requires both channels. **Pitch Shift** changes −24…+24 semitones without changing duration/cues; ±12 is an octave, 0.01 semitone one cent. Formant preservation can keep vocal character; compare both settings for instruments.

Fine (default) and Fast use Rubber Band offline. Stereo is processed jointly; extreme changes can sound artificial. For a real change use at least 50 ms and 64 samples. Neutral settings return original audio exactly; output rounds to whole samples. Preview analyses the whole selection before playing at most eight seconds; long files need analysis time and some analysis memory. Progress is cancellable. For a multitrack clip, edit a waveform copy then apply it back; line positions scale to the new length, following clips do not shift automatically.

### Special effects

**Special → Distortion** offers soft clip (rounded saturation), hard clip (sharp cutoff), wavefold (folds peaks) and bit crush (2–16 bits). Drive is 0–36 dB, Ceiling 10–100%, Effect mix blends original/processed, Output gain −24…+24 dB. Ceiling shapes only the processed part, not dry audio or final output. Soft warmth, crunch, wavefold and bit-crush presets are starts. High quality oversamples to reduce aliasing (usually 4×, adapted at high rates) and processes the whole selection even for Preview; standard is faster/rougher. Length/cues remain fixed; silence stays silent.

**Convolution** applies a WAV impulse response representing a filter, cabinet or acoustic response. Choose the response, set Dry/Wet and preview. Mono responses work per channel; stereo responses need stereo input and use the corresponding selected channel. A different rate is converted; the response is limited after conversion to 10 seconds and 524,288 samples, with a 32 MiB file limit. Empty or silent responses are rejected. A response tail has no extra fade. Normalize impulse energy scales both response channels together; disable for a deliberately calibrated response. Dry 0%, Wet 100% gives a pure filter result. Keep full response tail adds response length minus one sample and shifts later audio/cues. Without it length stays fixed. Keep the response file unchanged for F2; changed/missing files require choosing again.

## 8. Generate, analyse and convert

**Generate → Tones** inserts a sine wave at the cursor or replaces a selection with the specified duration, frequency in Hz and amplitude %. Try 440 Hz at modest level. **Generate → Silence** inserts/replaces with a chosen silence duration; **Transform → Silence** instead preserves the existing duration.

**Analyze → Frequency Analysis / Alt+Z** shows frequency versus dBFS for the selected channels/range (or full recording). It uses a bounded central part of long ranges, a Hann window and channel-power average. The peak frequency/level is shown below. Select a shorter sound to investigate it; this is not a continuous spectrum meter. Closing changes no audio.

**Edit → Convert Sample Rate** converts the entire waveform to the chosen Hz, preserving pitch/duration with whole-frame rounding (at least one frame). Cursor/selection follow the same times. Undo restores audio and rate. This changes the document; automatic playback conversion changes only the output stream.

## 9. Multitrack and automation

Create a session with rate/track count, import WAV using the file menu/import button or drop files from the file manager. Rates are converted; multiple files use successive tracks. **Window → Insert Current Waveform in Multitrack** inserts the open waveform. Add/remove track changes the selected track; Undo restores deleted content. Track names are editable. Mute silences, Solo restricts playback to solo tracks; Mute still wins. Pan −100 is left, 0 centre, +100 right. For stereo it attenuates one side rather than copying channels.

In **Move Clips**, drag the centre to move, edges to trim; trimming retains source audio for later extension. Empty timeline space selects a playback range. **Duplicate Clip / Ctrl+D** shares the source; **Remove Clip / Delete** removes the clip, not its source file. Right-click opens clip commands. **Clip Properties** edits name, timeline/source bounds (seconds), gain, pan, fades and mute; total fades must fit the clip. Cancel leaves it unchanged.

**Volume Line** and **Pan Line** draw points inside clips. Click adds, drag moves, right/double-click opens exact frame/value input, Remove Point/Delete removes the selected point, Reset Line restores neutral. Esc cancels a drag. Volume: bottom 0%, middle 100%, top 200%, multiplying clip/track gain and fades. Pan: top right, middle neutral, bottom left, adding to clip/track pan. Set ordinary pan centre for a full sweep. Points follow source audio when moving/trimming and are saved in the project. Return to Move Clips to move clips again.

Double-click or **Edit Copy in Waveform** opens a clip copy for offline effects. **Window → Apply Waveform to Clip** explicitly returns the result; merely switching views does not apply it. Session Undo restores old audio/lines. Sample rate is converted back, lines scale with changed length, and later clips do not move: check overlaps. **Mix Down Session / Mix Down** exports the entire session, regardless of time selection, with mute/solo, gain/pan, lines, effects and tails. Save Session keeps the editable project. Volume/pan/mute/solo/racks can change during playback; Undo and view changes stop it.

## 10. Realtime track effects, plug-ins and recording

Click **FX** beside a track or **Transform → Track Effects**. Add an effect, choose settings/preset, then OK to confirm or Apply to change it while the window stays open. Edit/double-click reopens settings. Up/Down changes order; the checkmark bypasses; Remove deletes. Changes have Undo/Redo. Up to sixteen effects run after clip gain/lines/fades and before track volume/pan. Mono becomes stereo. Tail after last clip adds 0–60 seconds. Playback and mixdown use the same chain without changing the sources.

Racks offer fixed Amplify, Channel Mixer, Dynamics, Graphic/Parametric EQ, filters, Delay, Echo, Reverb, Invert and external plug-ins. Apply updates while listening; already buffered audio retains old settings. Restart, seek and bypass changes clear effect memory. Normalize, restoration, time/pitch, distortion and convolution remain waveform edits through Edit Copy in Waveform. Use Volume Line for a changing clip gain.

### VST3, LV2 and LADSPA

Install a **64-bit native Linux audio effect**. In Track Effects choose **External Plug-in → Add**, select the format and **Add Plug-in**. Select a `.vst3` bundle, `.lv2` bundle or LADSPA shared library (`.so`). Effects within a bundle appear separately. Choose the effect, search its parameters and change their normalized 0–100% position: 50% need not mean half volume. Discrete parameters have steps; read-only ones stay fixed. Apply auditions on the track; OK confirms/closes.

**Open Plug-in Window** opens a supported VST3 or LV2 custom editor. Its parameters and saveable state are included when confirming. Custom windows require **X11 or XWayland**. General parameter controls remain available if the editor is absent or unsupported; LADSPA always uses these controls. LV2 editors needing a GTK/Qt adapter are not embedded.

VST3 supports one stereo input/output bus with float32 processing. LV2/LADSPA support mono/stereo effects with matching inputs/outputs; mono effects use separate instances per stereo channel. MIDI instruments, extra sidechains, VST2 and Windows plug-ins are unsupported. Missing required LV2 features or port types are reported; MIDI/Atom processing is unavailable. LV2 state requiring external files cannot be saved completely and raises a message: choose an effect with self-contained saveable state.

Each plug-in runs in an isolated helper. Crashes, timeout or invalid audio stop playback while preserving captured recording audio. Projects save parameters and at most 1 MiB state per effect. Install plug-in code and its external libraries/samples separately. On another computer add the same version. Missing/changed plug-ins are reported; playback/export needs a matching effect or deliberate bypass.

### Automatic plug-in delay compensation

Reported algorithmic processing delay is compensated per track in playback and mixdown. Chain delays add together; bypass/settings changes update processing. Timeline positions and mix length remain unchanged. Musical echo, predelay and reverb remain audible. Compensation depends on correct plug-in reporting and allows at most ten seconds per track. Invalid or continuously changing latency raises a message.

### Recording with backing and synchronization

Place backing clips on tracks, select a target track and position the cursor. Press **R**, choose input and a new-clip destination, and enable **Play existing tracks while recording**. Existing tracks and effects play; the input is not monitored through speakers. **P** pauses/resumes both; **Stop/Esc/Space/R** keeps the take as one Undo step. Discard removes only this take. Device/plug-in failure preserves captured audio.

**Automatic synchronization** links placement to the playback clock and measures the difference between input/output clocks. A sufficiently long, reliable measurement gently corrects the duration after Stop. Short or unstable measurements do not stretch the take. This does not measure the physical input/output route.

Use **Options → Calibrate Recording**, or the recording dialog’s calibration button, for that route. Choose the same devices, rate, mono/stereo mode, first input channel and buffer as for recording. Connect output to input with a suitable loopback cable; a microphone near a speaker also works but includes acoustic delay. Start at a low level. **Start Calibration** plays quiet pulses for about six seconds without monitoring the input. Only a reliable result is saved; silence, clipping, ambiguous signals or unstable timing leave an earlier good profile intact. Verify with a short take; calibrate again after changing the device combination or settings.

Automatic synchronization applies the matching device profile. Without a profile clock synchronization still works, but physical delay can remain. For manual adjustment disable automatic and use **Recording position offset**: negative moves earlier, positive later; −15 ms corrects a take arriving 15 ms late. Automatic and manual offsets are exclusive.

### Punch-in/out

Select a target track and a time range on the multitrack ruler or with **Edit → Set Selection**. Choose **Options → Punch In/Out** or **Shift+R**. Set input, synchronization, **Pre-roll** (default 2 s) and **Crossfade** (default 5 ms). The selection fixes the recording bounds and backing is enabled.

The input warms up before playback. Original audio plays during pre-roll. Inside the selected interval only the target track is muted while the replacement is captured; other tracks keep playing. Recording stops automatically after a short synchronization finish. Only corrected audio inside the selection becomes a new clip.

Crossfades blend old/new inside the interval, at most 100 ms. Audio outside remains intact. Original clips retain their sources, with the punched portion covered. Ctrl+Z restores everything in one step. Select an old clip and **Restore Covered Audio** to clear all its covered regions; remove/mute the new take to avoid hearing both. Early Stop keeps only the captured portion inside the interval. Stopping before the interval changes no session audio; the raw take remains under **File → Recover Work**. Recovery of an uncommitted recording offers the raw take, including pre/post-roll, for manual placement. Completed punch regions survive project saves and crash recovery.

**Save Session / Save Session As** retains sources, clips, lines, chains, plug-in state and punch regions; Open Session restores them. Mix Down exports WAV or MP3 through the same effects. Keep the project for separate-track editing. Newly saved projects need SoundSausage **0.19.0 or newer**; earlier project versions remain readable. Missing plug-ins do not prevent opening/recovering source audio.

## 11. Recording with backing tracks

Place backing clips on tracks, select a different target track and position the cursor. Press **R**, select input and a new-clip destination, enable “Play existing tracks while recording”. Existing tracks and effects play from the cursor; input is not sent to speakers. **P** pauses/resumes both; **Stop/Esc/Space/R** stops both and keeps the take as one Undo step. Recording can continue after the backing ends; a maximum duration stops both. Discard removes only this take. Device/plug-in failure retains captured samples. Document edits are locked during recording.

“Recording position offset” adjusts the inserted clip: negative earlier, positive later. If a take is 15 ms late, try −15 ms. Record a known click through your actual input/output route, compare positions, enter the difference and verify with a second take. Recalibrate after changing devices/buffer. Audio before timeline zero is trimmed on insertion. Offset is remembered, but automatic physical calibration, drift correction between clocks, plug-in delay compensation and punch-in/out remain work in progress. Check a short take before a long session.

## 12. Shortcuts, favourites and troubleshooting

**Favorites** provides repeat, normalize and fades; custom lists are not yet available. **Window** switches views and transfers waveforms/clips. Most common shortcuts are listed below; when typing in a field, keys belong to that field. Click the waveform/timeline before transport/edit shortcuts.

| Keys | Action |
| --- | --- |
| Ctrl+N / Ctrl+O | New / open in current view |
| Ctrl+S / Ctrl+Shift+S | Save / save as |
| Ctrl+Alt+N / Ctrl+Alt+O / Ctrl+Alt+S | New / open / save session |
| Ctrl+W / Ctrl+Q | Close document / exit |
| Ctrl+Z / Ctrl+Shift+Z | Undo / redo |
| Ctrl+X / Ctrl+C / Ctrl+V | Cut / copy / paste |
| Ctrl+M / Ctrl+T / Delete | Mix Paste / trim / remove |
| Ctrl+A / F4 | Select whole duration / zero crossings |
| Alt+B / Alt+L / Alt+R | Both / left / right channels |
| Space / P / Esc / R | Play-stop / pause / stop / record |
| Home / End / + / − | Start / end / zoom in / out |
| Ctrl+0 / Ctrl+Shift+A | Full / selection zoom |
| Ctrl+D / Tab / F11 | Duplicate clip / change view / full screen |
| F1 / F2 / Alt+Z | Manual / repeat effect / frequency analysis 

No input: check chosen device/channel and Linux microphone level, reconnect then start a new take. No output: check routing, volume, mute/solo and Audio Hardware. Distortion/red peaks: lower summed gain and normalize before PCM; Mix Paste and overlapping clips add. Paste rejected: check channel count or exact mono replacement length. Effect disabled: open a waveform/copy; Channel Mixer needs stereo, time-changing edits need both channels. Moving points instead of clips: choose Move Clips. Disk full: free space for copies/results/Undo without deleting active work files. Damaged recovery: original files remain; remove a copy only if no longer needed.

Work in progress includes custom favourites and a marker editor. Realtime chains, Linux VST3 and recording with backing are available as described above. Save your project before leaving. Updates: [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
