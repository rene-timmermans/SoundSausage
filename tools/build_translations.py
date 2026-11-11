"""Build checked application catalogues from reviewed multilingual text rows."""
import json
from pathlib import Path
import re
import sys
import string
sys.path.insert(0,str(Path(__file__).parent))
from extract_ui_text import extract

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'src/soundsausage/locales'
LANGS=('nl','de','fr','es')


def canonical(source):
    text=source.replace('&','')
    if text.endswith(('…','...')):text=re.sub(r'(…|\.\.\.)$','',text)
    return text.strip()


def build():
    rows={}
    for path in sorted((ROOT/'tools/translations').glob('*.txt')):
        for line in path.read_text().splitlines():
            if not line or line.startswith('#'):continue
            parts=line.split('|||')
            if len(parts) not in (5,6):raise ValueError(f'{path}: invalid field count: {line}')
            parts=[v.replace(r'\n','\n') for v in parts]
            source,*targets=parts
            row=dict(zip(LANGS,targets[:4]));row['en']=targets[4] if len(targets)==5 else source
            if source in rows and rows[source]!=row:raise ValueError(f'Conflicting translation: {source}')
            rows[source]=row
    identity_path=ROOT/'tools/translations/identity.json'
    identity=set(json.loads(identity_path.read_text())) if identity_path.exists() else set()
    ignore_path=ROOT/'tools/translations/ignore.json'
    ignored=set(json.loads(ignore_path.read_text())) if ignore_path.exists() else set()
    records=extract();missing=[];nested={};catalogues={lang:{} for lang in ('en',*LANGS)}
    for source in {r['source'] for r in records}|set(rows):
        if source in ignored:continue
        if source in rows:row=rows[source]
        elif source in identity:row={lang:source for lang in catalogues}
        elif re.fullmatch(r'(Invalid|Duplicate|Unknown|Unsupported) .+\.',source):
            prefix,field=source[:-1].split(' ',1)
            noun=rows.get(field) or rows.get(field.capitalize())
            template=rows.get(prefix+' {0}.')
            if noun is None or template is None:missing.append(source);continue
            row={lang:template[lang].replace('{0}',noun[lang]) for lang in catalogues}
            row['en']=source
        elif canonical(source) in rows:
            key=canonical(source);row={}
            for lang in catalogues:
                translated=rows[key][lang]
                if '&' in source and '&' not in translated:translated='&'+translated
                if source.endswith('…'):translated+='…'
                elif source.endswith('...'):translated+='...'
                row[lang]=source[:len(source)-len(source.lstrip())]+translated+source[len(source.rstrip()):]
        else:missing.append(source);continue
        def fields(text):
            return sorted(field for _,field,_,_ in string.Formatter().parse(text) if field is not None)
        for lang in catalogues:
            if fields(source)!=fields(row[lang]):raise ValueError(f'Invalid placeholders: {lang}: {source}')
            catalogues[lang][source]=row[lang]
    for record in records:
        if record['nested']:nested[record['source']]=record['nested']
    nested.update({" {0} Hz · {1} · {2} ": [1, 2], "Suggested tail: about {0} s.{1}\nThe final 10 ms of an added tail fade to silence.": [1],"Selection {0}": [0], "View {0}": [0], "Parametric band {0}: {1}": [1],
                   "{0} Hz · {1} · {2}": [1, 2], "{0} Line Point": [0],
                   "{0} by {1}; click to add or drag points, Delete to remove": [0, 1]})
    OUT.mkdir(parents=True,exist_ok=True)
    for lang,data in catalogues.items():(OUT/(lang+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    (OUT/'nested.json').write_text(json.dumps(nested,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    (ROOT/'build/ui-missing-translations.json').write_text(json.dumps(sorted(missing),ensure_ascii=False,indent=2)+'\n')
    print(f'{len(catalogues["en"])} translated source forms, {len(missing)} missing')
    return missing

if __name__=='__main__':raise SystemExit(bool(build()))
