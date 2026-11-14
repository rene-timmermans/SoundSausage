"""Continuous-context filtering, untouched outside samples and smooth select borders."""
import unittest

import numpy as np

from soundsausage.document import Document
from soundsausage.errors import OperationCancelled
from soundsausage.operations import operation
from soundsausage import storage


class FilterBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.rate = 8000
        t = np.arange(self.rate*3)/self.rate
        self.source = np.column_stack((.4*np.sin(2*np.pi*137*t), .25*np.cos(2*np.pi*313*t))).astype(np.float32)

    def test_internal_selection_keeps_exact_endpoints_outside_and_matches_warm_interior(self):
        for name, settings in (('graphic_eq', dict(gains=(0, 0, 0, 0, -12, 0, 0, 0, 0, 0))),
                               ('parametric_eq', dict(bands=[dict(frequency=137, gain_db=-18, q=2)])),
                               ('filter', dict(kind='high_pass', frequency=500, slope=48))):
            doc = Document(self.source, self.rate); doc.select(8000, 16000)
            reference = doc.dsp.process_blocks(name, self.source, self.rate, **settings)
            preview = doc.preview_effect(name, limit=500, **settings); doc.apply(name, **settings)
            np.testing.assert_array_equal(doc.view(8000, 8500), preview)
            np.testing.assert_array_equal(doc.view()[:8001], self.source[:8001])
            np.testing.assert_array_equal(doc.view()[15999:], self.source[15999:])
            np.testing.assert_allclose(doc.view()[8400:15600], reference[8400:15600], atol=1e-6)
            doc.undo(); np.testing.assert_array_equal(doc.view(), self.source)

    def test_gain_step_at_borders_is_replaced_by_a_short_ramp(self):
        source = np.full((1000, 1), .5, np.float32)
        doc = Document(source, 1000); doc.select(200, 800)
        doc.apply('graphic_eq', output_db=-12, edge_ms=20)
        result = doc.view()[:, 0]
        self.assertEqual(result[200], .5); self.assertEqual(result[799], .5)
        self.assertLess(abs(float(result[201]-result[200])), .025)
        self.assertAlmostEqual(float(result[400]), .5*10**(-12/20), places=7)
        self.assertTrue(np.all(np.diff(result[200:220]) < 0))
        self.assertTrue(np.all(np.diff(result[780:800]) > 0))

    def test_zero_transition_is_exact_legacy_and_whole_file_keeps_raw_phase_response(self):
        doc = Document(self.source, self.rate); doc.select(8000, 16000)
        settings = dict(kind='notch', frequency=137, q=5)
        expected = doc.dsp.process_blocks('filter', self.source[8000:16000], self.rate, **settings)
        doc.apply('filter', edge_ms=0, **settings)
        np.testing.assert_array_equal(doc.view(8000, 16000), expected)
        doc.undo(); doc.select(0, doc.frames); doc.apply('filter', **settings)
        np.testing.assert_array_equal(doc.view(), doc.dsp.process_blocks('filter', self.source, self.rate, **settings))

    def test_short_one_sided_and_single_channel_selections_keep_shape_and_other_bits(self):
        for start, end in ((0, 1), (0, 100), (500, 501), (500, 502), (100, len(self.source))):
            doc = Document(self.source, self.rate); doc.select_channels((1,)); doc.select(start, end)
            doc.apply('filter', frequency=100)
            self.assertEqual(doc.frames, len(self.source))
            np.testing.assert_array_equal(doc.view()[:, 0].view(np.uint32), self.source[:, 0].view(np.uint32))
            np.testing.assert_array_equal(doc.view()[:start], self.source[:start])
            np.testing.assert_array_equal(doc.view()[end:], self.source[end:])

    def test_cancelling_context_or_result_keeps_history_redo_and_selection(self):
        for label in ('Filter voorbereiden', 'Effect toepassen'):
            doc = Document(self.source, self.rate); doc.select(8000, 16000)
            doc.apply('invert'); doc.undo(); before = doc._pieces; redo = list(doc.redo_stack)
            def cancel(done, total, current): return not (current == label and done > 0)
            with self.assertRaises(OperationCancelled), operation(cancel):
                doc.apply('filter', kind='notch', frequency=10, q=50)
            self.assertIs(doc._pieces, before); self.assertEqual(doc.redo_stack, redo)
            self.assertEqual(doc.selection, (8000, 16000))

    def test_transition_parameter_rejects_invalid_values_before_mutation(self):
        doc = Document(self.source, self.rate); doc.select(100, 200)
        for value in (-1, 101, True, float('nan')):
            with self.assertRaises(ValueError): doc.apply('filter', edge_ms=value)
        np.testing.assert_array_equal(doc.view(), self.source); self.assertFalse(doc.undo_stack)

    def test_large_selection_result_remains_disk_backed_and_source_is_immutable(self):
        data = storage.allocate((1200000, 2), zero=True); data = storage.seal(data)
        doc = Document(data, 48000); doc.select(1000, 1199000); doc.apply('filter', frequency=80)
        self.assertIsNotNone(storage.lease_of(doc._pieces[-2]))
        np.testing.assert_array_equal(data, 0); self.assertFalse(data.flags.writeable)
