# Public Notice Check benchmark for approval

All 60 pairs are synthetic. The English source is fixed within each family. The Chinese uses written Hong Kong Traditional Chinese suitable for notices.

## N01 · Course registration (dev)

English source for all three rows

> Apply by 20 November. The class starts on 27 November.

### N01-C · clean

> 請於11月20日或之前報名。課程於11月27日開始。

20 November is the inclusive application deadline and 27 November is the class start in both versions.

### N01-1 · easy

> 請於11月21日或之前報名。課程於11月27日開始。

The application deadline moves from 20 to 21 November.

### N01-2 · hard

> 請於11月27日或之前報名。課程於11月20日開始。

20 and 27 November exchange roles as the deadline and class start.

## N02 · Equipment deposit (dev)

English source for all three rows

> Pay a refundable HK$50 deposit when collecting the kit.

### N02-C · clean

> 領取工具套裝時，須繳付港幣50元按金，按金可退還。

Both versions require a refundable HK$50 deposit at collection.

### N02-1 · easy

> 領取工具套裝時，須繳付港幣500元按金，按金可退還。

The deposit increases from HK$50 to HK$500.

### N02-2 · moderate

> 領取工具套裝時，須繳付港幣50元按金，按金不設退還。

A refundable deposit becomes non-refundable.

## N03 · Age eligibility (dev)

English source for all three rows

> Applicants aged 12 or over on 1 December may register.

### N03-C · clean

> 於12月1日年滿12歲的人士可報名。

年滿 includes applicants who turn 12 on 1 December as well as older applicants.

### N03-1 · easy

> 於12月1日年滿13歲的人士可報名。

The minimum age rises from 12 to 13.

### N03-2 · hard

> 於12月1日未滿12歲的人士可報名。

Eligibility flips from age 12 and above to under 12 while the numbers stay the same.

## N04 · ID at check-in (dev)

English source for all three rows

> Participants must bring their original ID to check-in at Room 208.

### N04-C · clean

> 參加者須攜同身分證明文件正本到208室辦理登記。

Both require the original ID at Room 208, rather than a copy.

### N04-1 · easy

> 參加者須攜同身分證明文件正本到280室辦理登記。

Check-in moves from Room 208 to Room 280.

### N04-2 · moderate

> 參加者可攜同身分證明文件正本到208室辦理登記。

Bringing the original ID becomes optional.

## N05 · Dress rehearsal (dev)

English source for all three rows

> Report at 5 p.m. on 8 May. Only performers need to bring a music stand.

### N05-C · clean

> 請於5月8日下午5時報到。只有演出者須攜帶譜架。

Both specify 5 p.m. on 8 May and limit the stand requirement to performers.

### N05-1 · easy

> 請於5月8日下午6時報到。只有演出者須攜帶譜架。

Reporting moves from 5 p.m. to 6 p.m.

### N05-2 · moderate

> 請於5月8日下午5時報到。所有參加者須攜帶譜架。

The stand requirement expands from performers to everyone.

## N06 · Borrowing equipment (dev)

English source for all three rows

> Return the tablet by Friday. A charger is required only if one was issued with the tablet.

### N06-C · clean

> 請於星期五或之前歸還平板電腦。如借用平板電腦時獲發充電器，才須一併歸還。

Both allow return on Friday and require the charger only when it was issued.

### N06-1 · moderate

> 請於星期五之後歸還平板電腦。如借用平板電腦時獲發充電器，才須一併歸還。

The return window changes from by Friday to after Friday.

### N06-2 · very hard

> 請於星期五或之前歸還平板電腦。如借用平板電腦時沒有獲發充電器，才須一併歸還。

The charger condition reverses, requiring a return only from borrowers who never received one.

## N07 · Refund contact (holdout)

English source for all three rows

> For refunds, call 2345 6789. For transfers, call 2345 6798.

### N07-C · clean

> 查詢退款請致電2345 6789；查詢轉讓名額請致電2345 6798。

Both assign 2345 6789 to refunds and 2345 6798 to transfers.

### N07-1 · easy

> 查詢退款請致電2345 6780；查詢轉讓名額請致電2345 6798。

The refund number changes from 2345 6789 to 2345 6780.

### N07-2 · hard

> 查詢退款請致電2345 6798；查詢轉讓名額請致電2345 6789。

Both telephone numbers remain but their purposes are swapped.

## N08 · Online check-in (holdout)

English source for all three rows

> Online check-in closes at noon. Walk-in places are not available.

### N08-C · clean

> 網上報到於中午12時截止，不設即場名額。

中午12時 is noon and 不設 denies walk-in places.

### N08-1 · easy

> 網上報到於下午2時截止，不設即場名額。

Online check-in closes two hours later.

### N08-2 · moderate

> 網上報到於中午12時截止，設有即場名額。

Walk-in places become available.

## N09 · Class fee waiver (holdout)

English source for all three rows

> The course fee is HK$80. Members and volunteers may apply. Only members who are full-time students qualify for a fee waiver.

### N09-C · clean

> 課程費用為港幣80元。會員及義工均可申請。只有屬全日制學生的會員可獲豁免費用。

Both groups can apply, while only members who are full-time students qualify for the waiver.

### N09-1 · easy

> 課程費用為港幣90元。會員及義工均可申請。只有屬全日制學生的會員可獲豁免費用。

The fee rises from HK$80 to HK$90.

### N09-2 · very hard

> 課程費用為港幣80元。會員及義工均可申請。只有屬全日制學生的義工可獲豁免費用。

The waiver moves from full-time students who are members to full-time students who are volunteers.

## N10 · Pickup slot (holdout)

English source for all three rows

> Collect your pass from 9 a.m. to 11 a.m. at Counter 3. The counter closes at noon.

### N10-C · clean

> 櫃位於中午12時關閉。請於上午9時至11時到3號櫃位領取通行證。

The Chinese reverses the sentence order and writes noon as 中午12時. Pickup remains 9 to 11 a.m. at Counter 3.

### N10-1 · easy

> 櫃位於中午12時關閉。請於上午9時至11時到8號櫃位領取通行證。

Pass collection is directed to Counter 8 instead of Counter 3.

### N10-2 · hard

> 櫃位於中午12時關閉。請於上午11時至正午12時到3號櫃位領取通行證。

The pickup window starts at the original cutoff and ends at the counter closing time.

## N11 · Submission methods (holdout)

English source for all three rows

> Submit the form online unless the office has approved a paper submission.

### N11-C · clean

> 除非辦事處已批准以紙本遞交，否則須在網上提交表格。

Both require online submission unless the office has approved a paper submission.

### N11-1 · moderate

> 除非辦事處已批准以紙本遞交，否則可在網上提交表格。

The online submission requirement becomes permission.

### N11-2 · very hard

> 除非辦事處已批准以紙本遞交，否則可在網上或以紙本提交表格。

Applicants without approval gain a paper option, undermining the exception.

## N12 · Weather trigger (holdout)

English source for all three rows

> The trip is cancelled if Typhoon Signal No. 8 or higher is in force at 7 a.m.

### N12-C · clean

> 如上午7時仍有八號或以上熱帶氣旋警告信號生效，行程將取消。

八號或以上 includes Signal No. 8 itself, and the trigger is evaluated at 7 a.m.

### N12-1 · easy

> 如上午8時仍有八號或以上熱帶氣旋警告信號生效，行程將取消。

The time for checking the weather signal changes from 7 to 8 a.m.

### N12-2 · hard

> 如上午7時仍有高於八號熱帶氣旋警告信號生效，行程將取消。

Signal No. 8 itself stops triggering cancellation.

## N13 · Companion tickets (holdout)

English source for all three rows

> Each attendee may reserve one companion ticket. Attendees under 12 may reserve a second ticket only if both companions are their carers.

### N13-C · clean

> 每名參加者可預留一張同行者門票。未滿12歲的參加者只有在兩名同行者均為其照顧者的情況下，才可多預留一張。

Both allow one companion ticket and require two carers for the under-12 second-ticket exception.

### N13-1 · moderate

> 每名參加者須預留一張同行者門票。未滿12歲的參加者只有在兩名同行者均為其照顧者的情況下，才可多預留一張。

An optional companion ticket becomes mandatory.

### N13-2 · very hard

> 每名參加者可預留一張同行者門票。未滿12歲的參加者只有在其中一名同行者為其照顧者的情況下，才可多預留一張。

One carer is sufficient for the extra ticket, even if the other companion is not a carer.

## N14 · Waitlist reply (holdout)

English source for all three rows

> Waitlisted applicants must reply within two working days after receiving an offer.

### N14-C · clean

> 候補申請人須於收到補錄通知後兩個工作天內回覆。

Both count two working days from receipt of the waitlist offer.

### N14-1 · moderate

> 候補申請人須於收到補錄通知後兩個曆日內回覆。

The reply window counts weekends and holidays instead of working days only.

### N14-2 · hard

> 候補申請人須於補錄通知發出後兩個工作天內回覆。

The reply clock starts when the offer is issued instead of when it is received.

## N15 · Proof of address (holdout)

English source for all three rows

> Upload proof of address and a student ID. If the proof is in your parent’s name, also upload a document showing your relationship.

### N15-C · clean

> 請上載住址證明及學生證。如住址證明以家長名義發出，另須上載證明親屬關係的文件。

Both require two documents and add relationship evidence when the address proof names a parent.

### N15-1 · moderate

> 請上載住址證明或學生證。如住址證明以家長名義發出，另須上載證明親屬關係的文件。

Applicants can upload either document instead of supplying both.

### N15-2 · very hard

> 請上載住址證明及學生證。如住址證明由家長簽發，另須上載證明親屬關係的文件。

The extra evidence is triggered by who issued the proof instead of whose name appears on it.

## N16 · Pickup proxy (holdout)

English source for all three rows

> You may send a proxy if you cannot collect your parcel. The proxy must bring a copy of your ID and their own original ID.

### N16-C · clean

> 如未能親身取件，可委託他人代領。代領人須帶同收件人的身分證明文件副本及代領人本人的身分證明文件正本。

Both permit a proxy when needed and ask for the recipient’s copy and the proxy’s original ID.

### N16-1 · hard

> 如未能親身取件，可委託他人代領。代領人須帶同收件人的身分證明文件正本及代領人本人的身分證明文件副本。

The original and copy requirements are assigned to the opposite people.

### N16-2 · very hard

> 如未能在原定時段親身取件，可委託他人代領。代領人須帶同收件人的身分證明文件副本及代領人本人的身分證明文件正本。

Proxy eligibility narrows to inability to attend the original slot, so someone unable to attend a rescheduled slot loses this option.

## N17 · Induction exemption (holdout)

English source for all three rows

> Returning volunteers may skip induction. Returning volunteers who changed roles must attend the session for their new role.

### N17-C · clean

> 曾參與的義工可免出席簡介會。如已轉換崗位，則須出席新崗位的簡介會。

Both waive induction for unchanged roles and require the new role’s induction after a switch.

### N17-1 · moderate

> 曾參與的義工不得缺席簡介會。如已轉換崗位，則須出席新崗位的簡介會。

Returning volunteers in the same role must now attend.

### N17-2 · very hard

> 曾參與的義工可免出席簡介會。如已轉換崗位，則須出席原有崗位的簡介會。

Volunteers who changed roles are sent to induction for their former role.

## N18 · Registration priority (holdout)

English source for all three rows

> Residents living in the district for at least six months get priority. Other eligible applicants can still register.

### N18-C · clean

> 在區內居住滿六個月的居民可獲優先安排。其他合資格人士仍可報名。

Both grant priority at six months of district residence while allowing other eligible people to apply.

### N18-1 · hard

> 在區內居住未滿六個月的居民可獲優先安排。其他合資格人士仍可報名。

Priority shifts from residents of at least six months to newer residents.

### N18-2 · very hard

> 在區內居住滿六個月的居民方可在優先報名階段報名。其他合資格人士須待優先階段結束後才可報名。

Priority in allocation becomes an earlier registration window, restricting when other eligible applicants can apply.

## N19 · Queue cutoff (holdout)

English source for all three rows

> Anyone already in the queue at 4 p.m. will be served, even if the counter stops admitting new arrivals before they are served.

### N19-C · clean

> 下午4時已在排隊的人士，即使輪候期間櫃位停止接受新到人士排隊，仍可獲服務。

Both protect anyone in line at 4 p.m. even if the queue closes to new arrivals before they are served.

### N19-1 · hard

> 下午4時後才加入隊伍的人士，即使輪候期間櫃位停止接受新到人士排隊，仍可獲服務。

Guaranteed service goes to late arrivals instead of people already queued at the cutoff.

### N19-2 · very hard

> 下午4時已在排隊的人士，但如輪候期間櫃位停止接受新到人士排隊，便不獲服務。

The queue guarantee becomes contingent on the counter still admitting new arrivals when the person is served.

## N20 · Household application (holdout)

English source for all three rows

> Submit one form per household. Adults sharing an address may submit separate forms if they manage their finances separately.

### N20-C · clean

> 每個住戶請提交一份表格。同住的成年人如各自管理財務，可分開提交表格。

Both use one form per household and allow separate forms for financially independent adults sharing an address.

### N20-1 · hard

> 每個地址請提交一份表格。同住的成年人如各自管理財務，可分開提交表格。

The submission limit applies per address, grouping distinct households at the same address.

### N20-2 · very hard

> 每個住戶請提交一份表格。同住的成年人如各自管理財務，但只有在住址不同的情況下才可分開提交表格。

The separate-filing exception becomes unusable for the same-address adults it is meant to cover.
