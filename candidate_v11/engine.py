"""Frozen V11: equivalence classification plus corroborated missing-detail checks.

The score is a learned decision score, not a calibrated probability of error.
No benchmark labels, scenario names or case IDs enter the scoring features.
"""
from pathlib import Path
import json
import re
import difflib
import numpy as np
try:
    from .backbone import SignalExtractor, MODEL_IDS, MODEL_REVISIONS
    from .features import vector, feature_names
    from .coverage_rules import unsupported_details
except ImportError:
    from backbone import SignalExtractor, MODEL_IDS, MODEL_REVISIONS
    from features import vector, feature_names
    from coverage_rules import unsupported_details


class Decision:
    def __init__(self):
        self.head = json.loads(Path(__file__).with_name('learned_head.json').read_text())
        assert self.head['feature_names'] == feature_names()

    def score(self, result):
        h = self.head
        x = (vector(result) - np.array(h['mean'])) / np.array(h['scale'])
        value = float(x @ np.array(h['coefficients']) + h['intercept'])
        return float(1 / (1 + np.exp(-np.clip(value, -50, 50))))

    def apply(self, result, english, chinese):
        if result['coverage'] != 'complete_notice':
            return result
        s = result['signals']
        score = self.score(result)
        detail_warnings = unsupported_details(s, english, chinese)
        for passage in s['passages']:
            detail_warnings += unsupported_details(passage, passage['english_span'], passage['chinese_span'])
        # Keep a detail once when both full-notice and aligned views support it.
        detail_warnings = list({(w['detail_language'], w['unsupported_detail']): w for w in detail_warnings}.values())
        flagged = score >= self.head['threshold'] or bool(detail_warnings)
        warnings = []
        if flagged:
            warnings = [w for w in result['warnings'] if w['kind'] == 'explicit_fact'] + detail_warnings
            if not warnings:
                warnings = [self.explain(result, english, chinese)]
        return dict(result, flagged=flagged, warnings=warnings, error_score=score,
            decision_threshold=self.head['threshold'],
            decision_path='v11_unsupported_detail' if detail_warnings else 'v11_learned_equivalence',
            v7_fallback=False)

    def explain(self, result, english, chinese):
        s = result['signals']
        options = []
        for p in s['passages']:
            ps = dict(p, passages=[p])
            options.append((self.score(dict(signals=ps, warnings=[])), p))
        # A passage is a navigation aid; the actual decision uses the full input.
        focus = max(options, key=lambda x: x[0])[1] if options else dict(s, english_span=english, chinese_span=chinese)
        e, z, mt = focus['english_span'], focus['chinese_span'], focus['translation']
        edits = []
        a, b = re.findall(r"\w+(?:['’-]\w+)*|[^\w\s]", e), re.findall(r"\w+(?:['’-]\w+)*|[^\w\s]", mt)
        for tag, i, j, k, l in difflib.SequenceMatcher(a=[x.lower() for x in a], b=[x.lower() for x in b], autojunk=False).get_opcodes():
            if tag != 'equal':
                edits.append(dict(english=' '.join(a[max(0,i-2):min(len(a),j+2)]), machine_backtranslation=' '.join(b[max(0,k-2):min(len(b),l+2)])))
        direction = int(np.argmax(np.array(focus['cross_neutral']) + np.array(focus['neutral'])))
        if min(focus['cross_neutral'][direction], focus['neutral'][direction]) >= .5:
            category = 'Missing or changed detail'
            if re.search(r'\b(?:unless|except|only if)\b|除非|豁免|例外', e+' '+z, re.I):
                category = 'Exception or condition may differ'
            elif re.search(r'\b(?:only|all|every|both|either|including|any)\b|僅|只|均|所有|包括', e+' '+z, re.I):
                category = 'Scope or requirement may differ'
        else:
            category = 'Facts or instructions may differ'
        # Always expose both actual passages; a generated gloss can be wrong.
        why = f'{category}. English states: “{e}”. The Chinese passage has the machine gloss: “{mt}”. Compare the highlighted wording against the original Chinese; the gloss can contain errors.'
        return dict(kind='equivalence_model', category=category, why=why,
            english_span=e, chinese_span=z, machine_backtranslation=mt,
            comparison_edits=edits)


class Checker(SignalExtractor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decision = Decision()

    def predict_many(self, inputs):
        results = super().predict_many(inputs)
        return [self.decision.apply(r, row['english'], row['chinese']) for r, row in zip(results, inputs)]

    def check_notice(self, chinese_text, english_text):
        import pandas as pd
        r = self.predict_many([dict(case_id='interactive', chinese=chinese_text, english=english_text)])[0]
        warnings = r['warnings'] or [dict(why='', category='')]
        return pd.DataFrame([dict(status='⚠️ Check' if r['flagged'] else '✅ No discrepancy found',
            chinese=chinese_text, english=english_text, coverage=r['coverage'],
            decision_path=r['decision_path'], **w) for w in warnings])
