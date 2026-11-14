"""Deep short dips, safe surrounding sound and the complete Remaster workflow."""
import unittest
from unittest.mock import patch

import numpy as np

from soundsausage import remaster, storage
from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from test_remaster import tone_level


def short_cuts(rate=16000, seconds=3, duration=.035, depth=.12, enabled=True):
    t=np.arange(round(rate*seconds))/rate
    drums=np.zeros(len(t));envelope=np.ones(len(t))
    for beat in np.arange(1,seconds-.25,.5):
        tau=t-beat;active=(tau>=0)&(tau<.15)
        drums[active]+=.4*np.sin(2*np.pi*70*tau[active])*np.exp(-tau[active]/.045)
        if enabled:envelope[(tau>=.012)&(tau<.012+duration)]=depth
    body=(.16*np.sin(2*np.pi*887*t)+.05*np.sin(2*np.pi*3311*t))*envelope
    return np.column_stack((body+drums,(body+drums)*.8)).astype(np.float32)


STRONG=dict(amount=90,recovery_db=6,sensitivity_db=2,release_ms=240)


class ShortDropTests(unittest.TestCase):
    def test_deep_short_dip_recovers_more_than_the_existing_strong_preset(self):
        source=short_cuts();original=source.copy()
        strong=remaster.process_blocks('remaster',source,16000,ceiling_db=0,**STRONG)
        repaired=remaster.process_blocks('remaster',source,16000,ceiling_db=0,cut_repair_db=12,**STRONG)
        def dip(data):return 20*np.log10(tone_level(data,16000,2.018,2.040)/tone_level(data,16000,1.85,1.95))
        self.assertGreater(dip(repaired)-dip(strong),3)
        self.assertLess(dip(repaired),0)
        self.assertEqual(repaired.shape,source.shape)
        np.testing.assert_allclose(repaired[:,1],repaired[:,0]*.8,atol=2e-7)
        np.testing.assert_array_equal(source,original)
        self.assertFalse(repaired.flags.writeable)

    def test_zero_setting_retains_the_existing_processor_exactly(self):
        source=short_cuts()
        old=remaster.process_blocks('remaster',source,16000,**STRONG)
        disabled=remaster.process_blocks('remaster',source,16000,cut_repair_db=0,**STRONG)
        np.testing.assert_array_equal(old,disabled)

    def test_drums_without_a_volume_cut_receive_no_extra_repair(self):
        source=short_cuts(enabled=False)
        old=remaster.process_blocks('remaster',source,16000,**STRONG)
        repaired=remaster.process_blocks('remaster',source,16000,cut_repair_db=18,**STRONG)
        np.testing.assert_array_equal(old,repaired)

    def test_gradual_ending_and_a_long_pause_are_not_filled(self):
        source=short_cuts(enabled=False)
        source[16000:]*=np.linspace(1,0,32000)[:,None]
        old=remaster.process_blocks('remaster',source,16000,**STRONG)
        repaired=remaster.process_blocks('remaster',source,16000,cut_repair_db=18,**STRONG)
        np.testing.assert_array_equal(old,repaired)
        source=short_cuts(enabled=False);source[16320:21000]=0
        old=remaster.process_blocks('remaster',source,16000,**STRONG)
        repaired=remaster.process_blocks('remaster',source,16000,cut_repair_db=18,**STRONG)
        np.testing.assert_array_equal(repaired[17000:20000],old[17000:20000])
        np.testing.assert_array_equal(repaired[18000:20000],0)

    def test_recovery_does_not_leave_an_extra_peak_after_the_cut(self):
        source=short_cuts()
        strong=remaster.process_blocks('remaster',source,16000,ceiling_db=0,**STRONG)
        repaired=remaster.process_blocks('remaster',source,16000,ceiling_db=0,cut_repair_db=12,**STRONG)
        for a,b in ((2.080,2.130),(2.150,2.250)):
            ratio=tone_level(repaired,16000,a,b)/tone_level(strong,16000,a,b)
            self.assertLess(20*np.log10(ratio),.15)

    def test_processing_is_independent_of_block_size_and_preview_is_exact(self):
        source=short_cuts(seconds=2)
        full=remaster.process_blocks('remaster',source,16000,cut_repair_db=12,**STRONG)
        small=remaster.process_blocks('remaster',source,16000,cut_repair_db=12,block_frames=127,**STRONG)
        prefix=remaster.process_blocks('remaster',source,16000,cut_repair_db=12,limit=17777,**STRONG)
        np.testing.assert_allclose(full,small,atol=1e-6)
        np.testing.assert_array_equal(prefix,full[:17777])

    def test_silence_short_ranges_high_rate_and_headroom_are_safe(self):
        for rate,frames in ((1000,1),(8000,63),(44100,4097),(192000,8)):
            silence=np.zeros((frames,2),np.float32)
            np.testing.assert_array_equal(remaster.process_blocks('remaster',silence,rate,cut_repair_db=18),silence)
        source=short_cuts()*np.float32(1e30)
        result=remaster.process_blocks('remaster',source,16000,cut_repair_db=18,ceiling_db=-3,**STRONG)
        self.assertTrue(np.isfinite(result).all())
        self.assertLessEqual(np.max(abs(result)),10**(-3/20)+1e-7)
        for value in (-1,19,float('nan')):
            with self.assertRaises(ValueError):remaster.process_blocks('remaster',source,16000,cut_repair_db=value)

    def test_cancel_new_repair_preserves_audio_metadata_channels_and_history(self):
        source=short_cuts();doc=Document(source,16000);doc.select(1000,42000);doc.select_channels((1,))
        with operation(lambda done,total,label:label!='Repairing short volume drops'):
            with self.assertRaises(OperationCancelled):doc.apply('remaster',cut_repair_db=12,**STRONG)
        np.testing.assert_array_equal(doc.read(),source)
        self.assertEqual(doc.selection,(1000,42000));self.assertEqual(doc.selected_channels,(1,))
        self.assertEqual(doc.undo_stack,[])

    def test_one_channel_undo_redo_and_disk_buffers(self):
        source=short_cuts();doc=Document(source,16000);doc.select_channels((1,))
        with patch.object(storage,'MEMORY_THRESHOLD',1024):
            doc.apply('remaster',cut_repair_db=12,**STRONG)
        after=doc.read().copy()
        np.testing.assert_array_equal(after[:,0],source[:,0])
        self.assertGreater(np.max(abs(after[:,1]-source[:,1])),.01)
        self.assertEqual(doc.last_effect[1]['cut_repair_db'],12)
        doc.undo();np.testing.assert_array_equal(doc.read(),source)
        doc.redo();np.testing.assert_array_equal(doc.read(),after)
