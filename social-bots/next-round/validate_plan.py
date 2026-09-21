#!/usr/bin/env python3
"""Offline validation of the next-round closure graph; never grants execution."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

ID = re.compile(r'NR-\d{2}$')
ARTIFACT = re.compile(r'SB-[A-Z0-9]+-[A-Z0-9]+$')
SHA = re.compile(r'[0-9a-f]{40}$')
TARGETS = {'V0.4','V0.5','V0.6','V0.7','V0.8','V0.9'} | {f'V1.{i}' for i in range(10)} | {f'V2.{i}' for i in range(10)} | {'V3.0'}

def validate(data: Any, artifact_ids: set[str] | None = None,
             cards: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ['plan must be an object']
    if data.get('schema_version') != 1:
        errors.append('unsupported schema_version')
    if data.get('stage') != 'NEXT_ROUND_NOT_ACTIVE':
        errors.append('plan must remain staged; activation is a separate lead action')
    if data.get('active_assignment_change') is not False:
        errors.append('active assignment change must be false')
    for key in ('canonical_baseline', 'current_worker_baseline'):
        if not isinstance(data.get(key), str) or not SHA.fullmatch(data[key]):
            errors.append(f'{key}: expected full pinned commit SHA')
    tasks = data.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        return errors + ['tasks must be a non-empty list']
    by_id: dict[str, dict] = {}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f'tasks[{index}]: expected object')
            continue
        task_id = task.get('id')
        if not isinstance(task_id, str) or not ID.fullmatch(task_id):
            errors.append(f'tasks[{index}]: invalid closure id')
            continue
        if task_id in by_id:
            errors.append(f'{task_id}: duplicate id')
            continue
        by_id[task_id] = task
        for key in ('title', 'owner_role'):
            if not isinstance(task.get(key), str) or not task[key].strip():
                errors.append(f'{task_id}: missing {key}')
        if type(task.get('points')) is not int or task['points'] not in (1, 2):
            errors.append(f'{task_id}: points must be integer 1 or 2')
        if task.get('target') not in TARGETS:
            errors.append(f'{task_id}: unsupported target')
        if task.get('status') != 'PLANNED':
            errors.append(f'{task_id}: graph cannot self-promote work')
        for key in ('build_after', 'artifact_refs', 'operational_gates'):
            values = task.get(key)
            if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
                errors.append(f'{task_id}: {key} must be a string list')
                continue
            if len(values) != len(set(values)):
                errors.append(f'{task_id}: duplicate {key}')
        refs = task.get('artifact_refs', [])
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, str) or not ARTIFACT.fullmatch(ref):
                    errors.append(f'{task_id}: invalid artifact ref')
                elif artifact_ids is not None and ref not in artifact_ids:
                    errors.append(f'{task_id}: unknown artifact {ref}')
        card = f'WORK_CARDS.md#{task_id.lower()}'
        if task.get('card') != card:
            errors.append(f'{task_id}: card must be {card}')
        if cards is not None and f'## {task_id}\n' not in cards:
            errors.append(f'{task_id}: missing work-card heading')
    graph: dict[str, list[str]] = {}
    for task_id, task in by_id.items():
        deps = task.get('build_after', [])
        graph[task_id] = []
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if not isinstance(dep, str) or dep not in by_id:
                errors.append(f'{task_id}: unknown build prerequisite {dep!r}')
            else:
                graph[task_id].append(dep)
    visited: set[str] = set()
    visiting: set[str] = set()
    def walk(node: str) -> None:
        if node in visiting:
            errors.append(f'cycle at {node}')
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            walk(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        walk(node)
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=Path(__file__).with_name('NEXT_ROUND_TASKS.json'))
    parser.add_argument('--repo-root', type=Path, help='Strictly verify refs against this checkout, without network access')
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding='utf-8'))
        refs = None
        if args.repo_root:
            registry = args.repo_root / 'social-bots' / 'ARTIFACT_INDEX.json'
            registry_data = json.loads(registry.read_text(encoding='utf-8'))
            refs = {a['id'] for a in registry_data['artifacts']}
        cards_path = args.plan.with_name('WORK_CARDS.md')
        cards = cards_path.read_text(encoding='utf-8') if cards_path.exists() else None
        errors = validate(data, refs, cards)
        if args.repo_root and cards is None:
            errors.append('WORK_CARDS.md missing in strict repository validation')
        tasks = data.get('tasks', []) if isinstance(data, dict) else []
        print(json.dumps({'valid': not errors, 'tasks': len(tasks),
                          'artifact_reference_check': 'performed' if refs is not None else 'not_performed',
                          'work_card_check': 'performed' if cards is not None else 'not_performed',
                          'runtime_tests': 'not_run', 'errors': errors}, indent=2))
        return 1 if errors else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'valid': False, 'errors': [str(exc)], 'runtime_tests': 'not_run'}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
