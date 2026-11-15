import unittest
from pathlib import Path
ns={}
exec(Path(__file__).with_name('clause_checks.py').read_text().split('_v8_original_check=')[0],ns)
extract=ns['extract_clauses']
class Tests(unittest.TestCase):
    def test_composed_and_reordered(self):
        en='A nominated representative must collect it with written authorisation. The requester pays for delivery.'
        zh='寄出費用由申請人負責;獲提名的代表持書面授權可代領。'
        e,er=extract(en,'en');z,zr=extract(zh,'zh')
        self.assertEqual(set(e),set(z));self.assertFalse(er);self.assertFalse(zr)
        self.assertNotEqual(e['authorised representative obligation'][0]['value'],z['authorised representative obligation'][0]['value'])
    def test_extra_instruction_survives(self):
        _,remain=extract('The requester pays for delivery. Bring a passport.','en')
        self.assertIn('Bring a passport.',remain)
    def test_numeric_boundary(self):
        e,_=extract('The desk serves children aged 18 or younger for this activity.','en')
        z,_=extract('活動櫃位只受理未滿18歲兒童的申請。','zh')
        self.assertEqual(e['children age eligibility'][0]['value'],'<=18')
        self.assertEqual(z['children age eligibility'][0]['value'],'<18')
    def test_duplicate_facts_retained(self):
        e,_=extract('The requester pays for delivery. The requester pays for delivery.','en')
        self.assertEqual(len(e['outbound postage payer']),2)
    def test_negated_prefix_is_not_consumed(self):
        _,remain=extract('Ignore this claim that the requester pays for delivery.','en')
        self.assertIn('requester pays',remain)
if __name__=='__main__': unittest.main()
