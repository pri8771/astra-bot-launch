import os,sys,json,tempfile,subprocess
from pathlib import Path
source=Path('/Users/pchordia/Downloads/swarm_codex/review/bots-reconcile-source')
identity=subprocess.check_output(['git','rev-parse','HEAD','HEAD^{tree}'],cwd=source,text=True).splitlines()
assert identity==['9de61f6c8db9d06b11e9c71a8f84b2f7802633c7','be23e6784c23db399db423f918ca4df912f2f252']
assert subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)==''
with tempfile.TemporaryDirectory(prefix='bots-reconcile-process-') as home:
 env={**os.environ,'SBOTS_HOME':home,'PYTHONPATH':str(source/'social-bots')}
 seed='''from runtime import paths,leasing,worker
from runtime.jsonstore import append_jsonl
append_jsonl(paths.content_dir("social-a")/"publish_queue.jsonl",{"content_id":"synthetic-violation","persona":"social-a","published":True,"publish_authorized":False})
leasing.acquire(worker.runtime_task_id("social-a"),"dead-owner",ttl_seconds=0)
'''
 subprocess.run([sys.executable,'-c',seed],env=env,check=True)
 queue=Path(home)/'content/social-a/publish_queue.jsonl'
 # Use the production paths helper to avoid assuming a storage layout.
 queue=Path(subprocess.check_output([sys.executable,'-c','from runtime import paths; print(paths.content_dir("social-a")/"publish_queue.jsonl")'],env=env,text=True).strip())
 before=queue.read_bytes()
 results=[]
 for name in ['takeover','fresh']:
  code='import json; from runtime import worker; print(json.dumps(worker.run_one_unit(worker.runtime_task_id("social-a"),"social-a","social-a",worker_id="'+name+'")))'
  proc=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,check=True)
  item=json.loads(proc.stdout);results.append(item)
  assert item['outcome']=='blocked_reconciliation_unsafe' and item['committed'] is False and item['verified'] is False and item['lease_released'] is True
  assert queue.read_bytes()==before
 assert results[0]['took_over_from'] is not None and results[1]['took_over_from'] is None
 assert not list(Path(home).rglob('*finish*.json'))
 assert len(list(Path(home).rglob('*failure*.json')))==2
 assert not list(Path(home).rglob('decisions.jsonl'))
 assert not list(Path(home).rglob('bot_state.json'))
 print(json.dumps({'source':identity[0],'tree':identity[1],'result':'PASS_TWO_FRESH_PROCESSES_REMAIN_BLOCKED','results':results,'queue_unchanged':True,'finish_receipts':0,'failure_receipts':2,'decision_records':0},indent=2))
