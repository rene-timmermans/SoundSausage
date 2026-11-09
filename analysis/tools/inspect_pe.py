#!/usr/bin/env python3
"""Read-only PE32 inventory using Python's standard library; never load target code."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import struct


class PE:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        self.nt = self.u32(0x3c)
        if self.data[:2] != b'MZ' or self.data[self.nt:self.nt+4] != b'PE\0\0':
            raise ValueError('not PE')
        self.machine, count, self.timestamp = struct.unpack_from('<HHI', self.data, self.nt+4)
        opt_size = self.u16(self.nt+20)
        self.opt = self.nt+24
        if self.u16(self.opt) != 0x10b:
            raise ValueError('only PE32 supported')
        self.base = self.u32(self.opt+28)
        self.sections = []
        for n in range(count):
            p = self.opt + opt_size + n*40
            name = self.data[p:p+8].rstrip(b'\0').decode('ascii')
            vs, va, size, raw = struct.unpack_from('<IIII', self.data, p+8)
            self.sections.append(dict(name=name, virtual_size=vs, rva=va, size=size, offset=raw))

    def u16(self, p): return struct.unpack_from('<H', self.data, p)[0]
    def u32(self, p): return struct.unpack_from('<I', self.data, p)[0]
    def zstr(self, p): return self.data[p:self.data.index(b'\0', p)].decode('cp1252', 'replace')
    def off(self, rva):
        for s in self.sections:
            if s['rva'] <= rva < s['rva']+max(s['virtual_size'], s['size']):
                return s['offset']+rva-s['rva']
        if rva < self.u32(self.opt+60): return rva
        raise ValueError('unmapped RVA: '+hex(rva))
    def directory(self, n): return struct.unpack_from('<II', self.data, self.opt+96+n*8)

    def imports(self):
        rva, size = self.directory(1)
        result = {}
        if not rva: return result
        p = self.off(rva)
        for _ in range(256):
            ilt, ts, fc, name, iat = struct.unpack_from('<IIIII', self.data, p)
            if not any((ilt, ts, fc, name, iat)): break
            dll = self.zstr(self.off(name))
            q = self.off(ilt or iat)
            funcs = []
            for i in range(4096):
                v = self.u32(q+i*4)
                if not v: break
                funcs.append(dict(name=('ordinal:'+str(v & 0xffff)) if v & 0x80000000 else self.zstr(self.off(v)+2), iat_va=hex(self.base+iat+i*4)))
            result[dll] = funcs
            p += 20
        return result

    def exports(self):
        rva, size = self.directory(0)
        if not rva: return []
        p = self.off(rva)
        base, nf, nn, af, an, ao = struct.unpack_from('<IIIIII', self.data, p+16)
        result = []
        for i in range(nn):
            name = self.zstr(self.off(self.u32(self.off(an)+i*4)))
            idx = self.u16(self.off(ao)+i*2)
            frva = self.u32(self.off(af)+idx*4)
            result.append(dict(name=name, ordinal=base+idx, rva=hex(frva), va=hex(self.base+frva), file_offset=hex(self.off(frva))))
        return result

    def resources(self):
        rva, size = self.directory(2)
        if not rva: return []
        root = self.off(rva)
        result = []
        def walk(rel, path, depth):
            if depth > 4: raise ValueError('resource recursion')
            p = root+rel
            n = self.u16(p+12)+self.u16(p+14)
            for i in range(n):
                name, target = struct.unpack_from('<II', self.data, p+16+i*8)
                if name & 0x80000000:
                    q = root+(name & 0x7fffffff)
                    length = self.u16(q)
                    name = self.data[q+2:q+2+length*2].decode('utf-16le', 'replace')
                if target & 0x80000000:
                    walk(target & 0x7fffffff, path+[name], depth+1)
                else:
                    data_rva, data_size, cp, reserved = struct.unpack_from('<IIII', self.data, root+target)
                    off = self.off(data_rva)
                    blob = self.data[off:off+data_size]
                    row = dict(path=path+[name], offset=hex(off), size=data_size)
                    if path and path[0] in (4, 5, 6, 16):
                        # Dialog labels, string tables, version fields. Preserve IDs separately.
                        row['text'] = [m.group().decode('utf-16le') for m in re.finditer(rb'(?:[\x20-\x7e]\x00){3,}', blob)]
                    if path and path[0] == 4:
                        row['menu'] = self.parse_menu(blob)
                    if path and path[0] == 5:
                        row['dialog'] = self.parse_dialog(blob)
                    result.append(row)
        walk(0, [], 0)
        return result

    @staticmethod
    def parse_dialog(blob):
        p = 0
        def read(fmt):
            nonlocal p
            values = struct.unpack_from('<'+fmt, blob, p)
            p += struct.calcsize('<'+fmt)
            return values[0] if len(values) == 1 else values
        def atom():
            nonlocal p
            first = read('H')
            if first == 0: return ''
            if first == 0xffff: return {'ordinal': read('H')}
            start = p-2
            while read('H'): pass
            return blob[start:p-2].decode('utf-16le', 'replace')
        try:
            extended = blob[2:4] == b'\xff\xff'
            if extended:
                version, signature, help_id, exstyle, style, count, x, y, cx, cy = read('HHIIIHhhhh')
            else:
                style, exstyle, count, x, y, cx, cy = read('IIHhhhh')
            result = dict(extended=extended, style=hex(style), exstyle=hex(exstyle), rect_dlu=[x,y,cx,cy],
                          menu=atom(), window_class=atom(), title=atom())
            if style & 0x40:
                result['font_point_size'] = read('H')
                if extended: result['font_weight'], result['font_italic'], result['font_charset'] = read('HBB')
                result['font'] = atom()
            controls = []
            for _ in range(count):
                p = (p+3) & ~3
                if extended:
                    help_id, exstyle, style, x, y, cx, cy, ident = read('IIIhhhhI')
                else:
                    style, exstyle, x, y, cx, cy, ident = read('IIhhhhH')
                c = dict(id=ident, style=hex(style), exstyle=hex(exstyle), rect_dlu=[x,y,cx,cy],
                         window_class=atom(), title=atom())
                extra = read('H')
                if extra: p += extra-2
                controls.append(c)
            result['controls'] = controls
            return result
        except (IndexError, struct.error, ValueError) as e:
            return {'parse_error': str(e), 'position': p}

    @staticmethod
    def parse_menu(blob):
        def word(p): return struct.unpack_from('<H', blob, p)[0]
        def string(p):
            q = p
            while word(q): q += 2
            return blob[p:q].decode('utf-16le', 'replace'), q+2
        def level(p, depth):
            if depth > 12: raise ValueError('menu depth')
            rows = []
            while p+2 <= len(blob):
                flags = word(p); p += 2
                popup = bool(flags & 0x10)
                command = None if popup else word(p)
                if not popup: p += 2
                label, p = string(p)
                row = dict(label=label, flags=hex(flags))
                if command is not None: row['command_id'] = command
                if popup: row['children'], p = level(p, depth+1)
                rows.append(row)
                if flags & 0x80: break
            return rows, p
        try:
            if word(0) != 0: return {'unsupported_template_version': word(0)}
            return level(4+word(2), 0)[0]
        except (IndexError, struct.error, ValueError) as e:
            return {'parse_error': str(e)}

    def summary(self):
        resources = self.resources()
        return dict(path=str(self.path), size=len(self.data), sha256=hashlib.sha256(self.data).hexdigest(),
            machine=hex(self.machine), pe_timestamp_utc=datetime.datetime.fromtimestamp(self.timestamp, datetime.timezone.utc).isoformat(),
            image_base=hex(self.base), entry_va=hex(self.base+self.u32(self.opt+16)),
            linker=f'{self.data[self.opt+2]}.{self.data[self.opt+3]}',
            clr_directory=list(self.directory(14)), sections=self.sections,
            imports=self.imports(), exports=self.exports(), resources=resources,
            resource_type_counts=dict(collections.Counter(str(r['path'][0]) for r in resources)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--installed', type=Path, default=Path('/home/deck/.wine/drive_c/coolpro'))
    parser.add_argument('--media', type=Path, default=Path('/home/deck/CoolEdit'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    modules = []
    for path in sorted(args.installed.iterdir()):
        if path.suffix.lower() not in ('.exe', '.dll', '.flt', '.xfm', '.ax'): continue
        info = PE(path).summary()
        (args.out/(path.name+'.json')).write_text(json.dumps(info, indent=2, ensure_ascii=False)+'\n')
        modules.append(dict(name=path.name, size=info['size'], sha256=info['sha256'],
            exports=[e['name'] for e in info['exports']], import_dlls=list(info['imports']),
            resource_type_counts=info['resource_type_counts']))
    setup = PE(args.media/'setup.exe').summary()
    (args.out/'setup.exe.json').write_text(json.dumps(setup, indent=2, ensure_ascii=False)+'\n')
    # Exclude our own generated results and session metadata if run in the source directory.
    media = [dict(path=str(p.relative_to(args.media)), size=p.stat().st_size)
             for p in sorted(args.media.rglob('*')) if p.is_file()
             and not any(s.startswith('.') or s == 'analysis' for s in p.relative_to(args.media).parts)]
    result = dict(installed=str(args.installed), media=str(args.media), modules=modules, media_files=media)
    (args.out/'inventory.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    counts = collections.Counter(Path(m['name']).suffix for m in modules)
    print(json.dumps(dict(module_counts=counts, media_file_count=len(media), empty_media_files=[m['path'] for m in media if m['size']==0]), indent=2))


if __name__ == '__main__': main()
