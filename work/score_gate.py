"""Read-only frozen matcher diagnostic sweep; saves reusable scored candidates."""
import collections,json,sys,time,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code/business_entity_resolution/src'))
from pipeline import open_index,read_source,split_bucket,candidates,pair_scores,entity_f05

def main():
 p=argparse.ArgumentParser();p.add_argument('--partition',choices=['dev','holdout'],required=True);a=p.parse_args()
 cache=ROOT/'work'/f'score_gate_{a.partition}_cache.jsonl';report=ROOT/'work'/f'score_gate_{a.partition}.json'
 thresholds=[.65,.70,.75,.80,.85,.90,.95]
 totals={str(t):collections.defaultdict(collections.Counter) for t in thresholds}
 started=time.monotonic()
 def add(ex):
  truth=set(ex['truth']);sl='zero' if not truth else 'singleton' if len(truth)==1 else 'multiple'
  for t in thresholds:
   pred={key for key,score in ex['scored'] if score>=t};tp=len(truth&pred);fp=len(pred-truth);fn=len(truth-pred)
   for group in ['overall',sl,'country:'+ex['country']]:
    c=totals[str(t)][group];c.update(anchors=1,tp=tp,fp=fp,fn=fn,prediction_count=len(pred),empty_count=int(not pred),macro_sum=entity_f05(truth,pred),true_links=len(truth))
 if cache.exists():
  for line in cache.open(encoding='utf-8'):add(json.loads(line))
 else:
  conn=open_index(ROOT/'work/train_index.sqlite');n=0
  partial=cache.with_suffix('.part')
  with partial.open('w',encoding='utf-8') as f:
   for row in read_source(ROOT/'Dataset/student_resource/dataset/train/train_source1.tsv'):
    bucket=split_bucket(row)
    if (a.partition=='dev' and bucket>=2) or (a.partition=='holdout' and not 2<=bucket<4):continue
    raw=conn.execute('SELECT matched FROM labels WHERE anchor=?',(row['entity_id'],)).fetchone()
    if raw is None:raise ValueError(row['entity_id'])
    truth=raw[0].split(',') if raw[0] else []
    ex=dict(anchor=row['entity_id'],country=row['country'],truth=truth,scored=pair_scores(row,candidates(conn,row,'rare_both')))
    f.write(json.dumps(ex,separators=(',',':'))+'\n');add(ex);n+=1
    if n%5000==0:print(f'{a.partition}: {n} anchors in {time.monotonic()-started:.1f}s',flush=True)
  conn.close();partial.rename(cache)
 results={}
 for t,groups in totals.items():
  results[t]={};alln=groups['overall']['anchors']
  for group,c in groups.items():
   n=c['anchors'];tp=c['tp'];fp=c['fp'];fn=c['fn']
   results[t][group]=dict(anchors=n,proportion=n/alln,prediction_count=c['prediction_count'],average_predictions=c['prediction_count']/n,empty_prediction_rate=c['empty_count']/n,macro_f05=c['macro_sum']/n,micro_precision=tp/(tp+fp) if tp+fp else None,micro_recall=tp/(tp+fn) if tp+fn else None,tp=tp,fp=fp,fn=fn)
 result=dict(partition=a.partition,variant='rare_both',thresholds=results,elapsed_s=time.monotonic()-started,cache=str(cache),note='Diagnostic sweep; select threshold on dev only. Holdout is diagnostic, not selection data.')
 if a.partition=='holdout':
  result['baseline_reproduction_error']=abs(results['0.65']['overall']['macro_f05']-.5616271142866884)
  assert result['baseline_reproduction_error']<1e-10,result['baseline_reproduction_error']
 report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
