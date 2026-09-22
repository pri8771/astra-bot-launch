"""Offline proof: current gate does not bind the reviewed matrix bytes.

Uses only temporary files and a sentinel in-process provider. The sentinel raises
BaseException before any external action; reaching it proves admission passed.
"""
from __future__ import annotations
import base64,json,os,tempfile
from datetime import datetime,timedelta,timezone
from pathlib import Path

SOURCE=Path('/Users/pchordia/Downloads/swarm_codex/review/bots-composition-source')
ROOT=SOURCE/'social-bots'
os.environ.pop('ANTHROPIC_API_KEY',None)
import sys
sys.path.insert(0,str(ROOT))
from runtime import divergence_prepare as dp
from runtime import reasoning_cli

freeze=ROOT/'worker-reports/cursor-recovery/evidence/SB-R07-042/freeze'
reviewed=dp.load_prepared(freeze/'PREPARED_MATRIX.json',freeze/'prompts')
bundle=json.loads((freeze/'EVIDENCE_BUNDLE.json').read_text())
snapshots={}
for sid in ('E1','E2'):
 e=bundle[sid]
 snapshots[sid]=dp.EvidenceSnapshot.from_bytes(
  sid,e['signal'],base64.b64decode(e['raw_b64']),e['receipt'],
  provenance_label=e['provenance_label'],captured_at=e['captured_at'])
files={'baseline':'social-a.json','variant_b':'social-b.json','variant_c':'social-c.json','cultural':'cultural-primandir-atman.json'}
personas={slot:json.loads((ROOT/'personas'/name).read_text()) for slot,name in files.items()}
# Same artifact/run/lane and same five-case layout, but changed objective and thus
# different contexts/prompts from the reviewed freeze.
mutated=dp.build_matrix(
 personas=personas,snapshots=snapshots,
 objective=reviewed.objective+' [UNREVIEWED MATRIX SWAP]',
 run_scope=reviewed.run_scope,lane=reviewed.lane,
 pending_count=reviewed.held_constant['pending_count'],
 is_duplicate=reviewed.held_constant['is_duplicate'],
 prior_hypotheses=reviewed.held_constant['prior_hypotheses'])
assert mutated.cases[0].context_sha256 != reviewed.cases[0].context_sha256
assert mutated.cases[0].prompt_sha256 != reviewed.cases[0].prompt_sha256

calls=[]
class SentinelProvider:
 provider_id='offline-sentinel-no-provider'
 def __init__(self): calls.append('constructed')
 def propose(self,ctx):
  calls.append('propose_reached')
  raise KeyboardInterrupt('STOP_BEFORE_ANY_EXTERNAL_PROVIDER_ACTION')

real=reasoning_cli.ClaudeCodeReasoningProvider
reasoning_cli.ClaudeCodeReasoningProvider=SentinelProvider
try:
 with tempfile.TemporaryDirectory(prefix='bots-binding-repro-') as td:
  td=Path(td); manifests=td/'manifests'; manifests.mkdir(); home=td/'home'
  now=datetime.now(timezone.utc)
  manifest={
   'schema_version':'v1','manifest_id':'diagnostic-matrix-binding','created_by':'diagnostic-only',
   'created_at':now.isoformat(),'owner_authorization_ref':'synthetic-diagnostic-no-authority',
   'artifact_scope':['SB-V04-002','SB-V04-004'],'run_scope':reviewed.run_scope,
   'lane':reviewed.lane,'provider_mode':'claude-cli','max_calls':5,
   'expires_at':(now+timedelta(minutes=30)).isoformat(),'retry_allowed':False,
   'public_effect_allowed':False,'spend_authorized':False,'api_key_allowed':False,
   'injected_runner_allowed':False}
  (manifests/'diagnostic.json').write_text(json.dumps(manifest))
  stopped=None
  try:
   dp.execute_batch(mutated,lane=reviewed.lane,personas=personas,snapshots=snapshots,
                    manifest_dir=manifests,home=home)
  except KeyboardInterrupt as exc:
   stopped=str(exc)
  assert calls==['constructed','propose_reached'],calls
  slots=list(home.rglob('slot-*.json'))
  assert len(slots)==1
  result={
   'source_sha':'8c86898d1c6641adbf5c9884e1aa7ab2923b1af3',
   'result':'CONFIRMED_MATRIX_NOT_BOUND_BY_AUTHORIZATION',
   'reviewed_context_sha256':reviewed.cases[0].context_sha256,
   'mutated_context_sha256':mutated.cases[0].context_sha256,
   'reviewed_prompt_sha256':reviewed.cases[0].prompt_sha256,
   'mutated_prompt_sha256':mutated.cases[0].prompt_sha256,
   'same_run_scope':mutated.run_scope==reviewed.run_scope,
   'same_lane':mutated.lane==reviewed.lane,
   'same_case_count':len(mutated.cases)==len(reviewed.cases)==5,
   'sentinel_events':calls,'stopped':stopped,
   'temporary_slot_count':len(slots),
   'external_provider_constructed':False,'network_calls':0,
   'temp_directory_removed_on_exit':True}
  print(json.dumps(result,indent=2,sort_keys=True))
finally:
 reasoning_cli.ClaudeCodeReasoningProvider=real
