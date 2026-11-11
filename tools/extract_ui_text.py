"""List user-facing source text, including dynamic templates, for catalogue review."""
import ast
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
UI={'window','chrome','transport','waveform','multitrack','amplitude_ui','space_ui','filters_ui','restoration_ui',
    'time_pitch_ui','special_ui','trackfx_ui','plugins_ui','recording_ui','audio_devices','envelope_ui','spectrum','progress_ui','about','manual','session_actions'}

def template(node):
    parts=[];nested=[];i=0
    for item in node.values:
        if isinstance(item,ast.Constant):parts.append(str(item.value))
        else:
            parts.append('{'+str(i)+'}')
            expr=ast.unparse(item.value)
            if 'channel_label' in expr or '.label' in expr or expr=='label' or isinstance(item.value,ast.IfExp):nested.append(i)
            i+=1
    return ''.join(parts),nested


def extract():
    records={}
    def add(text,path,line,nested=None):
        if not text.strip() or len(text)>20000:return
        if 'QMainWindow, QDialog {' in text:return
        if text.startswith(('http:','https:','#','/','\\','soundsausage.')):return
        if not re.search(r'[A-Za-zÀ-ž]',text):return
        if not (' ' in text or '\n' in text or text[0].isupper() or text.startswith('&') or text in ('sec','frames')):return
        if len(text.split())==1 and re.fullmatch(r'[a-zA-Z]+(?:[A-Z][a-z]+){2,}',text):return
        item=records.setdefault(text,dict(source=text,locations=[],nested=nested or []))
        item['locations'].append(f'{path}:{line}')
    for p in sorted((ROOT/'src/soundsausage').glob('*.py')):
        if p.stem in ('selftest','__main__','icons','i18n','i18n_widgets'):continue
        tree=ast.parse(p.read_text());parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            if isinstance(node,ast.JoinedStr):
                parent=parents.get(node)
                if isinstance(parent,ast.Call) and isinstance(parent.func,ast.Name) and parent.func.id=='Literal':continue
                source,nested=template(node)
                add(source,p.name,node.lineno,nested)
            elif isinstance(node,ast.Constant) and isinstance(node.value,str) and not isinstance(parents.get(node),ast.JoinedStr):
                if not isinstance(parents.get(node),ast.Expr):add(node.value,p.name,node.lineno)
    for p in (ROOT/'native').glob('*.cpp'):
        for i,line in enumerate(p.read_text().splitlines(),1):
            if 'throw std::runtime_error' in line:
                match=re.search(r'"([^"]+)"',line)
                if match:add(match[1],p.name,i)
    return sorted(records.values(),key=lambda r:r['source'])

if __name__=='__main__':
    entries=extract();target=ROOT/'build/ui-source-text.json';target.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(entries)} candidate texts written to {target}')
