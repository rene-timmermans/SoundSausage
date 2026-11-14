"""Regenerate/check clickable contents in all five bundled Markdown manuals."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from soundsausage.manual_index import index_manual, topics


def main():
    changed = []
    for code in ('nl', 'en', 'de', 'fr', 'es'):
        path = ROOT/'docs/HANDLEIDING.md' if code == 'nl' else ROOT/'docs/manual'/(code+'.md')
        source = path.read_text()
        indexed = index_manual(source, code)
        if indexed != source:
            changed.append(str(path.relative_to(ROOT)))
            if '--check' not in sys.argv:
                path.write_text(indexed)
        print(f'{code}: {len(topics(indexed))-1} indexed topics')
    if '--check' in sys.argv and changed:
        print('Outdated contents: '+', '.join(changed))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
