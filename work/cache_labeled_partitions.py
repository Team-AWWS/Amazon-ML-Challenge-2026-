"""Cache the existing fixed split to avoid rescanning 2.2M anchors per experiment."""
import collections
import csv
import json
import sqlite3
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
start = time.monotonic()
conn = sqlite3.connect(f"file:{(root/'work/train_index.sqlite').as_posix()}?mode=ro", uri=True)
counts = collections.Counter()
streams = {p: (root/'work'/f'anchors_{p}.jsonl.part').open('w', encoding='utf-8')
           for p in ('train', 'dev', 'holdout')}
with (root/'work/split_manifest.tsv').open(encoding='utf-8-sig', newline='') as sm, \
     (root/'Dataset/student_resource/dataset/train/train_source1.tsv').open(encoding='utf-8-sig', newline='') as src:
    for split, row in zip(csv.DictReader(sm, delimiter='\t'), csv.DictReader(src, delimiter='\t'), strict=True):
        assert split['source1_entity_id'] == row['entity_id']
        part = split['partition']
        if part == 'train' and counts[part, row['country']] >= 10000:
            continue
        raw = conn.execute('SELECT matched FROM labels WHERE anchor=?', (row['entity_id'],)).fetchone()
        if raw is None:
            raise ValueError(row['entity_id'])
        row['truth'] = raw[0].split(',') if raw[0] else []
        streams[part].write(json.dumps(row, ensure_ascii=False, separators=(',', ':'))+'\n')
        counts[part, row['country']] += 1
for part, stream in streams.items():
    stream.close()
    (root/'work'/f'anchors_{part}.jsonl.part').rename(root/'work'/f'anchors_{part}.jsonl')
conn.close()
print(dict(counts), 'elapsed_s', time.monotonic()-start, flush=True)
