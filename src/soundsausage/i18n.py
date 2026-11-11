"""Application language, local catalogues and weak live text bindings.

Bindings retain source text; switching language never reconstructs editors,
changes editable document data, or resets playback and recording objects.
"""
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import string
import weakref

from PySide6.QtCore import QObject, Signal, QCoreApplication, QLocale, QSettings, QTranslator, QLibraryInfo
from shiboken6 import isValid

LANGUAGES={'nl':'Nederlands','en':'English','de':'Deutsch','fr':'Français','es':'Español'}
ROOT=Path(__file__).parent/'locales'
_manager=None
_code='en'
_objects=weakref.WeakValueDictionary()


class Literal(str):
    """Document names, file paths and third-party names are not UI source text."""


def watch(obj):
    _objects[id(obj)]=obj


def bind(obj,method,text,*args):
    if not hasattr(obj,'_loc_sources'):obj._loc_sources={}
    obj._loc_sources[(method,args)]=text
    watch(obj)
    obj._loc_replaying=True
    try:getattr(obj,method)(*args,tr(text))
    finally:obj._loc_replaying=False


@lru_cache(maxsize=5)
def catalogue(code):
    path=ROOT/(code+'.json')
    return json.loads(path.read_text('utf-8')) if path.is_file() else {}


@lru_cache(maxsize=5)
def patterns(code):
    result=[]
    for source,target in catalogue(code).items():
        if '{' not in source or (source==target and (code=='en' or source not in nested_fields())):continue
        try:
            pieces=list(string.Formatter().parse(source))
            literal=''.join(p[0] for p in pieces)
            if len(re.sub('[^A-Za-zÀ-ž]','',literal))<3 and source not in nested_fields():continue
            seen=set();parts=[]
            for text,name,fmt,conversion in pieces:
                parts.append(re.escape(text))
                if name is not None:
                    if name in seen:parts.append('(?P=p'+name+')')
                    else:parts.append('(?P<p'+name+'>'+('.*?' if '\n' in source else '[^\n]*?')+')');seen.add(name)
            # Field names in catalogue templates are numeric; groups use p0, p1, ...
            expression=''.join(parts)
            result.append((len(literal),re.compile('^'+expression+'$',re.S),target,source))
        except (ValueError,re.error):continue
    return sorted(result,key=lambda row:row[0],reverse=True)


@lru_cache(maxsize=8192)
def _translate(code,text):
    data=catalogue(code)
    if text in data:return data[text]
    stripped=text.strip()
    if stripped!=text and stripped in data:
        return text[:len(text)-len(text.lstrip())]+data[stripped]+text[len(text.rstrip()):]
    if not re.search('[A-Za-zÀ-ž]',text):return text
    for prefix in ('&Undo ','&Redo '):
        if text.startswith(prefix):return _translate(code,prefix.rstrip())+' '+_translate(code,text[len(prefix):])
    for _,expression,target,source in patterns(code):
        match=expression.fullmatch(text)
        if match:
            values={key[1:]:value for key,value in match.groupdict().items()}
            nested=nested_fields().get(source,[])
            for key in nested:
                name=str(key)
                if name in values and values[name] in data:values[name]=data[values[name]]
            return re.sub(r'\{(\d+)(?:![^}:]+)?(?::[^}]+)?\}',lambda m:values.get(m[1],m[0]),target)
    for prefix in ('Unknown EQ settings: ', 'Unknown delay settings: '):
        if text.startswith(prefix):return data.get(prefix,prefix)+text[len(prefix):]
    # Long notes reuse complete sentences and lines; whitespace is retained.
    pieces=re.split(r'(\n|(?<=[.!?]) +)',text)
    if len(pieces)>1:
        return ''.join(_translate(code,p) if p and not p.isspace() else p for p in pieces)
    return text


def tr(text):
    return str(text) if isinstance(text,Literal) else _translate(_code,str(text))


def language():return _code


@lru_cache(maxsize=1)
def nested_fields():
    path=ROOT/'nested.json'
    return json.loads(path.read_text('utf-8')) if path.is_file() else {}


class LanguageManager(QObject):
    changed=Signal(str)
    def __init__(self,app,settings=None):
        super().__init__(app)
        self.app=app;self.settings=settings or QSettings('SoundSausage','SoundSausage')
        self.qt_translator=None
        system=QLocale.system().name().split('_')[0]
        initial=os.environ.get('SOUNDSAUSAGE_LANGUAGE') or self.settings.value('ui/language',system if system in LANGUAGES else 'en')
        self.set_language(initial if initial in LANGUAGES else 'en',persist=False)

    def set_language(self,code,persist=True):
        global _code
        if code not in LANGUAGES:raise ValueError('Unsupported interface language.')
        _code=code
        QLocale.setDefault(QLocale(code))
        if self.qt_translator is not None:
            self.app.removeTranslator(self.qt_translator);self.qt_translator.deleteLater();self.qt_translator=None
        if code!='en':
            translator=QTranslator(self)
            if translator.load('qtbase_'+code,QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
                self.app.installTranslator(translator);self.qt_translator=translator
            else:translator.deleteLater()
        if persist:self.settings.setValue('ui/language',code);self.settings.sync()
        for obj in list(_objects.values()):
            if not isValid(obj):continue
            obj._loc_replaying=True
            try:
                if hasattr(obj,'setLocale'):obj.setLocale(QLocale(code))
                for (method,args),source in getattr(obj,'_loc_sources',{}).copy().items():
                    getattr(obj,method)(*args,tr(source))
                if hasattr(obj,'_localize_items'):obj._localize_items()
                if hasattr(obj,'_localize_status'):obj._localize_status()
                if hasattr(obj,'update'):obj.update()
            finally:obj._loc_replaying=False
        self.changed.emit(code)


def install_language(app=None,settings=None):
    global _manager
    app=app or QCoreApplication.instance()
    if _manager is None or not isValid(_manager):_manager=LanguageManager(app,settings)
    return _manager
