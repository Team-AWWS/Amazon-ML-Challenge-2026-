"""Streaming integrity gate for a large experimental candidate output."""
import argparse, collections, csv, hashlib, json, sqlite3, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(4*1024*1024): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); ap.add_argument('--report',required=True); args=ap.parse_args()
    out=Path(args.output); matching=out/'matching_results.tsv'; candidates=out/'candidate_pairs.tsv'; start=time.monotonic()
    conn=sqlite3.connect(f'file:{(ROOT/"work/test_index.sqlite").as_posix()}?mode=ro',uri=True)
    country={entity_id: ctry for entity_id,ctry in conn.execute('SELECT entity_id,country FROM records')}; conn.close()
    counts=collections.Counter(); candidates_total=matches_total=0; sizes=collections.Counter(); empty=collections.Counter();
    with (ROOT/'Dataset/student_resource/dataset/test/test_source1.tsv').open(encoding='utf-8-sig',newline='') as src, matching.open(encoding='utf-8',newline='') as mf, candidates.open(encoding='utf-8',newline='') as cf:
        sources=csv.DictReader(src,delimiter='\t'); ms=csv.DictReader(mf,delimiter='\t'); cs=csv.DictReader(cf,delimiter='\t')
        if ms.fieldnames != ['source1_entity_id','matched_entity_ids'] or cs.fieldnames != ['source1_entity_id','candidate_entity_ids']: raise ValueError('Header mismatch')
        for n,(source,match,candidate) in enumerate(zip(sources,ms,cs,strict=True),1):
            anchor=source['entity_id']; ctry=source['country']
            if match['source1_entity_id'] != anchor or candidate['source1_entity_id'] != anchor: raise ValueError(f'Order mismatch at {n}: {anchor}')
            mids=match['matched_entity_ids'].split(',') if match['matched_entity_ids'] else []
            cids=candidate['candidate_entity_ids'].split(',') if candidate['candidate_entity_ids'] else []
            if len(mids)!=len(set(mids)) or len(cids)!=len(set(cids)): raise ValueError(f'Duplicate target at {anchor}')
            if not set(mids).issubset(cids): raise ValueError(f'Match outside candidate set at {anchor}')
            for target in cids:
                if country.get(target) != ctry: raise ValueError(f'Unknown or cross-country target at {anchor}: {target}')
            counts[ctry]+=1; candidates_total+=len(cids); matches_total+=len(mids); sizes[len(cids)]+=1; empty[ctry]+=not mids
            if n%100000==0: print(f'checked={n:,} elapsed_s={time.monotonic()-start:.1f}',flush=True)
        if next(ms,None) is not None or next(cs,None) is not None: raise ValueError('Extra output rows')
    def pct(p):
        target=int(p*(sum(sizes.values())-1)); total=0
        for value,count in sorted(sizes.items()):
            total+=count
            if total>target:return value
    report={'anchors':sum(counts.values()),'country_counts':dict(counts),'candidate_pairs':candidates_total,'candidate_mean':candidates_total/sum(counts.values()),'candidate_p95':pct(.95),'candidate_max':max(sizes),'predicted_matches':matches_total,'country_empty_prediction_rate':{c:empty[c]/counts[c] for c in counts},'target_ids_all_exist':True,'matches_subset_of_candidates':True,'rows_unique_and_in_source1_order':True,'output_sha256':{'matching_results.tsv':digest(matching),'candidate_pairs.tsv':digest(candidates)},'elapsed_s':time.monotonic()-start}
    Path(args.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
