import json, os, tempfile
from runtime import metrics
from runtime.jsonstore import append_jsonl
with tempfile.TemporaryDirectory(prefix='bots-kind-review-') as home:
    os.environ['SBOTS_HOME'] = home
    row = metrics.normalize(platform='x', source='capture:receipt', persona='persona-a',
        content_id='content-a', collected_at='2026-09-22T12:00:00+00:00',
        raw_metrics={'impressions': 9}).as_dict()
    row['normalized'][metrics.REACH]['metric_kind'] = 'invented_kind'
    append_jsonl(metrics._store('bot-a'), row)
    print(json.dumps({'stored': metrics.observations_for('bot-a'),
                      'aggregate': metrics.aggregate_semantic('bot-a', metrics.REACH)},
                     indent=2, sort_keys=True))
