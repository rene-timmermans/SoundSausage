"""Interrupted input is kept separately from editor recovery and source WAV files."""
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage.capture import Take,recover_take
from soundsausage.errors import AudioError
from soundsausage.recovery import candidates,collect_orphans,discard

ROOT=Path(__file__).resolve().parents[1]


class TakeRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build');self.path=Path(self.folder.name)
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.path/'work')});self.env.start()
    def tearDown(self):self.env.stop();gc.collect();self.folder.cleanup()

    def crash(self):
        code='''
import os
import numpy as np
from soundsausage.capture import Take
x=Take(48000,2,'USB microphone')
x.append(np.full((500,2),.25,np.float32));x.checkpoint()
x.append(np.full((20,2),.75,np.float32))
os._exit(19)
'''
        result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True)
        self.assertEqual(result.returncode,19,result.stderr)

    def test_process_crash_recovers_only_the_last_durable_prefix_and_survives_cleanup(self):
        self.crash();collect_orphans()
        entries=candidates();self.assertEqual(len(entries),1)
        take=recover_take(entries[0]);self.assertEqual(take.frames,500)
        self.assertEqual(take.description,'USB microphone')
        np.testing.assert_array_equal(take.samples,.25)
        self.assertEqual(take.path.stat().st_size,500*2*4)
        take.leave_for_recovery()
        again=candidates();self.assertEqual(len(again),1)
        take=recover_take(again[0]);np.testing.assert_array_equal(take.samples,.25)
        path=take.path;take.discard();self.assertFalse(path.exists());self.assertEqual(candidates(),[])

    def test_active_take_is_not_offered_and_cancel_removes_journal(self):
        take=Take(48000,1);take.append(np.zeros((20,1),np.float32))
        self.assertEqual(candidates(),[])
        path=take.journal;take.discard();self.assertFalse(path.exists())

    def test_broken_recording_can_be_discarded_without_following_its_path(self):
        self.crash();owner=candidates()[0]
        original=self.path/'keep.wav';original.write_bytes(b'original recording')
        path=owner.path/'recording.json';record=json.loads(path.read_text());record['file']=str(original)
        path.write_text(json.dumps(record))
        with self.assertRaises(AudioError):recover_take(owner)
        discard(owner)
        self.assertEqual(original.read_bytes(),b'original recording');self.assertFalse(path.exists())

    def test_partial_disk_write_is_truncated_to_preceding_complete_frames(self):
        take=Take(48000,2);take.append(np.full((10,2),.25,np.float32));original=take._file
        class FailingWriter:
            count=0
            def write(self,raw):
                self.count+=1
                if self.count==1:return original.write(raw[:7])
                raise OSError('disk full')
            def __getattr__(self,name):return getattr(original,name)
        take._file=FailingWriter()
        with self.assertRaises(OSError):take.append(np.ones((10,2),np.float32))
        self.assertEqual(take.frames,10)
        take.finish();self.assertEqual(take.path.stat().st_size,80)
        np.testing.assert_array_equal(take.samples,.25);take.discard()

    def test_slow_durable_checkpoints_do_not_block_input_writes_and_finish_waits_for_them(self):
        take=Take(48000,1);started=threading.Event();release=threading.Event()
        checkpoint=take._write_checkpoint
        def slow(frames):
            started.set();release.wait(5);checkpoint(frames)
        with patch.object(take,'_write_checkpoint',side_effect=slow):
            take._last_checkpoint=0
            take.append(np.ones((10,1),np.float32))
            self.assertTrue(started.wait(2))
            take.append(np.full((10,1),.5,np.float32))
            self.assertEqual(take.frames,20)
            release.set();take.finish()
        record=json.loads(take.journal.read_text());self.assertEqual(record['frames'],20)
        np.testing.assert_array_equal(take.samples[:,0],[1]*10+[.5]*10);take.discard()


if __name__=='__main__':unittest.main()
