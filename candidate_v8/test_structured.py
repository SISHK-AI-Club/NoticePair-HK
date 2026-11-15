import unittest
from structured_notice import structured_comparison,parse_notice

class GrammarTests(unittest.TestCase):
    def check_pair(self,z,e,issue):
        parsed=structured_comparison(z,e)
        self.assertIsNotNone(parsed,(z,e))
        self.assertEqual(bool(parsed[2]),issue,(z,e,parsed[2]))

    def test_order_in_both_directions(self):
        for first,second in [('開立帳戶','提交申請'),('提交申請','開立帳戶')]:
            for order in ['before','after']:
                self.check_pair(f'辦理研討會時，請先{first}，再{second}。',f'For the seminar, submit your request {order} creating an account.',(first=='開立帳戶')!=(order=='after'))

    def test_month_end_not_quantity(self):
        for zoff in ['當月','後下一個月']:
            for eoff in ['in which','after']:
                self.check_pair(f'研討會收據的有效期於發出{zoff}最後一日屆滿。',f'A receipt for the seminar is valid until the end of the month {eoff} it was issued.',(zoff=='當月')!=(eoff=='in which'))

    def test_passive_duties_mutated_alternate(self):
        for a,b in [('班主任','領袖生'),('領袖生','班主任')]:
            self.check_pair(f'研討會期間的分工如下：名單由{a}核對。物資由{b}派發。','For the seminar, class teachers check the list and prefects distribute the materials.',a!='班主任')

    def test_group_modality_in_prose(self):
        for modal in ['須','毋須']:
            self.check_pair(f'個別人士可即場到訪研討會。團體則{modal}事先預約。','The seminar accepts walk-ins. Group visits must be booked in advance.',modal!='須')

    def test_correction_roles_not_sets(self):
        for a,b in [('13','24'),('24','13')]:
            self.check_pair(f'研討會移至{a}室。請勿依照舊告示前往{b}室。','seminar update: disregard Room 24 on the earlier sign. Use Room 13.',a!='13')

    def test_footnote_prose_and_audience(self):
        e='seminar schedule\nGeneral arrival: 10 p.m.\n* Performers report at 11 p.m. instead.'
        for a,b in [('10','11'),('11','10')]:
            self.check_pair(f'研討會一般到場時間為下午{a}時。表演者須按附註於下午{b}時報到。',e,a!='10')
        self.check_pair('研討會一般到場時間為下午10時。參展者須按附註於下午11時報到。',e,True)

    def test_extra_clause_never_ignored(self):
        z='研討會於下午3時開始。';e='The seminar starts at 3 p.m.'
        for extra in [' Participants must pay a fee.',' Only members may attend.','\nNo walk-ins.']:
            self.assertIsNone(structured_comparison(z,e+extra))
        for extra in ['參加者須繳費。','只限會員。','\n不設即場到訪。']:
            self.assertIsNone(structured_comparison(z+extra,e))

    def test_unsupported_condition_not_equated(self):
        self.assertIsNone(structured_comparison('研討會期間，如有職員於該處當值，側門便開放。','During the seminar, the side door is closed unless a staff member is on duty there.'))
        self.assertIsNone(parse_notice('The seminar starts at 3 p.m. only if staff arrive.','en'))

    def test_reviewer_guards(self):
        self.assertIsNone(parse_notice('下午3時開始書展並須攜帶學生證。','zh'))
        self.assertIsNone(parse_notice('書展期間，除非有職員在側門當值，仍側門關閉。','zh'))
        self.check_pair('研討會一般到場時間為下午10時。參展者須按附註於下午11時到場。','seminar schedule\nGeneral arrival: 10 p.m.\n* Exhibitors report at 11 p.m. instead.',True)

    def test_valid_clock_and_daypart(self):
        self.check_pair('研討會於上午12時開始。','The seminar starts at 12 a.m.',False)
        self.check_pair('研討會於下午12時開始。','The seminar starts at 12 a.m.',True)
        self.assertIsNone(parse_notice('研討會於下午25時開始。','zh'))
        self.check_pair('研討會於下午3時30分開始。','The seminar starts at 3:45 p.m.',True)

if __name__=='__main__':unittest.main()
