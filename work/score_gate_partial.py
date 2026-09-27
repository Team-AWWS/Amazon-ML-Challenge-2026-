import json
from pathlib import Path
for p in Path('work').glob('score_gate_*cache.part'):
 totals={t:[0,0,0,0,0] for t in [.65,.7,.75,.8,.85,.9,.95]};slices={s:[0,0,0] for s in ['zero','singleton','multiple']}
 for line in p.open():
  try:e=json.loads(line)
  except json.JSONDecodeError:continue
  truth=set(e['truth']);s='zero' if not truth else 'singleton' if len(truth)==1 else 'multiple'
  for t,v in totals.items():
   pred={k for k,score in e['scored'] if score>=t};tp=len(truth&pred);fp=len(pred-truth);fn=len(truth-pred);f=float(not pred) if not truth else 5*tp/(5*tp+4*fp+fn)
   v[0]+=1;v[1]+=f;v[2]+=tp;v[3]+=fp;v[4]+=fn
   if t==.65:slices[s][0]+=1;slices[s][1]+=f;slices[s][2]+=int(not pred)
 print(p.name,'N',totals[.65][0], 'macro',{t:round(v[1]/v[0],6) for t,v in totals.items()},'slices',slices)
