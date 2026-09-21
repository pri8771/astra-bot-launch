"""Offline source-excerpt reproductions, NOT the full repository test suite."""
import hashlib,json,tempfile,threading
from pathlib import Path
from types import SimpleNamespace as NS
import excerpts as e

observations=[]
c=NS(worker_id='w-111111111111', model_call_budget=1, bot='social-a', persona='social-a')
ctx={'bot':'social-a','persona':'social-a'}
def wrap(p): return e.BudgetedProvider(p,c,artifact='AUDIT',lane='lead',run_scope='isolated')

calls=[]
e.ModelReasoningProvider(lambda ctx:calls.append('invoked')).propose(ctx)
observations.append({'probe':'direct_model_callable_without_grant','expected_safe_dispatches':0,'observed_sentinel_dispatches':len(calls),'defect_reproduced':len(calls)>0})

class LabelOnly:
    adaptive=False
    def __init__(self): self.calls=0
    def propose(self,ctx): self.calls+=1; return {'fixture_sentinel':True}
p=LabelOnly(); b=wrap(p); b.propose(ctx)
observations.append({'probe':'false_fixture_label_authorization_exemption','expected_safe_dispatches':0,'observed_sentinel_dispatches':p.calls,'authorization_required':b.ledger.authorization['required'],'defect_reproduced':p.calls>0})

barrier=threading.Barrier(2)
class Racing(LabelOnly):
    def propose(self,ctx):
        self.calls+=1
        barrier.wait(timeout=3)
        return None
p=Racing(); b=wrap(p); errors=[]
def run():
    try: b.propose(ctx)
    except Exception as exc: errors.append(type(exc).__name__)
threads=[threading.Thread(target=run) for _ in range(2)]
for t in threads:t.start()
for t in threads:t.join(4)
observations.append({'probe':'concurrent_one_slot_budget','expected_max_dispatches':1,'observed_sentinel_dispatches':p.calls,'recorded_calls_after_returns':b.calls_used,'errors':errors,'defect_reproduced':p.calls>1 and not errors})

class Reentering(LabelOnly):
    def propose(self,ctx):
        self.calls+=1
        if self.calls==1:return self.wrapper.propose(ctx)
        return None
p=Reentering(); p.wrapper=wrap(p); p.wrapper.propose(ctx)
observations.append({'probe':'reentrant_one_slot_budget','expected_max_dispatches':1,'observed_sentinel_dispatches':p.calls,'recorded_calls':p.wrapper.calls_used,'defect_reproduced':p.calls>1})

# Two wrappers share the same fake grant but receive separate private in-memory counters.
e.authorization.authorize=lambda **kw:NS(max_calls=1,manifest_id='offline-test-grant',manifest_digest='fixture-only')
p=LabelOnly();p.adaptive=True
b1=wrap(p);b2=wrap(p);b1.propose(ctx);b2.propose(ctx)
observations.append({'probe':'same_grant_new_wrappers','grant_max_calls':1,'observed_sentinel_dispatches':p.calls,'defect_reproduced':p.calls>1,'limit':'authorization service is an isolated test double; proves wrapper-local accounting only'})

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'result.json'
    old=json.dumps({'schema':'ResearchResult/1','claim':'reviewed value'}).encode(); p.write_bytes(old)
    receipt=NS(outputs=[{'schema':'ResearchResult/1','kept_path':str(p),'sha256':hashlib.sha256(old).hexdigest()}])
    p.write_text(json.dumps({'schema':'ResearchResult/1','claim':'changed after verification'}))
    out,doc=e._kept_doc(receipt,'ResearchResult/1')
    observations.append({'probe':'changed_kept_output_consumed','expected_safe_outcome':'reject_hash_mismatch','observed_claim':doc['claim'],'receipt_hash_matches_bytes':out['sha256']==hashlib.sha256(p.read_bytes()).hexdigest(),'defect_reproduced':doc['claim']=='changed after verification'})

report={'classification':'OFFLINE_SOURCE_EXCERPT_REPRODUCTION','not_full_repo_execution':True,'dependencies':'test doubles for contract validation, grant lookup and ledger support; target class/method bodies copied from inspected source','probes':observations,'reproduced':sum(x['defect_reproduced'] for x in observations),'total':len(observations),'external_model_calls':0,'network_calls':0,'public_effects':0,'runtime_acceptance_changed':False}
print(json.dumps(report,indent=2))
assert report['reproduced']==len(observations)
