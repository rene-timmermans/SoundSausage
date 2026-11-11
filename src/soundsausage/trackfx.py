"""Immutable insert settings and stateful block processors for track playback/export."""
import ctypes as C
from dataclasses import dataclass
import json
import uuid

import numpy as np

from .audio import AudioError
from .filters import EFFECTS as FILTERS, design, number
from .space import Processor as SpaceProcessor

MAX_EFFECTS = 16
NAMES = {'gain': 'Amplify', 'channel_mix': 'Channel Mixer', 'dynamics': 'Dynamics',
         'graphic_eq': 'Graphic EQ', 'parametric_eq': 'Parametric EQ', 'filter': 'Filter',
         'delay': 'Delay', 'echo': 'Echo', 'reverb': 'Reverb', 'invert': 'Invert', 'plugin': 'External Plug-in'}


@dataclass(frozen=True)
class TrackEffect:
    id: str
    kind: str
    parameters: str = '{}'
    enabled: bool = True

    @property
    def settings(self): return json.loads(self.parameters)


def effect(kind, settings=None, *, key=None, enabled=True):
    if kind not in NAMES: raise AudioError('Unsupported track effect.')
    if type(enabled) is not bool: raise AudioError('Effect bypass must be boolean.')
    key = uuid.uuid4().hex if key is None else key
    if not isinstance(key, str) or len(key) != 32 or any(c not in '0123456789abcdef' for c in key):
        raise AudioError('Invalid track effect identifier.')
    if settings is not None and not isinstance(settings, dict): raise AudioError('Invalid effect settings.')
    try:
        parameters = json.dumps(settings or {}, allow_nan=False, sort_keys=True, separators=(',', ':'))
        if len(parameters) > (2*1024*1024 if kind == 'plugin' else 65536): raise ValueError('Effect settings are too large.')
    except (ValueError, TypeError) as error: raise AudioError(str(error)) from error
    return TrackEffect(key, kind, parameters, enabled)


def chain(values):
    if not isinstance(values, (tuple, list)) or len(values) > MAX_EFFECTS:
        raise AudioError(f'A track supports at most {MAX_EFFECTS} effects.')
    result = []
    for value in values:
        if isinstance(value, TrackEffect):
            item = effect(value.kind, value.settings, key=value.id, enabled=value.enabled)
        elif isinstance(value, dict) and set(value) == {'id', 'kind', 'parameters', 'enabled'}:
            item = effect(value['kind'], json.loads(value['parameters']), key=value['id'], enabled=value['enabled'])
        else: raise AudioError('Invalid track effect record.')
        if item.id in {e.id for e in result}: raise AudioError('Duplicate track effect identifier.')
        result.append(item)
    return tuple(result)


class Processor:
    def __init__(self, spec, rate, dsp):
        self.spec, self.rate, self.dsp = spec, rate, dsp
        self.settings = settings = spec.settings
        self.space = None
        self.plugin = None
        self.state = (C.c_double * 2)()
        if spec.kind == 'plugin':
            from .plugins import PluginProcess
            self.plugin = PluginProcess(settings,rate)
        elif spec.kind in FILTERS:
            self.coefficients, self.output = design(spec.kind, rate, **settings)
            self.state = np.zeros((len(self.coefficients), 2, 2), np.float64)
        elif spec.kind in ('delay', 'echo', 'reverb'):
            if settings.get('tail_seconds', 0): raise AudioError('Set the track tail instead of an offline effect tail.')
            self.space = SpaceProcessor(spec.kind, rate, 2, **settings)
        elif spec.kind == 'gain':
            if set(settings) - {'initial', 'final', 'logarithmic'}: raise AudioError('Unknown amplification setting.')
            values = np.broadcast_to(np.asarray(settings.get('initial', 1), np.float64), (2,))
            if not np.isfinite(values).all() or (values < 0).any() or (values > 100).any(): raise AudioError('Invalid amplification.')
            # Track inserts are constant gain; fades belong to clip automation.
            if 'final' in settings and not np.array_equal(values, np.broadcast_to(settings['final'], (2,))):
                raise AudioError('Use a clip volume line for a realtime fade.')
            self.settings = dict(initial=values)
        elif spec.kind == 'dynamics':
            if 'points' not in settings: raise AudioError('Choose a dynamics curve.')
        elif spec.kind == 'invert' and settings: raise AudioError('Invert has no parameters.')
        # Exercise native validation before the first audible block.
        if spec.kind in ('dynamics', 'channel_mix'): self.process(np.zeros((1, 2), np.float32))
        self.state = (C.c_double * 2)() if spec.kind == 'dynamics' else self.state

    def process(self, data):
        kind = self.spec.kind
        if self.plugin is not None: self.plugin.process(data)
        elif kind in FILTERS: self.dsp.biquads(data, self.coefficients, self.state, self.output)
        elif self.space is not None: self.space.process(self.dsp, data)
        elif kind == 'dynamics': self.dsp.dynamics(data, self.rate, state=self.state, **self.settings)
        elif kind == 'gain': self.dsp.gain(data, **self.settings)
        elif kind == 'channel_mix': self.dsp.channel_mix(data, **self.settings)
        else: self.dsp.simple(kind, data)
        if not np.isfinite(data).all(): raise AudioError('A track effect overflowed. Lower its level.')
        return data

    def update(self,spec):
        if self.plugin is None or spec.kind != 'plugin': return False
        old,new = self.spec.settings,spec.settings
        if any(old.get(key)!=new.get(key) for key in ('plugin_id','fingerprint')):return False
        if old.get('state')!=new.get('state') and new.get('state'):
            self.plugin.restore(new['state'])
        self.plugin.helper.request(dict(op='parameters',values=new.get('values',{})))
        self.spec=spec;self.settings=new
        return True

    def close(self):
        if self.plugin is not None:self.plugin.close();self.plugin=None


class Rack:
    def __init__(self, rate, dsp):
        self.rate, self.dsp = rate, dsp
        self.processors = {}

    @property
    def latency(self):
        return sum(p.plugin.info.get('latency',0) for p in self.processors.values() if p.plugin is not None)

    def process(self, data, effects):
        active = {e.id for e in effects if e.enabled}
        for key in set(self.processors)-active: self.processors.pop(key).close()
        for spec in effects:
            if not spec.enabled: continue
            processor = self.processors.get(spec.id)
            if processor is None or (processor.spec != spec and not processor.update(spec)):
                replacement = Processor(spec, self.rate, self.dsp)
                if processor is not None: processor.close()
                self.processors[spec.id] = processor = replacement
            processor.process(data)
        return data

    def close(self):
        for processor in self.processors.values(): processor.close()
        self.processors.clear()
