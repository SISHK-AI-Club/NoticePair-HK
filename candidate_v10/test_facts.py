import unittest
from facts import direct_evidence

class FactChecks(unittest.TestCase):
    def test_equivalent_rephrasings(self):
        for z,e in [
            ('公布的百分比以已完成的個案為分母。','The published percentage uses completed cases as the denominator.'),
            ('以零為起點。','Begin at zero.'),
            ('姓名不會在公開版本中披露。','Names are withheld from the published copy.'),
            ('即使照片維持不變，仍須重新取得同意。','Fresh consent is needed even if the photograph has not changed.'),
            ('電線長100厘米。','The cable is 1 metre long.'),
            ('請等待60分鐘。','Please wait 1 hour.'),
            ('費用為1,200港元。','The fee is HK$1,200.'),
            ('截止日期為十一月二十日。','The deadline is 20 November.'),
            ('全部學生須出席。','All students must attend.'),
            ('下週提供資料。','Information will be provided next week.'),
            ('活動於下午二時開始。','The activity starts at 2 p.m.'),
            ('請於正午回覆。','Please reply at noon.'),
            ('你毋須帶備文件。','You need not bring documents.'),
        ]:
            with self.subTest(z=z):self.assertEqual(direct_evidence(z,e),[])
    def test_concrete_discrepancies(self):
        for z,e,cat in [
            ('費用為130港元。','The fee is HK$120.','amount HKD'),
            ('請等待30分鐘。','Please wait 1 hour.','duration'),
            ('電線長2米。','The cable is 100 centimetres long.','length'),
            ('請使用藍色筆。','Please use a green pen.','colour'),
            ('只接受PDF格式。','Only CSV format is accepted.','file format'),
            ('請以毫米記錄高度。','Record the height in centimetres.','length unit'),
            ('箭嘴指向左方。','The arrow points right.','spatial direction'),
            ('最少18人。','More than 18 people.','inclusive/exclusive boundary'),
            ('活動於星期六舉行。','The event takes place on Sunday.','weekday'),
            ('代碼為AB-104。','The code is AB-105.','reference identifier'),
            ('請於下午二時回覆。','Please reply at 2 a.m.','clock time'),
            ('你必須帶備文件。','You may bring documents.','obligation to bring'),
            ('每月發出報告。','Reports are issued quarterly.','frequency'),
        ]:
            with self.subTest(z=z):self.assertIn(cat,{f['category'] for f in direct_evidence(z,e)})

if __name__=='__main__':unittest.main()
