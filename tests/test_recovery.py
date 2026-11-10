"""Real process termination and recovery without rewriting original recordings."""
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import storage
from soundsausage.document import Document
from soundsausage.session import Session
from soundsausage.recovery import Recovery,candidates,restore,discard,collect_orphans
from soundsausage.errors import AudioError

ROOT=Path(__file__).resolve().parents[1]


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(dir=ROOT/'build')
        self.cache=Path(self.folder.name)/'work'
        self.env=patch.dict(os.environ,{'SOUNDSAUSAGE_CACHE_DIR':str(self.cache)})
        self.env.start()

    def tearDown(self):
        self.env.stop();gc.collect();self.folder.cleanup()

    def crash(self,extra=''):
        code='''
import os
import numpy as np
from soundsausage.document import Document
from soundsausage.session import Session
from soundsausage.recovery import Recovery
from soundsausage.audio import write_wav
from pathlib import Path
source=Path(os.environ['SOUNDSAUSAGE_CACHE_DIR']).parent/'original.wav'
data=np.arange(1200,dtype=np.float32).reshape(600,2)/1200
write_wav(source,data,48000,'float32')
doc=Document(data,48000,encoding='float32');doc.path=source
doc.select(120,480);doc.apply('gain',initial=.5)
session=Session(48000,1)
ids=session.import_audio([(data,48000,'Recording')])
session.configure_clip(ids[0],gain=.75)
recovery=Recovery();recovery.checkpoint(doc,session,'multitrack',ids[0])
''' +extra+'''\nos._exit(17)\n'''
        result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True)
        self.assertEqual(result.returncode,17,result.stderr)
        return self.cache.parent/'original.wav'

    def test_crash_recovers_document_and_session_exactly_without_touching_original(self):
        original=self.crash();before=original.read_bytes()
        entries=candidates();self.assertEqual(len(entries),1)
        current=Recovery()
        try:
            doc,session,mode,editing=restore(entries[0])
            expected=np.arange(1200,dtype=np.float32).reshape(600,2)/1200
            expected[120:480]*=.5
            np.testing.assert_array_equal(doc.view(),expected)
            self.assertEqual(doc.selection,(120,480));self.assertEqual(doc.cursor,120)
            self.assertTrue(doc.dirty);self.assertTrue(session.dirty)
            self.assertEqual(doc.undo_stack,[]);self.assertEqual(session.undo_stack,[])
            self.assertEqual(mode,'multitrack');self.assertEqual(session.tracks[0].clips[0].id,editing)
            self.assertEqual(session.tracks[0].clips[0].gain,.75)
            current.checkpoint(doc,session,mode,editing);discard(entries[0])
            self.assertEqual(original.read_bytes(),before)
            self.assertTrue(current.path.exists())
            doc.mark_saved();session.mark_saved();current.checkpoint(doc,session)
            self.assertFalse(current.path.exists())
        finally:
            current.close()
            for owner in entries:owner.close()

    def test_active_process_journals_are_not_offered_and_failed_atomic_write_keeps_previous(self):
        doc=Document(np.ones((20,1),np.float32),8000);session=Session(8000,1)
        doc.apply('invert');manager=Recovery()
        try:
            manager.checkpoint(doc,session)
            before=manager.path.read_bytes()
            self.assertEqual(candidates(),[])
            doc.apply('silence')
            with patch('soundsausage.recovery.os.replace',side_effect=OSError('disk failure')),self.assertRaises(OSError):
                manager.checkpoint(doc,session)
            self.assertEqual(manager.path.read_bytes(),before)
            self.assertFalse(manager.path.with_suffix('.tmp').exists())
        finally:manager.close()

    def test_recovery_rejects_outside_paths_and_leaves_journal_available(self):
        self.crash()
        entries=candidates();owner=entries[0];path=owner.path/'recovery.json'
        record=json.loads(path.read_text())
        record['document']['pieces'][0]['file']='../../outside.buffer'
        path.write_text(json.dumps(record))
        with self.assertRaises(AudioError):restore(owner)
        self.assertTrue(path.exists());discard(owner)

    def test_recovery_survives_a_second_crash_and_cleanup_keeps_referenced_buffers(self):
        self.crash()
        result=subprocess.run([sys.executable,'-c',
            'import os; from soundsausage.recovery import *; old=candidates()[0]; d,s,m,e=restore(old); new=Recovery(); new.checkpoint(d,s,m,e); discard(old); os._exit(23)'],
            cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True)
        self.assertEqual(result.returncode,23,result.stderr)
        collect_orphans()
        entries=candidates();self.assertEqual(len(entries),1)
        doc,session,_,_=restore(entries[0])
        self.assertTrue(doc.dirty);self.assertEqual(doc.frames,600)
        self.assertTrue(session.dirty);discard(entries[0])


if __name__=='__main__':unittest.main()
