"""Bounded posting-union retrieval; baseline pipeline is deliberately unchanged."""
import functools
import pipeline as p
MAX_DF=500
ROUTES=1
CANDIDATE_CAP=36

ALIASES={'rd':'road','st':'street','ave':'avenue','dr':'drive','ln':'lane','blvd':'boulevard','hwy':'highway','fl':'floor','ste':'suite','pvt':'private','ltd':'limited','inc':'incorporated','corp':'corporation'}

def token_set(text):
    return frozenset(ALIASES.get(t,t.lstrip('0') or '0') for t in text.split())

@functools.lru_cache(maxsize=20000)
def prepared(name,address):
    return token_set(name)-p.NAME_STOP-frozenset({'incorporated','corporation','limited'}),token_set(address),frozenset(x.lstrip('0') or '0' for x in p.NUMBER.findall(address)),name.replace(' ','')

@functools.lru_cache(maxsize=768)
def postings(conn,field,term):
    expression=f'{field}:"{term}"'
    return tuple(conn.execute('SELECT r.entity_id,r.nname,r.naddr,r.country FROM search JOIN records r ON r.rowid=search.rowid WHERE search MATCH ? LIMIT 1500',(expression,)))

def terms(conn,value,field,stop):
    out=[]
    for term in set(value.split()):
        if len(term)<2 or term in stop: continue
        df=p.token_document_frequency(conn,term,field)
        if df>0:out.append((df,term))
    return sorted(out)

def rank(anchor,target):
    n,a,nums,compact=anchor; tn,ta,tnums,tc=target
    ni=len(n&tn);ai=len(a&ta)
    ns=max(ni/max(1,len(n|tn)),.85*ni/max(1,min(len(n),len(tn))))
    if compact==tc:ns=1.
    ads=max(ai/max(1,len(a|ta)),.85*ai/max(1,min(len(a),len(ta))))
    return .53*ns+.42*ads+.05*bool(nums&tnums)

def candidates(conn,row,stats=None):
    country=row['country'];nn=p.normalize(row['business_name']);na=p.normalize(row['business_address'])
    selected={}
    for field,value in [('nname',nn),('naddr',na)]:
        if not value:continue
        for src in ('s2','s3'):
            for hit in conn.execute(f'SELECT entity_id,nname,naddr FROM records WHERE country=? AND src=? AND {field}=? LIMIT 10',(country,src,value)):
                selected[hit[0]]=hit
    nt=terms(conn,nn,'nname',p.NAME_STOP);at=terms(conn,na,'naddr',p.ADDRESS_STOP)
    for field,choices in [('nname',nt),('naddr',at)]:
        chosen=[t for df,t in choices if df<=MAX_DF][:ROUTES]
        if field=='naddr':
            numerical=next((t for df,t in choices if df<=MAX_DF and t.isdigit()),None)
            if numerical and numerical not in chosen:chosen.append(numerical)
        for term in chosen:
            for eid,name,addr,ctry in postings(conn,field,term):
                if ctry==country:selected[eid]=(eid,name,addr)
    # Common names/streets become selective together. Restrict the shortest
    # posting list, and never traverse a huge country posting list in MATCH.
    if nt and at:
        pairs=[(nt[0],at[0])]
        if len(nt)>1:pairs.append((nt[1],at[0]))
        if len(at)>1:pairs.append((nt[0],at[1]))
        for (ndf,ntoken),(adf,atoken) in pairs:
            if min(ndf,adf)<=MAX_DF:continue
            expression=f'nname:"{ntoken}" AND naddr:"{atoken}"'
            for hit in conn.execute('SELECT r.entity_id,r.nname,r.naddr FROM search JOIN records r ON r.rowid=search.rowid WHERE search MATCH ? AND r.country=? LIMIT 300',(expression,country)):
                selected[hit[0]]=hit
    anchor=prepared(nn,na)
    found=sorted(selected.values(),key=lambda h:(-rank(anchor,prepared(h[1],h[2])),h[0]))[:CANDIDATE_CAP]
    if stats is not None:stats['raw_count']=len(selected)
    return found
