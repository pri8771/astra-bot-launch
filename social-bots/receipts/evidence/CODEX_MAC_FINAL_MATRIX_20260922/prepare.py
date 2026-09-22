"""LEAD-068 preparation only: existing source APIs, no model/provider construction."""
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

SOURCE=Path('/tmp/bots-mac-matrix-source-20260922')
ROOT=SOURCE/'social-bots'
sys.path.insert(0,str(ROOT))
from runtime import authorization, collector, divergence_prepare as dp, reasoning_local

OUT=Path('/Users/pchordia/Downloads/swarm_codex/coordination/astra-bot-launch/social-bots/receipts/evidence/CODEX_MAC_FINAL_MATRIX_20260922')
if OUT.exists():raise SystemExit('immutable output exists; inspect before any further preparation')
OUT.mkdir(parents=True)
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip()
tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=SOURCE,text=True).strip()
assert subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True)==''
assert sha=='3bad0541fde8afb584bc6e396ea093b5d1f3c407'

def digest(data):return hashlib.sha256(data).hexdigest()
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')

files={'baseline':'social-a.json','variant_b':'social-b.json','variant_c':'social-c.json','cultural':'cultural-primandir-atman.json'}
personas={slot:json.loads((ROOT/'personas'/name).read_text()) for slot,name in files.items()}
inputs={};snapshots={}
for sid in ('E1','E2'):
    source=ROOT/'receipts/evidence/CODEX_CORRECTED_CAPTURE_20260922'
    raw=(source/f'{sid}.raw').read_bytes()
    receipt_bytes=(source/f'{sid}.receipt.json').read_bytes()
    receipt=json.loads(receipt_bytes)
    lineage=json.loads((source/f'{sid}.lineage.json').read_text())
    signal_bytes=(source/f'{sid}.signal.json').read_bytes()
    extracted=json.loads(signal_bytes)
    assert digest(raw)==receipt['content_hash']==lineage['raw_sha256']
    assert digest(receipt_bytes)==lineage['receipt_file_sha256']
    assert digest(signal_bytes)==lineage['signal_sha256']
    signal=asdict(collector.to_operational_signal(collector.CaptureReceipt(**receipt),title=extracted['title'],summary=extracted['summary'],tags=[]))
    # Bind full extraction lineage and exact original signal bytes inside the
    # reviewed execution closure without changing its factual title/summary.
    signal['extraction_lineage']=lineage
    signal['extracted_signal_sha256']=digest(signal_bytes)
    snapshots[sid]=dp.EvidenceSnapshot.from_bytes(sid,signal,raw,receipt,provenance_label=dp.LIVE_CAPTURE,captured_at=receipt['retrieved_at'])
    inputs[sid]={'source_path':str(source.relative_to(SOURCE)), 'raw_sha256':digest(raw),
      'receipt_file_sha256':digest(receipt_bytes),'receipt_id':receipt['receipt_id'],
      'lineage_file_sha256':digest((source/f'{sid}.lineage.json').read_bytes()),
      'signal_file_sha256':digest(signal_bytes),'signal':extracted,
      'projection':'accepted collector.to_operational_signal; exact extracted title/summary, empty tags; full lineage and signal SHA retained in execution closure'}
matrix=dp.build_matrix(personas=personas,snapshots=snapshots,
  objective='grow a durable, factually sound audience without publishing anything unreviewed',
  run_scope='v04-mac-local-20260922',lane='mac-local',provider_config=reasoning_local.provider_config())
dp.write_prepared(matrix,OUT/'PREPARED_MATRIX.json',include_prompt=True)
dp.write_prompts(matrix,OUT/'prompts')
verification=dp.verify_written(OUT/'PREPARED_MATRIX.json',OUT/'prompts')
assert verification['verified']
write('VERIFICATION.json',verification)
write('EVIDENCE_INPUTS.json',inputs)
write('PERSONAS.json',personas)
write('SNAPSHOTS.json',{sid:snapshots[sid].to_dict() for sid in snapshots})
status=dp.prepare_only_status(matrix,lane='mac-local',home='/tmp/bots-v04-mac-prepared-runtime-20260922')
assert not status['live_execution_permitted'] and not status['live_execution_performed']
write('PREPARE_STATUS.json',status)
write('SOURCE_BINDING.json',{'source_sha':sha,'source_tree':tree,'source_worktree':str(SOURCE),
 'execution_matrix_sha256':dp.execution_binding(matrix).digest,
 'prepared_matrix_file_sha256':digest((OUT/'PREPARED_MATRIX.json').read_bytes()),
 'model_calls':0,'manifest_created':False,'classification':'PREPARE_ONLY_ENGINEERING',
 'required_review':'exact source composition plus prepared matrix; no owner grant inferred',
 'persona_files':{slot:{'path':'social-bots/personas/'+name,'sha256':digest((ROOT/'personas'/name).read_bytes())} for slot,name in files.items()}})
print(json.dumps({'source_sha':sha,'source_tree':tree,'execution_matrix_sha256':dp.execution_binding(matrix).digest,'verified':verification['verified'],'status':status},indent=2))
