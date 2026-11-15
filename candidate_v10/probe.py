"""Development-only measurement of contextual model signals; no holdout inputs."""
import os, json, csv, re, time
from pathlib import Path
os.environ.setdefault('HF_HOME','/tmp/veritas-v9-hf-cache')
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer

torch.set_num_threads(4)
torch.manual_seed(10)
root=Path(__file__).resolve().parent
MT='Helsinki-NLP/opus-mt-zh-en'
NLI='MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7'
mt_tok=AutoTokenizer.from_pretrained(MT)
mt=AutoModelForSeq2SeqLM.from_pretrained(MT).eval()
print('MT loaded',flush=True)
rows=list(csv.DictReader((root.parent/'holdout_v9/v9_unseen_1000.csv').open(encoding='utf-8-sig')))
# Evaluate unique content without shared reference-only layout decorations; this
# probe is diagnostic only, and is not the final production preprocessing.
def body(s):
 s=re.sub(r'(?m)^.*(?:S\d{2}-\d{3}).*\n','',s) if False else s
 s=re.sub(r'[（(【\[]?S\d{2}-\d{3}[）)】\]]?','',s)
 s=re.sub(r'(?m)^.*(?:reference:|刊登編號).*$', '',s)
 s=re.sub(r'(?m)^(?:Revision notice|For circulation|Text for publication|Update for readers|Operational circular|Information sheet|Current instructions|Notice extract|修訂通知|供傳閱|刊登文本|讀者須知|工作通告|資料單張|現行指引|通告節錄)\s*\n','',s)
 return s.strip()
pairs=list(dict.fromkeys((body(r['chinese']),body(r['english'])) for r in rows))
translations={}
cache=root/'dev_translations.json'
if cache.exists(): translations=json.loads(cache.read_text())
zs=list(dict.fromkeys(z for z,e in pairs if z not in translations))
for i in range(0,len(zs),8):
 inp=mt_tok(zs[i:i+8],return_tensors='pt',padding=True,truncation=True,max_length=512)
 with torch.inference_mode(): ids=mt.generate(**inp,max_new_tokens=220,num_beams=4)
 translations.update(zip(zs[i:i+8],mt_tok.batch_decode(ids,skip_special_tokens=True)))
 cache.write_text(json.dumps(translations,ensure_ascii=False,indent=2))
 print('Translate',min(i+8,len(zs)),len(zs),flush=True)
del mt
print('loading NLI',flush=True)
tok=AutoTokenizer.from_pretrained(NLI)
model=AutoModelForSequenceClassification.from_pretrained(NLI).eval()
print(model.config.id2label,flush=True)
labse=SentenceTransformer('sentence-transformers/LaBSE')
emb=labse.encode(list(dict.fromkeys([x for z,e in pairs for x in (z,e,translations[z])])),normalize_embeddings=True,show_progress_bar=False)
texts=list(dict.fromkeys([x for z,e in pairs for x in (z,e,translations[z])]))
emap=dict(zip(texts,emb))
results=[]
for i in range(0,len(pairs),4):
 batch=pairs[i:i+4]; p=[x for z,e in batch for x in [(z,e),(e,z),(translations[z],e),(e,translations[z])]]
 inputs=tok([x[0] for x in p],[x[1] for x in p],return_tensors='pt',padding=True,truncation=True,max_length=384)
 with torch.inference_mode(): probs=model(**inputs).logits.softmax(-1).tolist()
 for k,(z,e) in enumerate(batch):
  results.append(dict(chinese=z,english=e,translation=translations[z],probs=probs[4*k:4*k+4],similarity=float(emap[z]@emap[e]),mt_similarity=float(emap[translations[z]]@emap[e])))
 if i%20==0:print('NLI',i,len(pairs),flush=True)
 (root/'dev_signals.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('DONE',len(pairs),flush=True)
