"""Generate original synthetic demonstration audio; no supplied recordings are used."""
from pathlib import Path
import numpy as np
from soundsausage.audio import write_wav
from soundsausage.audio import tone
from soundsausage.session import Session
from soundsausage.project import save_project

rate = 44100
frames = round(8.727 * rate)
t = np.arange(frames) / rate
rng = np.random.default_rng(1997)
envelope = np.minimum(1, np.maximum(0, np.sin(2 * np.pi * 1.1 * t) + 0.6))
voice = np.sin(2 * np.pi * 155 * t + 5 * np.sin(2 * np.pi * 3.4 * t))
voice += 0.4 * np.sin(2 * np.pi * 311 * t)
voice += 0.12 * rng.standard_normal(frames)
left = np.clip(voice * envelope * 0.45, -0.95, 0.95)
right = np.clip(np.roll(voice, 19) * np.roll(envelope, 150) * 0.42, -0.95, 0.95)
audio = np.column_stack((left, right)).astype(np.float32)
path = Path(__file__).resolve().parents[1] / "build/demo.wav"
path.parent.mkdir(exist_ok=True)
write_wav(path, audio, rate, "pcm16")
print(path)

session = Session(rate)
main = session.import_audio([(audio, rate, "Main waveform")], session.tracks[0].id, 0)[0]
session.configure_clip(main, gain=0.65, fade_in=round(0.15 * rate), fade_out=round(0.35 * rate))
tone_id = session.import_audio([(tone(2, rate, 1, 440, 0.22), rate, "440 Hz tone")], session.tracks[1].id, round(1.25 * rate))[0]
session.configure_clip(tone_id, pan=-0.5, fade_in=round(0.2 * rate), fade_out=round(0.2 * rate))
again = session.duplicate_clip(tone_id)
session.move_clip(again, round(4.25 * rate))
stereo = tone(3, rate, 2, 660, 0.12)
stereo_id = session.import_audio([(stereo, rate, "Stereo layer")], session.tracks[2].id, round(2.5 * rate))[0]
session.configure_clip(stereo_id, pan=0.25, fade_in=round(0.3 * rate), fade_out=round(0.4 * rate))
session.configure_track(session.tracks[0].id, name="Main")
session.configure_track(session.tracks[1].id, name="Tones", gain=0.75)
session.configure_track(session.tracks[2].id, name="Layer", gain=0.8)
session.selected_clip = None
session.select(0, 0)
project = path.with_name("demo-multitrack.celp")
save_project(session, project)
print(project)
