"""Assemble and validate planning artifacts only; never invokes runtimes or external APIs."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
MISSIONS = {'opo':'OPO','whb':'WHB','commercelint':'CL','bidetfit':'BF','guru':'GURU','lipi':'LIPI'}
REQUIRED = ['id','mission','title','goal','status','owner_role','source_repo','owned_paths','evidence_refs','dependencies','prerequisite_inputs','implementation_steps','deliverables','tests','review','acceptance','rollback','next_eligible_action','estimate','jira','effect_gates','requirement_ids']

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',',':')).encode()).hexdigest()

def render(v):
    if isinstance(v, list): return '; '.join(render(x) for x in v)
    if isinstance(v, dict): return '; '.join(f'{k}: {render(x)}' for k,x in v.items())
    return str(v)

def cell(v):
    return render(v).replace('|',' / ').replace('\n',' ')

def load():
    groups=[]
    for folder in [ROOT/'shared', *[ROOT/'missions'/x for x in MISSIONS]]:
        if not (folder/'TASKS.json').exists() or not (folder/'requirements.json').exists():
            raise ValueError(f'Missing required mission bundle {folder.relative_to(ROOT)}')
        tasks,reqs=read(folder/'TASKS.json'),read(folder/'requirements.json')
        if not isinstance(tasks,list) or not isinstance(reqs,list):
            raise ValueError(f'Task/requirement files must be arrays: {folder}')
        if folder.parent.name=='missions':
            for filename in ['PLAN.md','TASKS.md','EVIDENCE.md','evidence.json','UNRESOLVED_INPUTS.md','JIRA_RECONCILIATION.md','CHECKPOINT.md','CONTINUE.md']:
                if not (folder/filename).exists(): raise ValueError(f'Missing required deliverable {folder.name}/{filename}')
        groups.append((folder,tasks,reqs))
    return groups

def validate(groups):
    errors=[]; tasks=[t for _,ts,_ in groups for t in ts]; reqs=[r for _,_,rs in groups for r in rs]
    by={t['id']:t for t in tasks}; byreq={r['id']:r for r in reqs}
    if len(by)!=len(tasks): errors.append('Duplicate task IDs')
    if len(byreq)!=len(reqs): errors.append('Duplicate requirement IDs')
    for t in tasks:
        for key in REQUIRED:
            if key not in t: errors.append(f'{t["id"]}: missing {key}')
            elif t[key] in (None,'',{}) and key not in ('jira',): errors.append(f'{t["id"]}: empty {key}')
        for key in ['owned_paths','evidence_refs','implementation_steps','deliverables','tests','acceptance','requirement_ids']:
            if not isinstance(t.get(key),list) or not t[key]: errors.append(f'{t["id"]}: needs nonempty array {key}')
        for dep in t.get('dependencies',[]):
            if dep not in by: errors.append(f'{t["id"]}: unknown dependency {dep}')
        for branch in t.get('conditional_dependencies',[]):
            for dep in branch.get('dependencies',[]):
                if dep not in by: errors.append(f'{t["id"]}: unknown conditional dependency {dep}')
            if not branch.get('condition') or not branch.get('acceptance'): errors.append(f'{t["id"]}: conditional branch lacks condition/acceptance')
        for req in t.get('requirement_ids',[]):
            if req not in byreq: errors.append(f'{t["id"]}: unknown requirement {req}')
        gate_document=ROOT/'PERMISSIONS_AND_INPUTS.md' if t['mission']=='SH' else next((f/'UNRESOLVED_INPUTS.md' for f,ts,_ in groups if any(x['id']==t['id'] for x in ts)),None)
        gate_text=gate_document.read_text(encoding='utf-8-sig') if gate_document and gate_document.exists() else ''
        known_gates=set(re.findall(r'(?<![A-Za-z0-9_-])(?:SH|OPO|WHB|CL|BF|GURU|LIPI)-[GI]\d+(?![A-Za-z0-9_-])',gate_text))
        gate_refs=list(t.get('effect_gates',[]))
        for branch in t.get('conditional_effect_gates',[]):
            if not isinstance(branch,dict):errors.append(f'{t["id"]}: conditional gate needs structured condition');continue
            if not branch.get('condition'):errors.append(f'{t["id"]}: conditional gate lacks condition')
            refs=branch.get('gates',branch.get('effect_gates',branch.get('gate_ids',[])))
            if isinstance(refs,str):refs=[refs]
            if not refs:errors.append(f'{t["id"]}: conditional effect gate lacks referenced gates')
            gate_refs.extend(refs)
        for gate in gate_refs:
            if not re.fullmatch(r'(?:SH|OPO|WHB|CL|BF|GURU|LIPI)-[GI]\d+',gate) or gate not in known_gates:
                errors.append(f'{t["id"]}: unresolved/noncanonical effect gate {gate}')
        e=t.get('estimate',{})
        if e.get('unit')!='engineering_hours' or not isinstance(e.get('low'),(int,float)) or not isinstance(e.get('high'),(int,float)) or e.get('low',0)<0 or e.get('high',0)<e.get('low',0):
            errors.append(f'{t["id"]}: invalid planning estimate')
        if not e.get('assumptions') or not e.get('dependency_risk'): errors.append(f'{t["id"]}: missing estimate caveats')
        if t.get('jira',{}).get('key','absent') is not None: errors.append(f'{t["id"]}: native binding must remain null absent writer admission')
        for k in ['candidates','matching_action','writer']:
            if k not in t.get('jira',{}): errors.append(f'{t["id"]}: missing jira.{k}')
    for r in reqs:
        for k in ['id','mission','requirement','task_ids','evidence_refs','acceptance']:
            if k not in r or r[k] in (None,'',[]): errors.append(f'{r["id"]}: missing/empty {k}')
        for tid in r.get('task_ids',[]):
            if tid not in by: errors.append(f'{r["id"]}: unknown task {tid}')
        if r['mission']!='SH' and not any(by.get(x,{}).get('mission')==r['mission'] for x in r.get('task_ids',[])):
            errors.append(f'{r["id"]}: no mission-specific implementation task')
    for m in MISSIONS.values():
        for a in range(1,19):
            if f'{m}-A{a:02}' not in byreq: errors.append(f'{m}: missing A{a:02}')
        if not any(r['mission']==m and not re.search(r'-A\d+$',r['id']) for r in reqs): errors.append(f'{m}: no product outcome requirements')
    for folder,ts,rs in groups:
        if folder.parent.name!='missions':continue
        evidence=read(folder/'evidence.json');ids={e['id'] for e in evidence}
        for e in evidence:
            for key in ['id','repository','ref','path','observed_at','classification','finding','proof_limits']:
                if key not in e:errors.append(f'{folder.name}: {e.get("id")}: missing evidence field {key}')
        for entry in ts+rs:
            for ref in entry['evidence_refs']:
                if re.fullmatch(r'(?:OPO|WHB|CL|BF|GURU|LIPI)-E\d+',ref) and ref not in ids:
                    errors.append(f'{entry["id"]}: unresolved evidence ID {ref}')
    used={x for r in reqs for x in r['task_ids']}
    for tid in by:
        if tid not in used: errors.append(f'{tid}: no coverage mapping')
    levels=[]; done=set()
    while len(done)<len(tasks):
        ready=sorted(tid for tid,t in by.items() if tid not in done and set(t['dependencies'])<=done)
        if not ready:
            errors.append('Cycle or unresolved dependencies: '+', '.join(sorted(set(by)-done)));break
        levels.append(ready);done.update(ready)
    # Optional branches must also have a feasible implementation order when enabled.
    remaining={t['id']:set(t['dependencies']) | {d for b in t.get('conditional_dependencies',[]) for d in b.get('dependencies',[])} for t in tasks}
    finished=set()
    while remaining:
        ready={k for k,v in remaining.items() if v<=finished}
        if not ready:errors.append('Conditional dependency cycle or unresolved branch: '+', '.join(sorted(remaining)));break
        finished|=ready
        for k in ready:remaining.pop(k)
    return tasks,reqs,by,levels,errors

def cards(folder,tasks):
    text=['# Shared implementation task cards','','Proposals only. Future exact-source admission and owned-path binding precede implementation. Existing release workers keep their separate scope. Each estimate is active engineering effort, not historical Jira effort or elapsed observation time.','']
    for t in tasks:
        text.extend([f'## {t["id"]} — {t["title"]}',''])
        for k in REQUIRED[3:]:
            text.extend([f'**{k.replace("_"," ").title()}:** {render(t[k])}',''])
    (folder/'TASKS.md').write_text('\n'.join(text),encoding='utf-8')

def assemble(groups,tasks,reqs,by,levels):
    cards(ROOT/'shared',groups[0][1])
    paths={t['id']:str((f/'TASKS.md').relative_to(ROOT)).replace('\\','/') for f,ts,_ in groups for t in ts}
    matrix=['# Coverage matrix','','Every row is a planning coverage claim. Linked task acceptance must still be executed. Existing source/testing/live evidence and its limits are recorded in the referenced mission bundle. A mapped external input remains unresolved; coverage is not runtime completion.','','| Requirement | Mission outcome or autonomy requirement | Owned task(s) | Dependencies | Acceptance | Evidence |','| --- | --- | --- | --- | --- | --- |']
    for r in reqs:
        links=', '.join(f'[{tid}]({paths[tid]})' for tid in r['task_ids'])
        deps=sorted({d for tid in r['task_ids'] for d in by[tid]['dependencies']})
        matrix.append(f'| {r["id"]} | {cell(r["requirement"])} | {links} | {cell(deps) or "None"} | {cell(r["acceptance"])} | {cell(r["evidence_refs"])} |')
    (ROOT/'COVERAGE_MATRIX.md').write_text('\n'.join(matrix)+'\n',encoding='utf-8')
    graph={'schema_version':1,'kind':'implementation_DAG_not_running_schedule','nodes':[{'id':t['id'],'mission':t['mission'],'title':t['title'],'dependencies':t['dependencies'],'conditional_dependencies':t.get('conditional_dependencies',[]),'effect_gates':t['effect_gates'],'conditional_effect_gates':t.get('conditional_effect_gates',[]),'acceptance':t['acceptance'],'task_file':paths[t['id']]} for t in tasks],'topological_levels':levels}
    write(ROOT/'DEPENDENCY_GRAPH.json',graph)
    dag=['# Reviewed dependency graph','','Machine-readable edges and acceptance are in DEPENDENCY_GRAPH.json. Every edge below is a predecessor required by the proposed task. These edges do not supersede current release-worker admissions. External input/effect gates are separately evaluated at action time; a blocked task never globally pauses unrelated lanes.','','| Task | Depends on | Proposed owner | Acceptance reference |','| --- | --- | --- | --- |']
    for level in levels:
        for tid in level:
            t=by[tid];dag.append(f'| {tid} | {cell(t["dependencies"]) or "None"} | {cell(t["owner_role"])} | [{t["title"]}]({paths[tid]}) |')
    dag+=['','Topological levels are implementation dependency order, not a calendar or authority to start all ready tasks. OPO/WHB/CL take priority; serialize shared portfolio deployment effects for CL/BF and all claimed paths. R730 migration is optional after Windows acceptance. Review verdicts are in reviews/.','']
    for t in tasks:
        if t.get('conditional_dependencies'): dag.extend([f'**{t["id"]} conditional branches:** {render(t["conditional_dependencies"])}',''])
        if t.get('conditional_effect_gates'): dag.extend([f'**{t["id"]} conditional effect gates:** {render(t["conditional_effect_gates"])}',''])
    (ROOT/'DEPENDENCY_GRAPH.md').write_text('\n'.join(dag),encoding='utf-8')
    est=['# Planning estimates','','Ranges are active engineering hours for proposed residual scope including relevant tests/review. They are not Jira original estimates, actual work or elapsed observation windows. Reuse/delta matching must remove overlap before dispatch; totals below are gross planning envelopes, not a quote, schedule or guaranteed spend. Provider/owner/sample/shipping and low-traffic waits remain outside these totals.','','| Stream | Tasks | Low hours | High hours |','| --- | ---: | ---: | ---: |']
    for f,ts,_ in groups:
        est.append(f'| {ts[0]["mission"]} | {len(ts)} | {sum(t["estimate"]["low"] for t in ts):g} | {sum(t["estimate"]["high"] for t in ts):g} |')
    est.append(f'| Gross envelope | {len(tasks)} | {sum(t["estimate"]["low"] for t in tasks):g} | {sum(t["estimate"]["high"] for t in tasks):g} |')
    est+=['','Per-task assumptions and dependency risk are in TASKS.json and TASKS.md. Historical current Jira estimate/actual snapshots are preserved separately in evidence/JIRA_READBACK.json and JIRA_MISSION_SEARCH.json; null actuals are unknown, not zero. No worklogs were created.','']
    (ROOT/'ESTIMATES.md').write_text('\n'.join(est),encoding='utf-8')
    out=ROOT/'jira-outbox';out.mkdir(exist_ok=True)
    records=out/'records';records.mkdir(exist_ok=True)
    for f,ts,_ in groups:
        proposals=[]
        index=out/f'{ts[0]["mission"].lower()}-v1.jsonl'
        previous={}
        if index.exists():
            previous={x['internal_task_id']:x for x in (json.loads(line) for line in index.read_text(encoding='utf-8-sig').splitlines() if line)}
        for t in ts:
            spec=digest(t);op=f'autonomy-complete-20260912-{t["id"]}-{spec}'
            prior=previous.get(t['id'])
            supersedes=(prior.get('supersedes_operation_id') if prior and prior['operation_id']==op else prior['operation_id'] if prior else None)
            proposal={'schema_version':1,'operation_id':op,'supersedes_operation_id':supersedes,'state':'proposal_only_no_write','requested_operation':'match_reuse_or_extend_then_readback; create only verified unmatched residual scope','internal_task_id':t['id'],'mission':t['mission'],'jira_key':None,'candidate_keys':t['jira']['candidates'],'writer':t['jira']['writer'],'matching_action':t['jira']['matching_action'],'task_spec_sha256':spec,'task_file':str((f/'TASKS.json').relative_to(ROOT)).replace('\\','/'),'payload':t,'preserve_native':['original_estimate','actuals','worklogs','accepted_artifacts','existing_links','history'],'forbidden':['automatic_null_field_clear','duplicate_issue_without_matching','fabricated_key','planner_jira_write','estimate_to_worklog','new_scope_admission_from_old_readback']}
            record=records/f'{t["id"]}-{spec[:20]}.json'
            if record.exists() and read(record)!=proposal:raise ValueError(f'Immutable outbox collision: {op}')
            if not record.exists():write(record,proposal)
            proposals.append(proposal)
        index.write_text(''.join(json.dumps(p,ensure_ascii=False)+'\n' for p in proposals),encoding='utf-8')
    queue={'status':'planning_only_not_dispatched','priority':['OPO','WHB','CL','BF','GURU','LIPI'],'scope_rule':'Existing Windows release assignments continue independently. Planning tasks reconcile and consume their evidence before proposing duplicate work.','phases':[{'phase':0,'name':'Source/input/native-scope matching and independent preparation','tasks':levels[0]},{'phase':1,'name':'Useful native releases','selection':'Mission product tasks; OPO/WHB/CL first, BF/GURU next, Lipi product decisions in parallel; explicit per-task dependencies apply.'},{'phase':2,'name':'Shared mechanics and six native integrations','selection':'SH-01 through SH-15 and mission autonomy integrations, without blocking already-admitted useful releases.'},{'phase':3,'name':'Real receipts, two cycles, owner/restart acceptance','selection':'Mission external/runtime acceptance tasks; actual observation/fulfillment windows must elapse.'},{'phase':4,'name':'Optional central-hub migration','tasks':['SH-16']}],'topological_levels':levels,'tasks':[{'id':t['id'],'mission':t['mission'],'dependencies':t['dependencies'],'inputs':t['prerequisite_inputs'],'effect_gates':t['effect_gates'],'next_action':t['next_eligible_action'],'status':'planned_not_admitted'} for t in tasks]}
    write(ROOT/'RELEASE_QUEUE.json',queue)
    for item in queue['tasks']:
        item['conditional_dependencies']=by[item['id']].get('conditional_dependencies',[])
        item['conditional_effect_gates']=by[item['id']].get('conditional_effect_gates',[])
    write(ROOT/'RELEASE_QUEUE.json',queue)

def main():
    p=argparse.ArgumentParser();p.add_argument('--validate-only',action='store_true');a=p.parse_args()
    try: groups=load();tasks,reqs,by,levels,errors=validate(groups)
    except Exception as e: print(str(e));return 1
    if not errors and not a.validate_only: assemble(groups,tasks,reqs,by,levels)
    result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Planning schema, full task/requirement references and implementation dependency DAG; not runtime verification','task_count':len(tasks),'requirement_count':len(reqs),'autonomy_requirements_per_mission':18,'mission_count':6,'topological_levels':len(levels),'errors':errors,'passed':not errors}
    write(ROOT/'validation/PLANNING_VALIDATION.json',result)
    print(json.dumps(result,indent=2));return 1 if errors else 0

if __name__=='__main__':sys.exit(main())
