"""Run a real F11/X11 render and recorded-output probe on private CI devices."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(os.environ.get('SOUNDSAUSAGE_AUDIO_TEST') == '1',
                     'private virtual audio server not enabled')
class FullscreenBackendTests(unittest.TestCase):
    def test_fullscreen_resize_and_zoom_keep_output_continuous(self):
        with tempfile.TemporaryDirectory(prefix='soundsausage-fullscreen-config-') as config:
            environment = dict(os.environ, QT_QPA_PLATFORM='xcb', XDG_CONFIG_HOME=config)
            result = subprocess.run([sys.executable, str(Path(__file__).parent/'fixtures/fullscreen_audio.py')],
                                    env=environment, capture_output=True, text=True, timeout=60)
        if result.returncode:
            print(result.stdout+'\n'+result.stderr, flush=True)
        self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)
        self.assertIn('"fullscreen_audio": "OK"', result.stdout)
        print(result.stdout.strip())
