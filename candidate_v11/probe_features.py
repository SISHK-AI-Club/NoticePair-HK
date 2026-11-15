import json,csv,collections
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier,ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
root=Path(__file__).resolve().parent.parent
records=[]
for dataset,predfile,tag in [('holdout_v10/v10_blind_1000.csv','holdout_v10/v10_results.json','v10'),('holdout_v9/v9_unseen_1000.csv','candidate_v10/old_v9_full_results.json','v9')]:
 gold={r['case_id']:r for r in csv.DictReader((root/dataset).open(encoding='utf-8-sig'))}
 for p in json.loads((root/predfile).read_text())['results']:
  records.append((gold[p['case_id']],p,tag))
keys=['cross','cross_entailment','cross_neutral','translated','entailment','neutral']
def vec(s):
 return [v for k in keys for v in s[k]]+[s['similarity'],s['translation_quality']]
def features(p):
 s=p['signals'];ps=s['passages'];a=np.array([vec(x) for x in ps])
 return vec(s)+list(a.min(0))+list(a.max(0))+list(a.mean(0))+[len(ps),int(any(x['kind']=='explicit_fact' for x in p['warnings']))]
X=np.array([features(p) for g,p,t in records]);y=np.array([g['expected_status']=='issue' for g,p,t in records]);groups=[t+g['family_id'] for g,p,t in records]
folds=list(StratifiedGroupKFold(5,shuffle=True,random_state=1101).split(X,y,groups))
for name,ctor in [('logistic',lambda:make_pipeline(StandardScaler(),LogisticRegression(C=.1,max_iter=2000))),('hist',lambda:HistGradientBoostingClassifier(max_iter=120,max_leaf_nodes=7,l2_regularization=10,learning_rate=.07,random_state=11)),('extra',lambda:ExtraTreesClassifier(n_estimators=200,min_samples_leaf=12,max_features=.8,random_state=11,n_jobs=2))]:
 prob=np.zeros(len(y))
 for tr,va in folds:
  m=ctor();m.fit(X[tr],y[tr]);prob[va]=m.predict_proba(X[va])[:,1]
 print(name)
 for threshold in [.3,.4,.5,.6,.7,.8,.9]:
  pred=prob>=threshold;tp=int(sum(pred&y));fp=int(sum(pred&~y));print(threshold,'acc',float(np.mean(pred==y)),'tp',tp,'fp',fp,'recall',tp/sum(y))
 for tag in ['v9','v10']:
  ids=np.array([t==tag for _,_,t in records]);p=prob>=.5;print(tag,float(np.mean(p[ids]==y[ids])),int(sum(p[ids]&y[ids])),int(sum(p[ids]&~y[ids])))
np.savez(root/'candidate_v11/dev_features.npz',X=X,y=y,groups=groups)
(root/'candidate_v11/dev_records.json').write_text(json.dumps([dict(gold=g,prediction=p,dataset=t) for g,p,t in records],ensure_ascii=False))
