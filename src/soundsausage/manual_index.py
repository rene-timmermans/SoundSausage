"""Stable explicit Markdown anchors shared by offline help and repository readers."""
from collections import Counter
from dataclasses import dataclass
import re
import unicodedata


START = '<!-- soundsausage-contents:start -->'
END = '<!-- soundsausage-contents:end -->'
CONTENTS_ANCHOR = 'ss-contents'
TITLES = {'nl': 'Inhoudsopgave', 'en': 'Contents', 'de': 'Inhalt', 'fr': 'Sommaire', 'es': 'Índice'}
HINTS = {
    'nl': 'Klik op een onderwerp om er direct naartoe te gaan. De knop Inhoud bovenaan brengt je terug.',
    'en': 'Click a topic to jump directly to it. The Contents button above brings you back.',
    'de': 'Ein Thema anklicken, um direkt dorthin zu springen. Die Schaltfläche Inhalt führt zurück.',
    'fr': 'Cliquez sur un sujet pour y accéder. Le bouton Sommaire en haut permet de revenir ici.',
    'es': 'Haz clic en un tema para ir a él. El botón Índice de arriba permite volver aquí.',
}


@dataclass(frozen=True)
class Topic:
    anchor: str
    title: str
    level: int


def topics(markdown):
    """Read generated anchor/heading pairs, including the contents heading."""
    result = []
    anchor = None
    for line in markdown.splitlines():
        marker = re.fullmatch(r'<a id="(ss-[a-z0-9-]+)"></a>', line)
        if marker:
            anchor = marker[1]
        heading = re.fullmatch(r'(#{2,4}) (.+)', line)
        if heading:
            if anchor:
                result.append(Topic(anchor, heading[2], len(heading[1])))
            anchor = None
    return result


def index_manual(markdown, code):
    """Regenerate a static contents list without changing the manual prose."""
    markdown = re.sub(re.escape(START)+r'.*?'+re.escape(END)+r'\n*', '', markdown, flags=re.S)
    markdown = re.sub(r'^<a id="ss-[a-z0-9-]+"></a>\n\n?', '', markdown, flags=re.M)
    counts = Counter(); entries = []; lines = []
    for line in markdown.splitlines():
        heading = re.fullmatch(r'(#{2,4}) (.+)', line)
        if heading:
            title = heading[2]
            plain = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode().lower()
            slug = re.sub('[^a-z0-9]+', '-', plain).strip('-') or 'topic'
            counts[slug] += 1
            anchor = 'ss-topic-'+slug+('' if counts[slug] == 1 else '-'+str(counts[slug]))
            entries.append(Topic(anchor, title, len(heading[1])))
            lines.extend([f'<a id="{anchor}"></a>', ''])
        lines.append(line)
    if not entries:
        return markdown
    contents = [START, f'<a id="{CONTENTS_ANCHOR}"></a>', '', '## '+TITLES[code], '', HINTS[code], '']
    for entry in entries:
        title = entry.title.replace('[', r'\[').replace(']', r'\]')
        contents.append('  '*(entry.level-2)+f'- [{title}](#{entry.anchor})')
    contents += ['', END, '']
    first = next(i for i, line in enumerate(lines) if line.startswith('<a id="ss-topic-'))
    lines[first:first] = contents
    return '\n'.join(lines).rstrip()+'\n'
