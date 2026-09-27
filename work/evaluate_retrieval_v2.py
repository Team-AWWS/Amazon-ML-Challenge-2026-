import argparse,collections,json,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path('code/business_entity_resolution/src').resolve()))
import pipeline as p
import retrieval_v2 as r
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=1000);ap.add_argument('--partition',default='dev');ap.add_argument('--seconds',type=int,default=720);ap.add_argument('--output',required=True);ap.add_argument('--maxdf',type=int,default=1500);ap.add_argument('--routes',type=int,default=2);ap.add_argument('--cap',type=int,default=36);ap.add_argument('--threshold',type=float);args=ap.parse_args()
if args.partition=='holdout' and args.threshold is None:raise ValueError('Holdout requires frozen threshold')
r.MAX_DF=args.maxdf;r.ROUTES=args.routes;r.CANDIDATE_CAP=args.cap
c=p.open_index(Path('work/train_index.sqlite'));start=time.monotonic();countries=collections.Counter();examples=[];raws=[];sizes=[];true=hit=0;oracle=[];retrieval_s=scoring_s=0
for row in p.read_source(Path('Dataset/student_resource/dataset/train/train_source1.tsv')):
    if countries[row['country']]>=args.limit//2:continue
    b=p.split_bucket(row)
    if (args.partition=='dev' and b>=2) or (args.partition=='holdout' and not 2<=b<4):continue
    if time.monotonic()-start>args.seconds:raise RuntimeError('Mandatory bounded experiment budget exceeded')
    raw=c.execute('SELECT matched FROM labels WHERE anchor=?',(row['entity_id'],)).fetchone()[0];truth=set(raw.split(',')) if raw else set()
    stats={};t=time.monotonic();found=r.candidates(c,row,stats);retrieval_s+=time.monotonic()-t
    t=time.monotonic();scores=p.pair_scores(row,found);scoring_s+=time.monotonic()-t
    cs={x[0] for x in found};hit+=len(truth&cs);true+=len(truth);oracle.append(p.entity_f05(truth,truth&cs));raws.append(stats['raw_count']);sizes.append(len(found));countries[row['country']]+=1;examples.append((truth,scores))
    if len(examples)%500==0:print(f'anchors={len(examples)} recall={hit/max(1,true):.5f} elapsed={time.monotonic()-start:.1f}',flush=True)
    if len(examples)>=args.limit:break
sweep=[]
for threshold in ([args.threshold] if args.threshold is not None else [.55,.60,.65,.70,.75,.80,.85]):
    vals=[];tp=fp=fn=0
    for truth,scores in examples:
        pred={eid for eid,s in scores if s>=threshold};vals.append(p.entity_f05(truth,pred));tp+=len(truth&pred);fp+=len(pred-truth);fn+=len(truth-pred)
    sweep.append(dict(threshold=threshold,macro_f05=statistics.fmean(vals),precision=tp/max(1,tp+fp),recall=tp/max(1,tp+fn)))
report=dict(partition=args.partition,max_df=args.maxdf,routes=args.routes,candidate_cap=args.cap,module_sha256=p.file_sha256(Path(r.__file__)),anchors=len(examples),country_counts=dict(countries),candidate_recall=hit/true,candidate_oracle_macro_f05=statistics.fmean(oracle),candidate_mean=statistics.fmean(sizes),raw_candidate_mean=statistics.fmean(raws),raw_candidate_max=max(raws),retrieval_seconds=retrieval_s,scoring_seconds=scoring_s,elapsed_seconds=time.monotonic()-start,thresholds=sweep)
Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2),flush=True)
