import unittest
from pathlib import Path
from types import SimpleNamespace
import structured_notice as grammar

class FakeText(str):
    @property
    def str(self):return self
    def replace(self,old,new,regex=False):return FakeText(super().replace(old,new))

class AdapterTests(unittest.TestCase):
    def make(self,frozen_why="unchanged full-context assessment"):
        calls=[]
        def frozen(z,e):
            calls.append((z,e));return {'original_result':True,'why':FakeText(frozen_why)}
        ns={**vars(grammar),'check_notice':frozen,'SIM_T':.4,'NLI_T':.65,'similarity':lambda z,e:.2,'contradiction':lambda z,e:.99,'pd':SimpleNamespace(DataFrame=lambda rows:rows)}
        exec((Path(__file__).parent/'adapter.py').read_text(),ns)
        return ns,calls
    def test_uncertain_subject_defers_to_original(self):
        ns,calls=self.make()
        out=ns['check_notice']('研討會於下午3時開始。','The seminar starts at 3 p.m.')
        self.assertEqual(out['decision_path'],'uncertain_subject_fallback')
        self.assertEqual(len(calls),1)
        self.assertEqual(out['why'],'unchanged full-context assessment')
    def test_explicit_issue_survives_uncertain_subject(self):
        ns,calls=self.make()
        out=ns['check_notice']('研討會於下午4時開始。','The seminar starts at 3 p.m.')
        self.assertFalse(calls)
        self.assertEqual(out[0]['semantic_evidence'][0]['chinese_value'],'16:00')
        self.assertIn('time differs',out[0]['why'])
    def test_deadline_label_does_not_invent_application(self):
        ns,calls=self.make('application deadline differs: Chinese says 3 June, English says 4 June')
        out=ns['check_notice']('請回覆。','Please reply.')
        self.assertEqual(out['why'],'deadline differs: Chinese says 3 June, English says 4 June')

    def test_unknown_clause_uses_original(self):
        ns,calls=self.make()
        out=ns['check_notice']('研討會於下午3時開始。須繳費。','The seminar starts at 3 p.m.')
        self.assertEqual(out['decision_path'],'frozen_fallback')
        self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main()
