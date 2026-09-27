import sys,json,time,collections,heapq
from pathlib import Path
sys.path.insert(0,str(Path('code/business_entity_resolution/src').resolve()))
import pipeline as p
start=time.monotonic(); conn=p.open_index(Path('work/train_index.sqlite')); counts=collections.Counter(); stats=collections.Counter(); examples=[]
for row in p.read_source(Path('Dataset/student_resource/dataset/train/train_source1.tsv')):
 if counts[row['country']]>=250: continue
 if p.split_bucket(row)<4: continue
 counts[row['country']]+=1
 raw=conn.execute('SELECT matched FROM labels WHERE anchor=?',(row['entity_id'],)).fetchone()[0]
 truth=set(raw.split(',')) if raw else set(); found=p.candidates(conn,row,'rare_both'); ids={x[0] for x in found}; nn=p.normalize(row['business_name']); na=p.normalize(row['business_address'])
 stats['anchors']+=1; stats['truth_links']+=len(truth); stats['retrieved_true']+=len(truth&ids)
 allpairs={x[0]:x for x in found}
 for target in truth-ids:
  r=conn.execute('SELECT entity_id,nname,naddr FROM records WHERE entity_id=?',(target,)).fetchone()
  if r: allpairs[target]=r
 for target,tn,ta in allpairs.values():
  score=p.similarity(nn,na,tn,ta); label=target in truth; retrieved=target in ids
  kind='tp' if label and score>=.65 and retrieved else 'fp' if not label and score>=.65 else 'missed_retrieval' if label and not retrieved else 'fn_score' if label else 'tn'
  stats[kind]+=1
  if kind in ('fp','fn_score','missed_retrieval'):
   examples.append(dict(kind=kind,score=score,country=row['country'],name=nn,address=na,target_name=tn,target_address=ta))
 if sum(counts.values())==500:break
out=dict(counts=dict(counts),stats=dict(stats),elapsed=time.monotonic()-start,highest_fp=sorted([x for x in examples if x['kind']=='fp'],key=lambda x:-x['score'])[:20],lowest_fn=sorted([x for x in examples if x['kind']=='fn_score'],key=lambda x:x['score'])[:20],missed_high_score=sorted([x for x in examples if x['kind']=='missed_retrieval'],key=lambda x:-x['score'])[:12])
Path('work/train_matcher_diagnosis.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
