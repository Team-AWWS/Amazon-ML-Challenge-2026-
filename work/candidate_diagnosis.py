import sys, json, collections, time
from pathlib import Path
sys.path.insert(0, str(Path('code/business_entity_resolution/src').resolve()))
import pipeline as p
c=p.open_index(Path('work/train_index.sqlite'))
counts=collections.Counter(); countries=collections.Counter(); examples=[]
start=time.monotonic()
for row in p.read_source(Path('Dataset/student_resource/dataset/train/train_source1.tsv')):
    if countries[row['country']]>=150 or p.split_bucket(row)<4: continue
    countries[row['country']]+=1
    raw=c.execute('SELECT matched FROM labels WHERE anchor=?',(row['entity_id'],)).fetchone()[0]
    truth=raw.split(',') if raw else []
    found={x[0] for x in p.candidates(c,row,'rare_both')}
    exact={x[0] for x in p.candidates(c,row,'narrow')}
    nn=p.normalize(row['business_name']); na=p.normalize(row['business_address'])
    fields=[('nname',nn,p.NAME_STOP),('naddr',na,p.ADDRESS_STOP)]
    selected={f:p.rare_term(c,v,f,s) for f,v,s in fields}
    counts['anchors']+=1;counts['true_links']+=len(truth);counts['retrieved_links']+=len(found&set(truth))
    for tid in set(truth)-found:
        target=c.execute('SELECT nname,naddr,country FROM records WHERE entity_id=?',(tid,)).fetchone()
        tags=[]
        if nn==target[0] or (na and na==target[1]): tags.append('exact_limit_6')
        if len(exact)>=8: tags.append('rare_gate_ge8')
        shared=[];eligible=[]
        for ix,(f,v,stop) in enumerate(fields):
            common=set(v.split())&set(target[ix].split())
            for t in common:
                df=p.token_document_frequency(c,t,f)
                shared.append((f,t,df))
                if len(t)>=4 and t not in stop and any(x.isalpha() for x in t):
                    if df==1: tags.append('shared_df1_excluded')
                    elif 1<df<=1000: eligible.append((f,t,df))
                    elif df>1000: tags.append('shared_df_gt1000')
            if selected[f] and selected[f] in common: tags.append('chosen_rare_term_shared_limit_or_gate')
        if eligible:tags.append('some_shared_eligible_rare')
        if eligible and not any(t==selected[f] for f,t,df in eligible):tags.append('selected_rarest_not_shared')
        if not shared:tags.append('no_shared_tokens')
        if not eligible and not any(t=='shared_df1_excluded' for t in tags):tags.append('no_shared_eligible_rare')
        for tag in set(tags):counts[tag]+=1
        if len(examples)<50:examples.append({'anchor':row,'target_id':tid,'target':target,'selected_terms':selected,'shared':shared,'tags':sorted(set(tags)),'baseline_score':p.similarity(nn,na,target[0],target[1])})
    if sum(countries.values())>=300:break
report={'counts':dict(counts),'country_counts':dict(countries),'seconds':time.monotonic()-start,'examples':examples}
Path('work/candidate_diagnosis.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='examples'},indent=2))
