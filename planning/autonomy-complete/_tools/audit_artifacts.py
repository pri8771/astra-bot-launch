"""Bounded file, content and owned-path audit for the planning package."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
EXCLUDE={'validation/ARTIFACT_AUDIT.json','validation/ARTIFACT_HASHES.json','PUBLICATION_RECEIPT.json'}
def main():
    findings=[]; files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or rel.startswith('.scratch/') or '__pycache__' in rel:continue
        data=p.read_bytes()
        files.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'hash_scope':'working-file bytes'})
        if p.suffix not in {'.json','.jsonl','.md','.py','.txt','.mmd'}:findings.append(f'Unexpected artifact type: {rel}')
        try:text=data.decode('utf-8-sig')
        except UnicodeDecodeError:findings.append(f'Non-UTF8 artifact: {rel}');continue
        # Report paths/labels only, never suspected values.
        for label,pattern in [('private key',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),('GitHub token',r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),('Slack token',r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),('AWS access key',r'\bAKIA[A-Z0-9]{16}\b')]:
            if re.search(pattern,text):findings.append(f'Suspected {label} in {rel}')
        if p.suffix=='.json':
            try:json.loads(text)
            except json.JSONDecodeError as e:findings.append(f'Invalid JSON {rel}: {e}')
        if p.suffix=='.jsonl':
            for n,line in enumerate(text.splitlines(),1):
                try:json.loads(line)
                except json.JSONDecodeError as e:findings.append(f'Invalid JSONL {rel}:{n}: {e}')
    changed=subprocess.run(['git','diff','--name-only','3833a1b392b140f0a4f79ac4ba00e39dcad383fb'],cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
    untracked=subprocess.run(['git','ls-files','--others','--exclude-standard'],cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
    outside=[p for p in changed+untracked if not p.startswith('planning/autonomy-complete/')]
    if outside:findings.append('Changes outside owned scope: '+', '.join(outside))
    result={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_base':'3833a1b392b140f0a4f79ac4ba00e39dcad383fb','file_count':len(files),'changed_outside_owned_path':outside,'scope':'Bounded common-secret-pattern and format/ownership check; not comprehensive security certification or runtime verification','findings':findings,'passed':not findings}
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/ARTIFACT_HASHES.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
    (ROOT/'validation/ARTIFACT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return bool(findings)
if __name__=='__main__':sys.exit(main())
