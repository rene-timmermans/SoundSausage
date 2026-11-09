#!/usr/bin/env python3
"""Export static menus, accelerator tables, dialogs and script command names."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct
from inspect_pe import PE


def walk_menu(rows, prefix, commands, lines):
    if not isinstance(rows, list): return
    for row in rows:
        label = row['label'].replace('\b', ' [shortcut] ').replace('&&', '<AMP>').replace('&', '').replace('<AMP>', '&').strip()
        if not label: continue
        path = prefix+' / '+label if prefix else label
        if 'children' in row: walk_menu(row['children'], path, commands, lines)
        else:
            commands[row['command_id']].append(path)
            lines.append(f"{row['command_id']:5d}  {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--installed', type=Path, default=Path('/home/deck/.wine/drive_c/coolpro'))
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    pe = PE(args.installed/'coolpro.exe')
    info = pe.summary()
    commands, lines, accelerators = defaultdict(list), [], []
    for resource in info['resources']:
        if resource['path'][0] == 4:
            lines.append('\nRESOURCE '+str(resource['path']))
            walk_menu(resource['menu'], str(resource['path'][1]), commands, lines)
    special_keys = {0x20:'Space', 0x2e:'Delete', 0x2d:'Insert', 0x08:'Backspace', 0x09:'Tab',
                    0x0d:'Enter', 0x1b:'Esc', 0x24:'Home', 0x23:'End', 0x25:'Left', 0x26:'Up',
                    0x27:'Right', 0x28:'Down', 0x21:'PageUp', 0x22:'PageDown'}
    for resource in info['resources']:
        if resource['path'][0] != 9: continue
        off = int(resource['offset'], 16)
        blob = pe.data[off:off+resource['size']]
        for pos in range(0, len(blob)-7, 8):
            flags, key, command, pad = struct.unpack_from('<HHHH', blob, pos)
            mods = [v for bit,v in [(8,'Ctrl'),(16,'Alt'),(4,'Shift')] if flags & bit]
            key_name = special_keys.get(key)
            if key_name is None:
                key_name = 'F'+str(key-0x6f) if flags & 1 and 0x70<=key<=0x87 else chr(key) if 0x20<=key<0x7f else hex(key)
            accelerators.append(dict(resource=resource['path'][1], flags=hex(flags), key=key,
                shortcut='+'.join(mods+[key_name]), command_id=command,
                menu_paths=list(dict.fromkeys(commands[command]))))
    dialogs = []
    for path in sorted((args.evidence/'pe').glob('*.json')):
        if path.name == 'inventory.json': continue
        module = json.loads(path.read_text())
        for resource in module.get('resources', []):
            if resource['path'][0] == 5:
                dialogs.append(dict(module=path.name.removesuffix('.json'), resource=resource['path'],
                                    offset=resource['offset'], **resource['dialog']))
    scripts = []
    for path in sorted((args.installed/'scripts').glob('*.scp')):
        text = path.read_text(encoding='cp1252')
        scripts.append(dict(name=path.name, titles=[l[7:] for l in text.splitlines() if l.startswith('Title: ')],
            command_names=sorted({l[5:] for l in text.splitlines() if l.startswith('cmd: ')})))
    result = dict(source_sha256=info['sha256'], interpretation='Static resources, not runtime availability',
        menus=[r for r in info['resources'] if r['path'][0] == 4],
        commands={k:list(dict.fromkeys(v)) for k,v in sorted(commands.items()) if v},
        accelerators=accelerators, dialogs=dialogs, scripts=scripts)
    args.evidence.mkdir(parents=True, exist_ok=True)
    (args.evidence/'ui-spec.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    (args.evidence/'menus.txt').write_text('\n'.join(lines)+'\n')
    (args.evidence/'shortcuts.json').write_text(json.dumps(accelerators, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(dict(commands=len(result['commands']), accelerators=len(accelerators), dialogs=len(dialogs),
        dialog_parse_errors=[(d['module'],d['resource'],d['parse_error']) for d in dialogs if 'parse_error' in d],
        scripts=scripts), indent=2))


if __name__ == '__main__': main()
