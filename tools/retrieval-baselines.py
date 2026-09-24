#!/usr/bin/env python3
"""BM25 and BGE reranking replay for lc-263."""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, resource, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL="BAAI/bge-reranker-base"
REVISION="580465186bcc87f862a9b2f9003d720af2377980"
TOP_K=10
OUT_K=3

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def toks(s): return re.findall(r"[a-z0-9_]+", s.lower())
def bm25(query, docs, k1=1.2, b=.75):
    q=toks(query); ds=[toks(x) for x in docs]; n=len(ds); avg=sum(map(len,ds))/max(1,n)
    df={t:sum(t in set(d) for d in ds) for t in set(q)}; out=[]
    for i,d in enumerate(ds):
        counts={t:d.count(t) for t in set(d)}; score=0
        for t in q:
            if not counts.get(t): continue
            idf=math.log(1+(n-df[t]+.5)/(df[t]+.5))
            score += idf*counts[t]*(k1+1)/(counts[t]+k1*(1-b+b*len(d)/max(1,avg)))
        out.append(score)
    return out
def counts(selected, ann):
    known={p:v['relevant'] for p,v in ann.items() if v['relevant'] is not None}; chosen=set(selected)&known.keys()
    tp=sum(known[p] for p in chosen); rel=sum(known.values())
    return {'tp':tp,'fp':len(chosen)-tp,'fn':rel-tp,'relevant':rel,'selected':len(selected),'unjudged_selected':len(set(selected)-known.keys())}
def agg(rows):
    s={k:sum(x[k] for x in rows) for k in rows[0]}; s['recall']=s['tp']/s['relevant'] if s['relevant'] else None; s['precision']=s['tp']/(s['tp']+s['fp']) if s['tp']+s['fp'] else None; return s
def select(scores, k=OUT_K): return [p for p,_ in sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:k]]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True); ap.add_argument('--labels',required=True); ap.add_argument('--output',required=True); ap.add_argument('--cache',required=True); ap.add_argument('--threads',type=int,default=8); args=ap.parse_args()
    data=json.loads(Path(args.dataset).read_text()); labels=json.loads(Path(args.labels).read_text())
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'; os.environ['HF_HOME']=args.cache
    import torch
    torch.set_num_threads(args.threads)
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    model=AutoModelForSequenceClassification.from_pretrained(MODEL,revision=REVISION,local_files_only=True)
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,local_files_only=True); model.eval()
    rows=[]; started=time.perf_counter()
    for e in data['events']:
        names=[c['path'] for c in e['candidates']]; texts=[c['text'] for c in e['candidates']]
        bm=bm25(e['query'],texts); bmrank={p:s for p,s in zip(names,bm)}; shortlist=select(bmrank,TOP_K)
        pairs=[(e['query'],texts[names.index(p)]) for p in shortlist]
        t=time.perf_counter()
        with torch.inference_mode():
            z=tokenizer([a for a,b in pairs],[b for a,b in pairs],padding=True,truncation=True,max_length=512,return_tensors='pt')
            logits=model(**z).logits.view(-1); vals=torch.sigmoid(logits).tolist()
        rerank={p:v for p,v in zip(shortlist,vals)}
        rows.append({'id':e['id'],'split':e['split'],'bm25':bmrank,'shortlist':shortlist,'reranker':rerank,'seconds':time.perf_counter()-t})
    out={'schema':1,'model':MODEL,'revision':REVISION,'dataset_sha256':digest(args.dataset),'labels_sha256':digest(args.labels),'events':rows,'peak_rss_gib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024**2,'wall_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'events':len(rows),'p95_seconds':sorted(x['seconds'] for x in rows)[math.ceil(.95*len(rows))-1],'peak_rss_gib':out['peak_rss_gib']},indent=2))

if __name__=='__main__': main()
