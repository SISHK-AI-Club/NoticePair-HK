"""Language-model signal features, without case IDs, topics or reference labels."""
import numpy as np
PROBS=('cross','cross_entailment','cross_neutral','translated','entailment','neutral')

def passage_vector(s):
    p=np.array([v for k in PROBS for v in s[k]],dtype=float)
    lp=np.log(np.clip(p,1e-5,1-1e-5)/np.clip(1-p,1e-5,1))
    summaries=[]
    for k in PROBS:
        a,b=s[k];summaries.extend([min(a,b),max(a,b),abs(a-b)])
    return np.r_[p,lp,summaries,[s['similarity'],s['translation_quality']]]

def vector(prediction):
    s=prediction['signals'];a=np.array([passage_vector(p) for p in s['passages']])
    direct=any(w['kind']=='explicit_fact' for w in prediction['warnings'])
    return np.r_[passage_vector(s),a.min(0),a.max(0),a.mean(0),len(a),int(direct)]


def feature_names():
    unit=[f'{p}.{direction}' for p in PROBS for direction in ['forward','reverse']]
    unit+=['logit.'+x for x in unit.copy()]
    unit+=[f'{p}.{stat}' for p in PROBS for stat in ['min','max','asymmetry']]
    unit+=['similarity','translation_quality']
    return [f'{group}.{name}' for group in ['whole','passage_min','passage_max','passage_mean'] for name in unit]+['passage_count','direct_fact']
