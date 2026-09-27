import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]; out=root/'work/v2_candidate_full'; dest=root/'amazon_ml_challenge_2026_submission_v2.zip'
paths={'output/matching_results.tsv':out/'matching_results.tsv','output/candidate_pairs.tsv':out/'candidate_pairs.tsv','Documentation_template.md':root/'work/Documentation_template_v2.md','code/business_entity_resolution/README.md':root/'code/business_entity_resolution/README.md','code/business_entity_resolution/requirements.txt':root/'code/business_entity_resolution/requirements.txt'}
for p in (root/'code/business_entity_resolution/src').glob('*.py'): paths[f'code/business_entity_resolution/src/{p.name}']=p
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
manifest={name:{'sha256':sha(path),'bytes':path.stat().st_size} for name,path in paths.items()}
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for name,path in paths.items():z.write(path,name)
 z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(dest) as z:
 bad=z.testzip()
 if bad:raise RuntimeError(bad)
print(json.dumps({'zip':str(dest),'sha256':sha(dest),'bytes':dest.stat().st_size,'files':len(paths)+1,'output':manifest['output/matching_results.tsv'],'candidates':manifest['output/candidate_pairs.tsv']},indent=2))
