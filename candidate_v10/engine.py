"""V10: direct contextual inference and bilingual facts, with no V7 dependency.

The Chinese-to-English translation is a cross-check, never a reference answer.
Scores remain diagnostic model scores, not calibrated probabilities of error.
"""
from pathlib import Path
import hashlib
import json
import re
import difflib
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from scipy.optimize import linear_sum_assignment
from facts import normal, direct_evidence
from terminology import translation_source

MODEL_REVISIONS = dict(embedding='836121a0533e5664b21c7aacc5d22951f2b8b25b',nli='b5113eb38ab63efdd7f280f8c144ea8b13f978ce',translation='f8d333a098d19b4fd9a8b18f94170487ad3f821d')

MODEL_IDS = dict(embedding='sentence-transformers/LaBSE',
    nli='MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7',
    translation='facebook/nllb-200-distilled-600M')


def sentences(text):
    # Keep semicolons and commas within propositions; preserve reorderings.
    return [x.strip() for x in re.split(r'(?<=[。！？])|(?<=[.!?])\s+(?=[A-Z])|\n+', text) if x.strip()]


def aligned_groups(zs, es, embeddings):
    if not zs or not es:return []
    sim=np.array([[float(embeddings[z]@embeddings[e]) for e in es] for z in zs])
    ii,jj=linear_sum_assignment(-sim)
    groups=[([int(i)],[int(j)],float(sim[i,j])) for i,j in zip(ii,jj)]
    # Preserve unmatched material by attaching it to the closest matched group.
    # The full-notice semantic pass decides meaning, not sentence-count parity.
    for i in sorted(set(range(len(zs)))-set(ii)):
        k=max(range(len(groups)),key=lambda k:max(sim[i,j] for j in groups[k][1]))
        groups[k][0].append(i)
    for j in sorted(set(range(len(es)))-set(jj)):
        k=max(range(len(groups)),key=lambda k:max(sim[i,j] for i in groups[k][0]))
        groups[k][1].append(j)
    return [(' '.join(zs[i] for i in sorted(iz)),' '.join(es[j] for j in sorted(ie)),score) for iz,ie,score in groups]


def digest(text):return hashlib.sha256(text.encode()).hexdigest()


class Checker:
    def __init__(self,cache=None,config=None,device=None,progress=print):
        self.progress=progress
        self.device=device or ('cuda' if torch.cuda.is_available() else 'cpu')
        torch.set_num_threads(4)
        torch.manual_seed(10)
        self.config=config or json.loads(Path(__file__).with_name('config.json').read_text())
        self.cache_path=Path(cache) if cache else None
        self.cache=json.loads(self.cache_path.read_text()) if self.cache_path and self.cache_path.exists() else {}
        self.progress('Loading V10 models (no V7 fallback).',flush=True)
        self.labse=SentenceTransformer(MODEL_IDS['embedding'],revision=MODEL_REVISIONS['embedding'],device=self.device)
        self.tok=AutoTokenizer.from_pretrained(MODEL_IDS['nli'],revision=MODEL_REVISIONS['nli'])
        self.nli=AutoModelForSequenceClassification.from_pretrained(MODEL_IDS['nli'],revision=MODEL_REVISIONS['nli']).to(self.device).eval()
        self.mt_tok=AutoTokenizer.from_pretrained(MODEL_IDS['translation'],revision=MODEL_REVISIONS['translation'],src_lang='zho_Hans')
        self.mt=AutoModelForSeq2SeqLM.from_pretrained(MODEL_IDS['translation'],revision=MODEL_REVISIONS['translation']).to(self.device).eval()
        labels=self.nli.config.id2label
        self.labels={name:i for i,name in labels.items()}
        assert all(x in self.labels for x in ('entailment','neutral','contradiction')),labels
        self.revisions=MODEL_REVISIONS.copy()
        self.progress('V10 ready on '+self.device,flush=True)

    def save_cache(self):
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.cache_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(self.cache,ensure_ascii=False))
            tmp.replace(self.cache_path)

    def translate(self,texts):
        missing=list(dict.fromkeys(t for t in texts if 'mt_nllb_hans_terms:'+digest(t) not in self.cache))
        for start in range(0,len(missing),8):
            batch=missing[start:start+8]
            inp=self.mt_tok([translation_source(t) for t in batch],return_tensors='pt',padding=True,truncation=False).to(self.device)
            if inp['input_ids'].shape[1]>512:raise ValueError('Translation segment exceeds token limit; no silent truncation.')
            with torch.inference_mode():
                out=self.mt.generate(**inp,max_new_tokens=300,num_beams=4,forced_bos_token_id=self.mt_tok.convert_tokens_to_ids("eng_Latn"))
            for t,ids,s in zip(batch,out,self.mt_tok.batch_decode(out,skip_special_tokens=True)):
                if len(ids)>=300 and self.mt.config.eos_token_id not in ids.tolist()[1:]:
                    self.cache['mt_nllb_hans_terms:'+digest(t)]={'error':'Translation output limit reached; the passage needs manual review.'}
                else:
                    self.cache['mt_nllb_hans_terms:'+digest(t)]=s
            self.save_cache()
            if start%40==0:self.progress(f'Translation cross-check: {min(start+8,len(missing))}/{len(missing)} new passages',flush=True)
        return {t:self.cache['mt_nllb_hans_terms:'+digest(t)] for t in texts}

    def nli_scores(self,pairs):
        def key(p):return 'nli:'+digest(json.dumps(p,ensure_ascii=False))
        missing=list(dict.fromkeys(p for p in pairs if key(p) not in self.cache))
        for start in range(0,len(missing),12):
            batch=missing[start:start+12]
            inp=self.tok([p[0] for p in batch],[p[1] for p in batch],return_tensors='pt',padding=True,truncation=False).to(self.device)
            if inp['input_ids'].shape[1]>512:raise ValueError('Inference segment exceeds token limit; no silent truncation.')
            with torch.inference_mode():scores=self.nli(**inp).logits.softmax(-1).cpu().tolist()
            for p,s in zip(batch,scores):self.cache[key(p)]={k:s[i] for k,i in self.labels.items()}
            self.save_cache()
            if start%120==0:self.progress(f'Contextual inference: {min(start+12,len(missing))}/{len(missing)} new pairs',flush=True)
        return {p:self.cache[key(p)] for p in pairs}

    def predict_many(self,inputs):
        # Only these fields cross the predictor boundary. References are not used.
        cases=[{k:r[k] for k in ('case_id','chinese','english')} for r in inputs]
        work=[]; invalid={}
        for i,r in enumerate(cases):
            z,e=normal(r['chinese']),normal(r['english'])
            if not z or not e:
                invalid[i]='Both language versions are required.';continue
            if max(len(z),len(e))>6000:
                invalid[i]='The 6,000-character input limit was exceeded.';continue
            # Short notices are compared as complete contexts. Long notices are
            # explicitly unresolved rather than silently dropping later text.
            if len(self.mt_tok(translation_source(z))['input_ids'])>480 or len(self.tok(z,e)['input_ids'])>480:
                invalid[i]='This notice exceeds V10’s validated context window; split it into shorter complete sections for review.';continue
            work.append((i,z,e))
        texts=list(dict.fromkeys([t for _,z,e in work for t in [z,e,*sentences(z),*sentences(e)]]))
        vectors=self.labse.encode(texts,normalize_embeddings=True,show_progress_bar=False,batch_size=16) if texts else []
        embeddings=dict(zip(texts,vectors))
        sentence_translations=self.translate(list(dict.fromkeys(t for _,z,_ in work for t in sentences(z))))
        valid=[]
        for i,z,e in work:
            if any(not isinstance(sentence_translations[t],str) for t in sentences(z)):
                invalid[i]='The translation cross-check could not cover this notice; manual review is needed.'
            else:valid.append((i,z,e))
        work=valid
        translations={z:' '.join(sentence_translations[t] for t in sentences(z)) for _,z,_ in work}
        valid=[]
        for i,z,e in work:
            if len(self.tok(translations[z],e)['input_ids'])>500:
                invalid[i]='The translated comparison exceeds the model context; manual review is needed.'
            else:valid.append((i,z,e))
        work=valid
        aligned={i:aligned_groups(sentences(z),sentences(e),embeddings) for i,z,e in work}
        quality_texts=list(dict.fromkeys([translations[z] for _,z,_ in work]+[v for v in sentence_translations.values() if isinstance(v,str)]+[a for i,z,e in work for a,b,sim in aligned[i]]+[' '.join(sentence_translations[t] for t in sentences(z) if t in a) for i,z,e in work for a,b,sim in aligned[i]]))
        quality_vectors=self.labse.encode(quality_texts,normalize_embeddings=True,show_progress_bar=False,batch_size=16) if quality_texts else []
        embeddings.update(dict(zip(quality_texts,quality_vectors)))
        pairs=[]
        for _,z,e in work:
            mt=translations[z]
            pairs.extend([(z,e),(e,z),(mt,e),(e,mt)])
            for a,b,sim in aligned[_]:
                am=' '.join(sentence_translations[t] for t in sentences(z) if t in a)
                pairs.extend([(a,b),(b,a),(am,b),(b,am)])
        scores=self.nli_scores(pairs)
        output={}
        for i,z,e in work:
            mt=translations[z]
            p=[scores[x] for x in [(z,e),(e,z),(mt,e),(e,mt)]]
            signal=dict(cross=[x['contradiction'] for x in p[:2]],cross_entailment=[x['entailment'] for x in p[:2]],cross_neutral=[x['neutral'] for x in p[:2]],
                        translated=[x['contradiction'] for x in p[2:]],
                        entailment=[x['entailment'] for x in p[2:]],
                        neutral=[x['neutral'] for x in p[2:]],
                        similarity=float(embeddings[z]@embeddings[e]),translation_quality=float(embeddings[z]@embeddings[mt]),translation=mt)
            facts=direct_evidence(z,e)
            groups=aligned[i]
            # Passage-level facts detect swapped roles even when document-level
            # value sets agree. Weak alignments do not establish a factual error.
            for a,b,sim in groups:
                if sim>=self.config['fact_alignment_min']:
                    facts.extend(direct_evidence(a,b))
            facts=list({json.dumps(x,sort_keys=True,ensure_ascii=False):x for x in facts}.values())
            reasons=[]
            for f in facts:
                reasons.append(dict(kind='explicit_fact',category=f['category'],
                    why=f"{f['category']} differs: English {f['english_value']} [{f['english_span']}]; Chinese {f['chinese_value']} [{f['chinese_span']}].",
                    **{k:v for k,v in f.items() if k!='category'}))
            semantic=self.semantic_decision(signal)
            passage_signals=[]
            for a,b,sim in groups:
                am=' '.join(sentence_translations[t] for t in sentences(z) if t in a)
                ps=[scores[x] for x in [(a,b),(b,a),(am,b),(b,am)]]
                ss=dict(cross=[x['contradiction'] for x in ps[:2]],cross_entailment=[x['entailment'] for x in ps[:2]],cross_neutral=[x['neutral'] for x in ps[:2]],entailment=[x['entailment'] for x in ps[2:]],neutral=[x['neutral'] for x in ps[2:]],translated=[x['contradiction'] for x in ps[2:]],similarity=sim,translation_quality=float(embeddings[a]@embeddings[am]),english_span=b,chinese_span=a,translation=am)
                passage_signals.append(ss)
            signal['passages']=passage_signals
            focus=None
            supported=[ss for ss in passage_signals if ss['similarity']>=self.config['semantic_alignment_min'] and self.semantic_decision(ss)]
            if supported:
                focus=max(supported,key=lambda ss:min(ss['translated'])+min(ss['cross']))
                semantic=self.semantic_decision(focus)
            elif len(groups)>1 and not (min(signal['cross'])>=self.config['whole_cross_min'] and min(signal['translated'])>=self.config['whole_mt_min']):
                # Both models must corroborate the SAME passage. Two weak
                # document scores can refer to unrelated sentences.
                semantic=None
            if semantic:
                # Diff is a navigation aid, not an asserted translation verdict.
                edits=[]
                fe=focus['english_span'] if focus else e
                fz=focus['chinese_span'] if focus else z
                fmt=focus['translation'] if focus else mt
                a=fe.split();b=fmt.split()
                for tag,l,h,j,k in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes():
                    if tag!='equal':edits.append({'english':' '.join(a[l:h]),'machine_backtranslation':' '.join(b[j:k])})
                reasons.append(dict(kind='contextual_model',category=semantic,why=f'{semantic}. Review the quoted passages; the machine back-translation is supporting evidence, not a reference translation.',english_span=fe,chinese_span=fz,machine_backtranslation=fmt,comparison_edits=edits))
            output[i]=dict(case_id=cases[i]['case_id'],flagged=bool(reasons),warnings=reasons,signals=signal,
                decision_path='v10_contextual_comparison',coverage='complete_notice',v7_fallback=False)
        for i,message in invalid.items():
            output[i]=dict(case_id=cases[i]['case_id'],flagged=True,warnings=[dict(kind='unresolved',category='input coverage',why=message,english_span=cases[i]['english'],chinese_span=cases[i]['chinese'])],decision_path='v10_unresolved',coverage='unresolved',v7_fallback=False)
        return [output[i] for i in range(len(cases))]

    def semantic_decision(self,s):
        c=self.config
        if s.get('translation_quality',1)<c['translation_quality_min']:return None
        x=max(s['cross']);m=max(s['translated']);b=min(s['translated'])
        if b>=c['mt_bidirectional'] and x>=c['cross_support']:
            return 'The complete versions give conflicting information'
        if m>=c['mt_oneway'] and x>=c['cross_support']:
            return 'Two semantic comparisons indicate a meaning difference'
        if s['similarity']<c['similarity_max'] and m>=c['mt_low_similarity'] and x>=c['cross_support']:
            return 'The versions may describe different facts or instructions'
        return None

    def check_notice(self,chinese_text,english_text):
        import pandas as pd
        r=self.predict_many([dict(case_id='interactive',chinese=chinese_text,english=english_text)])[0]
        warnings=r['warnings'] or [dict(why='',category='')]
        return pd.DataFrame([dict(status='⚠️ Check' if r['flagged'] else '✅ No discrepancy found',chinese=chinese_text,english=english_text,decision_path=r['decision_path'],coverage=r['coverage'],**w) for w in warnings])
