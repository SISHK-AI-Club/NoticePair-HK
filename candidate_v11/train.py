"""Group-separated development fitting. Fresh holdout files are never read."""
from pathlib import Path
import json,hashlib,collections
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from features import vector,feature_names
r=Path(__file__).resolve().parent
records=json.loads((r/'dev_records.json').read_text())
X=np.array([vector(z['prediction']) for z in records]);y=np.array([z['gold']['expected_status']=='issue' for z in records],int)
groups=[z['dataset']+':'+z['gold']['family_id'] for z in records]
folds=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=1101).split(X,y,groups))
all_trials=[]
for C in [.01,.03,.1,.3,1]:
    prob=np.zeros(len(y));fold_ids=np.zeros(len(y),int)
    for f,(tr,va) in enumerate(folds):
        model=make_pipeline(StandardScaler(),LogisticRegression(C=C,max_iter=3000))
        model.fit(X[tr],y[tr]);prob[va]=model.predict_proba(X[va])[:,1];fold_ids[va]=f
    choices=[]
    for threshold in np.arange(.3,.981,.005):
        pred=prob>=threshold;tp=int(sum(pred & (y==1)));fp=int(sum(pred & (y==0)))
        choices.append(dict(threshold=float(round(threshold,4)),tp=tp,fp=fp,fn=int(sum(y)-tp),tn=int(sum(y==0)-fp),accuracy=float(np.mean(pred==y))))
    eligible=[q for q in choices if q['fp']<=28] # <=2% of 1,400 clean old notices.
    best=max(eligible,key=lambda q:(q['accuracy'],q['tp'],-q['fp'])) if eligible else min(choices,key=lambda q:(q['fp'],-q['tp']))
    all_trials.append(dict(C=C,**best,auc=float(roc_auc_score(y,prob))))
    np.savez(r/f'oof_C{C}.npz',prob=prob,fold=fold_ids)
    print(C,best,flush=True)
best=max(all_trials,key=lambda q:(q['accuracy'],q['tp'],-q['fp']))
C=best['C'];model=make_pipeline(StandardScaler(),LogisticRegression(C=C,max_iter=3000));model.fit(X,y)
scaler,clf=model.steps[0][1],model.steps[1][1]
export=dict(version='v11-equivalence-head',feature_names=feature_names(),mean=scaler.mean_.tolist(),scale=scaler.scale_.tolist(),coefficients=clf.coef_[0].tolist(),intercept=float(clf.intercept_[0]),threshold=best['threshold'],C=C)
(r/'learned_head.json').write_text(json.dumps(export,indent=2)+'\n')
assert len(feature_names())==X.shape[1]
manual=1/(1+np.exp(-(((X-scaler.mean_)/scaler.scale_)@clf.coef_[0]+clf.intercept_[0])))
assert np.allclose(manual,model.predict_proba(X)[:,1],rtol=1e-12,atol=1e-12)
oof=np.load(r/f'oof_C{C}.npz')['prob'];pred=oof>=best['threshold']
by={}
for tag in ['v9','v10']:
    ix=np.array([z['dataset']==tag for z in records]);truth=y[ix];pr=pred[ix]
    by[tag]=dict(tp=int(sum(pr & (truth==1))),fp=int(sum(pr & (truth==0))),fn=int(sum(~pr & (truth==1))),tn=int(sum(~pr & (truth==0))),accuracy=float(np.mean(pr==truth)))
issue_types=collections.defaultdict(lambda:collections.Counter())
for z,pr in zip(records,pred):
    if z['dataset']=='v10' and z['gold']['expected_status']=='issue':issue_types[z['gold']['issue_type']]['caught' if pr else 'missed']+=1
report=dict(kind='development model/threshold selection; not an untouched evaluation',selection='five family-disjoint folds; maximise accuracy with at most 28/1400 clean false positives; then refit all old data',rows=len(y),families=len(set(groups)),fresh_holdout_read=False,selected=best,trials=all_trials,by_dataset=by,old_v10_issue_types=issue_types,
 training_records_sha256=hashlib.sha256((r/'dev_records.json').read_bytes()).hexdigest())
(r/'training_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('SELECTED',best,'BY DATASET',by,'TARGET TYPES',{k:dict(issue_types[k]) for k in ['scope','exception','omission']})
