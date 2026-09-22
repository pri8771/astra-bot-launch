"""Evidence-local deterministic extractor v1; reads frozen bytes, never the network."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
VERSION = 'bots-evidence-html-v1'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


class Article(HTMLParser):
    def __init__(self, snapshot):
        super().__init__(convert_charrefs=True)
        self.snapshot = snapshot
        self.stack = []
        self.blocks = []
        self.title = None
        self.published = None
        self.active = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        is_body = ('entry-content' in classes if self.snapshot == 'E1' else any(c.startswith('page-article-main-content_') for c in classes))
        self.stack.append((tag, is_body))
        if self.snapshot == 'E1' and tag == 'time' and 'published' in classes and self.published is None:
            self.published = {'value': attrs['datetime'], 'precision': 'timestamp-with-offset', 'selector': 'first time.published@datetime'}
        if self.active is None:
            kind = None
            if tag == 'h1' and self.title is None:
                kind = 'title'
            elif self.snapshot == 'E2' and any(c.startswith('article-basic-date-time_') for c in classes) and self.published is None:
                kind = 'date'
            elif any(body for _, body in self.stack) and tag in {'p', 'li', 'h2', 'h3'}:
                kind = 'paragraph'
            if kind:
                self.active = (kind, len(self.stack), [])
        if tag == 'br' and self.active:
            self.active[2].append(' ')
        if tag in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        positions = [i for i, (name, _) in enumerate(self.stack) if name == tag]
        if not positions:
            return
        position = positions[-1]
        if self.active and position < self.active[1]:
            kind, _, chunks = self.active
            text = ' '.join(''.join(chunks).split())
            if kind == 'title':
                self.title = text
            elif kind == 'date':
                self.published = {'value': text, 'precision': 'date', 'selector': 'span.article-basic-date-time_*'}
            elif text:
                self.blocks.append(text)
            self.active = None
        del self.stack[position:]

    def handle_data(self, text):
        if self.active and not any(tag in {'script', 'style', 'noscript'} for tag, _ in self.stack):
            self.active[2].append(text)


def extract(snapshot):
    raw = (ROOT / f'{snapshot}.raw').read_bytes()
    receipt_bytes = (ROOT / f'{snapshot}.receipt.json').read_bytes()
    receipt = json.loads(receipt_bytes)
    assert digest(raw) == receipt['content_hash']
    assert len(raw) == receipt['content_bytes']
    assert receipt['http_status'] == 200 and receipt['transport_trusted'] is True
    assert receipt['provenance'] == 'live-capture' and not receipt['partial']
    article = Article(snapshot)
    article.feed(raw.decode('utf-8'))
    assert article.title and article.published and article.blocks
    text = ('Title: ' + article.title + '\nPublished: ' + article.published['value'] + '\n\n' + '\n\n'.join(f'[{i}] {p}' for i, p in enumerate(article.blocks)) + '\n').encode()
    # Extractive signal: source-specific fixed paragraph indices provide
    # factual support without a model or inferred marketing conclusions.
    selected = [0, 2, 3, 7] if snapshot == "E1" else [0, 1]
    assert max(selected) < len(article.blocks)
    signal = {
        'snapshot_id': snapshot, 'title': article.title,
        'url': receipt['final_url'], 'published': article.published,
        'summary': ' '.join(article.blocks[i] for i in selected), 'supporting_paragraph_indices': selected,
        'summary_method': 'extractive-fixed-source-specific-paragraphs',
        'source_capture_receipt_id': receipt['receipt_id'],
    }
    assert len(article.blocks) >= 2
    signal_bytes = encoded(signal)
    lineage = {
        'schema_version': 1, 'snapshot_id': snapshot,
        'raw_sha256': digest(raw), 'receipt_file_sha256': digest(receipt_bytes),
        'receipt_id': receipt['receipt_id'], 'retrieved_at': receipt['retrieved_at'],
        'canonical_url': receipt['source_url'], 'final_url': receipt['final_url'],
        'published': article.published, 'extractor_version': VERSION,
        'extractor_source_sha256': digest(Path(__file__).read_bytes()),
        'runtime': 'Python standard-library html.parser; whitespace-collapse v1',
        'title_selector': 'first h1',
        'body_selector': 'div.entry-content' if snapshot == 'E1' else 'div.page-article-main-content_*',
        'block_tags': ['p', 'li', 'h2', 'h3'], 'excluded': ['script', 'style', 'noscript', 'navigation outside article body'],
        'paragraph_count': len(article.blocks), 'extracted_text_sha256': digest(text),
        'signal_sha256': digest(signal_bytes), 'signal_supporting_paragraph_indices': selected,
        'original_receipt_unchanged': True, 'extraction_status': 'ok',
        'classification': 'public-source-capture-and-offline-extraction-only',
        'model_calls': 0, 'matrix_built': False, 'source_suitability': 'pending-lead-review',
    }
    for suffix, content in [('extracted.txt', text), ('signal.json', signal_bytes), ('lineage.json', encoded(lineage))]:
        (ROOT / f'{snapshot}.{suffix}').write_bytes(content)
    print(snapshot, article.title, article.published, len(article.blocks))


if __name__ == '__main__':
    for name in ('E1', 'E2'):
        extract(name)
