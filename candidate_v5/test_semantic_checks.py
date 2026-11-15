"""Development unit tests, not an independent linguistic evaluation."""
import unittest
from semantic_checks import semantic_evidence

class SemanticChecks(unittest.TestCase):
    def test_clean_equivalences(self):
        pairs = [
            ('訪客須帶備護照。','Visitors must bring a passport.'),
            ('訪客可攜帶護照。','Visitors may bring a passport.'),
            ('參加者毋須支付費用。','Participants do not need to pay a fee.'),
            ('如獲批准，參加者可上載文件。','If approved, participants may upload documents.'),
            ('除非獲准，否則須提交申請。','Submit an application unless permission is granted.'),
            ('收到通知後三個工作天內回覆。','Reply within three business days after receiving the notice.'),
            ('只有義工可報名。','Only volunteers may register.'),
            ('每個地址請提交表格。','Submit a form per address.'),
            ('請於星期二或之前歸還器材。','Return the equipment by Tuesday.'),
            ('申請人可預留門票。','Applicants may reserve tickets in May.'),
            ('須在網上提交文件。','You must submit documents online.'),
            ('申請人不得攜帶寵物。','Applicants must not bring pets.'),
            ('只有在住址不同的情況下才可分開提交。','Adults at different addresses may submit separate forms.'),
            ('請上載住址證明或學生證。','Upload proof of address or a student ID.'),
            ('須出席新崗位的培訓。','You must attend the training for your new role.'),
            ('下午6時已在排隊的人士可入場。','Anyone already in the queue at 6 p.m. may enter.'),
            ('除非獲准使用紙本，否則須在網上提交申請。','Submit the application online unless paper submission is approved.'),
            ('除非獲准，否則須在網上或以紙本提交申請。','Submit the application online or on paper unless an exemption is approved.'),
        ]
        for z,e in pairs:
            with self.subTest(z=z): self.assertEqual(semantic_evidence(z,e),[])
    def test_real_contrasts(self):
        pairs = [
            ('訪客可攜帶護照。','Visitors must bring a passport.','obligation'),
            ('訪客須攜帶護照。','Visitors may bring a passport.','obligation'),
            ('除非獲准，否則可提交申請。','Submit an application unless permission is granted.','obligation'),
            ('收到通知後三個曆日內回覆。','Reply within three business days after receiving the notice.','day-count'),
            ('通知發出後三個工作天內回覆。','Reply within three working days after receiving the notice.','deadline'),
            ('只有會員可報名。','Only volunteers may register.','eligible'),
            ('每個地址請提交表格。','Submit a form per household.','limit'),
            ('請於星期二之後歸還器材。','Return the equipment by Tuesday.','weekday'),
            ('如高於三號信號生效，活動取消。','The event is cancelled if Signal No. 3 or higher is in force.','threshold'),
            ('請上載住址證明或學生證。','Upload proof of address and a student ID.','document'),
            ('須出席原有崗位的培訓。','You must attend the training for your new role.','role'),
            ('下午6時後才加入隊伍的人士可入場。','Anyone already in the queue at 6 p.m. may enter.','queue'),
            ('同住人士只有在住址不同的情況下才可分開提交。','Adults sharing an address may submit separate forms.','address condition'),
            ('除非獲准使用紙本，否則須在網上或以紙本提交申請。','Submit the application online unless paper submission is approved.','submission options'),
        ]
        for z,e,category in pairs:
            with self.subTest(z=z):
                evidence=semantic_evidence(z,e)
                self.assertTrue(any(category in x['category'] for x in evidence),evidence)
                for x in evidence:
                    self.assertTrue(x['chinese_span']);self.assertTrue(x['english_span'])
    def test_unknown_or_ambiguous_abstains(self):
        for z,e in [('此文件很重要。','This document is important.'),
                    ('工作天與曆日的定義如下。','Definitions of working days and calendar days follow.'),
                    ('會員及義工均可申請。','Members and volunteers may apply.'),
                    ('請勿猜測。','Do not guess.')]:
            self.assertEqual(semantic_evidence(z,e),[])

if __name__=='__main__':unittest.main()
