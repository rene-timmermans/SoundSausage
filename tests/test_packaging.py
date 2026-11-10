"""Check the staged application without using the source tree as an import path."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_staged_install_runs_from_an_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary) / "stage"
            subprocess.run(["sh", "packaging/stage.sh", str(stage)], cwd=ROOT, check=True)
            app = stage / "usr/lib/soundsausage"
            self.assertFalse(list(app.rglob("__pycache__")))
            self.assertTrue(os.access(stage / "usr/bin/soundsausage", os.X_OK))
            self.assertTrue((stage / "usr/share/licenses/soundsausage/LICENSE").is_file())
            env = os.environ | {"PYTHONPATH": str(app / "src"), "PYTHONDONTWRITEBYTECODE": "1", "QT_QPA_PLATFORM": "offscreen"}
            result = subprocess.run([sys.executable, "-m", "soundsausage", "--selftest"],
                cwd=temporary, env=env, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("selftest OK", result.stdout)
