"""Standalone X11/F11 output continuity probe on the explicit CI audio server."""
import json
from pathlib import Path
import tempfile
import time
import traceback

import numpy as np
from PySide6.QtCore import Qt, QEventLoop, QTimer, QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from soundsausage import storage
from soundsausage.capture import Recorder
from soundsausage.document import Document
from soundsausage.system_audio import SYSTEM_OUTPUT
from soundsausage.window import MainWindow


app = QApplication([])
rate = 44100
samples = storage.allocate((rate*300, 2))
for a in range(0, len(samples), rate):
    t = np.arange(a, min(a+rate, len(samples)))/rate
    samples[a:a+len(t), 0] = .3*np.sin(2*np.pi*997*t)
    samples[a:a+len(t), 1] = .25*np.sin(2*np.pi*1501*t)
window = MainWindow(Document(samples, rate), no_audio=False)
preferences = tempfile.TemporaryDirectory(prefix='soundsausage-fullscreen-preferences-')
window.audio_devices.settings = QSettings(str(Path(preferences.name)/'audio.ini'), QSettings.Format.IniFormat)
errors, takes, states = [], [], []
window.error = lambda title, message: errors.append(str(title)+": "+str(message))
window.player.failed.connect(errors.append)
window.player.state_changed.connect(states.append)
recorder = Recorder(devices=window.audio_devices)
recorder.failed.connect(errors.append)
recorder.finished.connect(takes.append)
try:
    output = next(d for d in window.audio_devices.outputs() if b'soundsausage_test' in bytes(d.id()))
    window.audio_devices.configure(bytes(output.id()).hex(), 100, SYSTEM_OUTPUT)
    window.resize(1180, 720)
    window.show()
    QTest.qWait(100)
    assert recorder.start(rate, 2, limit_seconds=5.5), errors
    QTest.qWait(150)
    window.toggle_play()
    assert window.player.state == 'Playing', errors
    started = time.monotonic()
    stages = set()
    loop = QEventLoop()
    def press_fullscreen():
        # The private X server has no window manager to focus new windows.
        # Deliver F11 to an active window, as with a physical keyboard.
        window.activateWindow()
        app.setActiveWindow(window)
        window.setFocus()
        QTest.keyClick(window, Qt.Key.Key_F11)

    def advance():
        try:
            elapsed = time.monotonic()-started
            if elapsed > .4 and 1 not in stages:
                press_fullscreen()
                assert window.isFullScreen(), 'F11 did not enter fullscreen'
                stages.add(1)
            if elapsed > 1.1 and 2 not in stages:
                press_fullscreen()
                assert not window.isFullScreen(), 'F11 did not leave fullscreen'
                window.resize(3840, 2160)
                stages.add(2)
            if elapsed > 1.9 and 3 not in stages:
                window.waveform.zoom(2)
                stages.add(3)
            if elapsed > 2.7 and 4 not in stages:
                press_fullscreen()
                assert window.isFullScreen(), 'F11 did not re-enter fullscreen'
                stages.add(4)
            if elapsed > 3.5 and 5 not in stages:
                window.waveform.fit()
                press_fullscreen()
                window.resize(1920, 1080)
                stages.add(5)
            if elapsed > 4.2 and 6 not in stages:
                time.sleep(.18)  # Deliberately stop GUI callbacks beyond the 100ms buffer.
                stages.add(6)
            if not recorder.active or time.monotonic()-started > 9:
                loop.quit()
        except Exception as error:
            errors.append(traceback.format_exc())
            loop.quit()
    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(advance)
    recorder.finished.connect(loop.quit)
    timer.start()
    loop.exec()
    timer.stop()
    assert not errors, errors
    assert len(takes) == 1 and not recorder.active, (len(takes), recorder.active)
    assert stages == {1, 2, 3, 4, 5, 6}, stages
    assert window.player.state == 'Playing', states
    data = takes[0].samples
    # Ignore startup/terminal silence. Every interior 5ms block must contain tone
    # on both channels; the original filled polygons leave long silent gaps here.
    block = rate//200
    rms = np.sqrt(np.mean(data[:len(data)//block*block].reshape(-1, block, 2).astype(np.float64)**2, axis=1))
    active = np.flatnonzero(np.all(rms > .02, axis=1))
    assert len(active) > 800, (len(active), rms.max(axis=0))
    interior = rms[active[0]+2:active[-1]-2]
    assert np.all(interior > .02), dict(minimum=interior.min(axis=0).tolist(), quiet_blocks=int(np.count_nonzero(interior < .02)))
    print(json.dumps(dict(fullscreen_audio='OK', stages=sorted(stages),
                          interior_blocks=len(interior), minimum_rms=interior.min(axis=0).tolist(),
                          frames=len(data), buffer_ms=window.audio_devices.buffer_ms)))
finally:
    window.player.stop()
    recorder.stop(keep=False)
    for take in takes:
        take.discard()
    window.document.mark_saved()
    window.session.mark_saved()
    window.close()
    preferences.cleanup()
