"""Development guards for semantics that a broad suppression can accidentally erase."""
import contextlib
import io
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parent.parent

def rule_namespace():
    ns={'re':re,'similarity':lambda z,e:0.9,'contradiction':lambda z,e:0.0}
    base=json.loads((ROOT/'Public_Notice_Check_v4_tested.ipynb').read_text())
    with contextlib.redirect_stdout(io.StringIO()):
        for i in [10,11,13,15,17]:exec(''.join(base['cells'][i]['source']),ns)
        for path in ['merged_v5/ambiguity_normalisation.py','merged_v5/semantic_checks.py','merged_v5/relation_checks.py']:
            exec((ROOT/path).read_text(),ns)
    return ns

class MergedRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ns=rule_namespace()
    def evidence(self,z,e):
        return (self.ns['semantic_evidence'](z,e)+self.ns['ambiguity_evidence'](z,e)+self.ns['relation_evidence'](z,e))
    def flagged(self,z,e):return bool(self.ns['rule_reasons'](z,e) or self.evidence(z,e))

    def test_clean_normalisation(self):
        pairs=[
            ('運動會兩年一度舉行。','The games are held biennially.'),
            ('運動會每兩年舉行。','The games take place every other year.'),
            ('運動會一年一度舉行。','The games are held annually.'),
            ('學生可獲半費優惠。','Students receive a 50 per cent concession.'),
            ('學生門票半價。','Student tickets are half price.'),
            ('評審將於第三季完成。','Assessment will finish in the third quarter.'),
            ('設有五人足球。','Futsal is available.'),
            ('各項目分成兩個組別。','All events are divided into two groups.'),
            ('請核對識別編號。','Please check the identification number.'),
            ('詳情請瀏覽hk.art.museum/tc/web/ma/test.html。','For details visit hk.art.museum/en/web/ma/test.html.'),
            ('請瀏覽https://example.org/tc/form?id=12。','Please visit https://example.org/en/form?id=12.'),
        ]
        for z,e in pairs:
            with self.subTest(z=z):self.assertFalse(self.flagged(z,e),self.ns['rule_reasons'](z,e)+self.evidence(z,e))

    def test_suppression_must_not_hide_errors(self):
        pairs=[
            ('運動會兩年一度舉行。','The games are held annually.'),
            ('運動會每三年舉行。','The games take place every other year.'),
            ('學生可獲半費優惠。','Students receive a 25 per cent concession.'),
            ('評審將於第三季完成。','Assessment will finish in the fourth quarter.'),
            ('設有七人足球。','Futsal is available.'),
            ('各項目不分組別。','All events are divided into groups.'),
            ('請瀏覽https://example.org/tc/form?id=12。','Please visit https://example.org/en/form?id=21.'),
            ('請瀏覽https://example.org/tc/form。','Please visit https://different.org/en/form.'),
            ('請瀏覽https://example.org/tc/refund。','Please visit https://example.org/en/payment.'),
        ]
        for z,e in pairs:
            with self.subTest(z=z):self.assertTrue(self.flagged(z,e))

    def test_clean_relations(self):
        pairs=[
            ('如住址證明以家長名義發出,另須上載證明親屬關係的文件。',"If the proof is in your parent's name, also upload a document showing your relationship."),
            ('如住址證明由家長簽發,另須上載證明親屬關係的文件。','If the proof is issued by your parent, also upload a document showing your relationship.'),
            ('代領人須帶同收件人的身分證明文件副本及代領人本人的身分證明文件正本。','The proxy must bring a copy of your ID and their own original ID.'),
            ('代領人須帶同收件人的身分證明文件正本及代領人本人的身分證明文件副本。','The proxy must bring your original ID and a copy of their own ID.'),
            ('如未能親身取件,可委託他人代領。','You may send a proxy if you cannot collect your parcel.'),
            ('如未能在原定時段親身取件,可委託他人代領。','You may send a proxy if you cannot collect your parcel at the original slot.'),
            ('只有在兩名同行者均為其照顧者的情況下才可預留。','You may reserve only if both companions are your carers.'),
            ('其他合資格人士仍可報名。','Other eligible applicants can still register.'),
            ('其他合資格人士須待優先階段結束後才可報名。','Other eligible applicants may register after the priority period ends.'),
        ]
        for z,e in pairs:
            with self.subTest(z=z):self.assertEqual(self.evidence(z,e),[])

    def test_changed_relations(self):
        pairs=[
            ('如住址證明由家長簽發,另須上載證明親屬關係的文件。',"If the proof is in your parent's name, also upload a document showing your relationship.",'parent relationship'),
            ('代領人須帶同收件人的身分證明文件正本及代領人本人的身分證明文件副本。','The proxy must bring a copy of your ID and their own original ID.','ID document form'),
            ('如未能在原定時段親身取件,可委託他人代領。','You may send a proxy if you cannot collect your parcel.','proxy collection'),
            ('只有在其中一名同行者為其照顧者的情況下才可預留。','You may reserve only if both companions are your carers.','carer requirement'),
            ('其他合資格人士須待優先階段結束後才可報名。','Other eligible applicants can still register.','registration timing'),
        ]
        for z,e,c in pairs:
            with self.subTest(z=z):self.assertTrue(any(c in x['category'] for x in self.evidence(z,e)),self.evidence(z,e))

    def test_ambiguous_relationships_abstain(self):
        for z,e in [
            ('請帶同文件副本。','Bring their document.'),
            ('如未能取件可安排代領。','A proxy may collect at a suitable time.'),
            ('家長可簽發文件,亦可使用家長名下文件。','Documents may be issued by your parent or in your parent\'s name.'),
            ('運動會兩年一度,比賽每年舉行。','The games are biennial; the competition is annual.'),
        ]:
            with self.subTest(z=z):self.assertEqual(self.evidence(z,e),[])

if __name__=='__main__':unittest.main()
