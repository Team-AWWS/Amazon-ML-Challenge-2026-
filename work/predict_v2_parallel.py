"""Bounded, ordered full-test prediction with experimental retrieval v2."""
import argparse, csv, json, multiprocessing as mp, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'code/business_entity_resolution/src'

def worker(task):
    shard, idx, data, out, threshold, max_df, routes = task
    import sys
    sys.path.insert(0,str(SRC))
    import pipeline as p, retrieval_v2 as r
    r.MAX_DF=max_df; r.ROUTES=routes
    conn=p.open_index(Path(idx))
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    mpth=out/f'matching_{shard:02}.tsv'; cpth=out/f'candidates_{shard:02}.tsv'
    with open(data,encoding='utf-8',newline='') as source, mpth.open('w',encoding='utf-8',newline='') as ms, cpth.open('w',encoding='utf-8',newline='') as cs:
        mr=csv.writer(ms,delimiter='\t',lineterminator='\n'); cr=csv.writer(cs,delimiter='\t',lineterminator='\n')
        mr.writerow(p.MATCH_HEADER); cr.writerow(p.CANDIDATE_HEADER)
        n=0; candidates_count=matches_count=0; start=time.monotonic()
        for line in source:
            row=json.loads(line); found=r.candidates(conn,row); scores=p.pair_scores(row,found)
            mids=[eid for eid,score in scores if score>=threshold]
            mr.writerow((row['entity_id'],','.join(mids))); cr.writerow((row['entity_id'],','.join(x[0] for x in found)))
            n+=1; candidates_count+=len(found); matches_count+=len(mids)
            if n%10000==0: print(f'worker={shard} rows={n} rows_per_s={n/(time.monotonic()-start):.1f}',flush=True)
    conn.close()
    return {'shard':shard,'rows':n,'candidates':candidates_count,'matches':matches_count,'seconds':time.monotonic()-start}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=8);ap.add_argument('--anchors',type=int,default=1732544);ap.add_argument('--output',default='work/v2full');ap.add_argument('--threshold',type=float,default=.75);ap.add_argument('--max-df',type=int,default=500);ap.add_argument('--routes',type=int,default=1);args=ap.parse_args()
    chunk_rows=(args.anchors+args.workers-1)//args.workers
    shards=ROOT/'work/v2_input_shards'; shards.mkdir(parents=True,exist_ok=True)
    paths=[shards/f'anchors_{i:02}.jsonl' for i in range(args.workers)]; streams=[p.open('w',encoding='utf-8') for p in paths]
    source=ROOT/'Dataset/student_resource/dataset/test/test_source1.tsv'; count=0; start=time.monotonic()
    with source.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            if count >= args.anchors:
                break
            i=min(count//chunk_rows,args.workers-1)
            streams[i].write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n'); count+=1
    for s in streams:s.close()
    tasks=[(i,str(ROOT/'work/test_index.sqlite'),str(paths[i]),str(ROOT/args.output),args.threshold,args.max_df,args.routes) for i in range(args.workers)]
    with mp.get_context('spawn').Pool(args.workers) as pool:
        results=pool.map(worker,tasks)
    out=ROOT/args.output; out.mkdir(parents=True,exist_ok=True)
    for name,pieces in [('matching_results.tsv',[out/f'matching_{i:02}.tsv' for i in range(args.workers)]),('candidate_pairs.tsv',[out/f'candidates_{i:02}.tsv' for i in range(args.workers)])]:
        dest=out/name; partial=dest.with_suffix('.tsv.part')
        with partial.open('wb') as w:
            first=True
            for piece in pieces:
                with piece.open('rb') as r:
                    if first: w.write(r.readline()); first=False
                    else:r.readline()
                    while block:=r.read(4*1024*1024):w.write(block)
        partial.replace(dest)
    print(json.dumps({'anchors':count,'results':results,'seconds':time.monotonic()-start,'output':str(out)},indent=2),flush=True)

if __name__=='__main__':main()
