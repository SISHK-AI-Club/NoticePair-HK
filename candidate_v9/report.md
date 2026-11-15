# V9 clause checking: 1,000-case development rerun

V9 reached 97.9% notice-level accuracy, caught 293/300 incorrect notices, missed 7, and falsely flagged 14/700 clean notices.

These cases previously formed V8’s unseen benchmark, but their failures informed V9. V9’s result is a development score, not held-out accuracy or a claim about real-world accuracy. The dataset has 38 repeated scenario families, not 1,000 independent structures. Some generated values are unrealistic, such as children aged 55, which further limits its value as a real-world benchmark.

| Difficulty | Cases | Accuracy V8 → V9 | Caught V8 → V9 | Missed V8 → V9 | False alarms V8 → V9 |
|---|---:|---:|---:|---:|---:|
| Routine | 600 | 88.5% → 100.0% | 165 → 180 | 15 → 0 | 54 → 0 |
| Difficult | 300 | 68.0% → 100.0% | 60 → 90 | 30 → 0 | 66 → 0 |
| Edge | 100 | 79.0% → 79.0% | 23 → 23 | 7 → 7 | 14 → 14 |
| Overall | 1000 | 81.4% → 97.9% | 248 → 293 | 52 → 7 | 134 → 14 |

Previously wrong decisions corrected: 165. Previously correct decisions made wrong: 0. Fresh baseline decisions reproduced 1000/1000 previous V8 decisions.

## What changed

- A clause-level parser extracts bilingual facts without requiring an entire notice to match a template. Recognised facts can appear alongside different headings, in a different order, or combined with other recognised clauses.
- Facts distinguish permission from obligation, refund exclusions, conditional submission channels, responsible actors, partial cancellation, time anchors, priority, inclusive thresholds, acknowledgement versus approval, and document custody.
- Additional concrete attributes cover gate colour, incoming/outgoing trays, front/back placement, and SMS/email delivery.
- Differences produce the compared values and the English and Chinese evidence spans.
- Unrecognised text, facts found in only one language, and repeated facts are retained for the V8 checker. V7 remains the underlying fallback for unsupported content.
- The neural model weights and similarity/contradiction thresholds are unchanged. This is a checking-logic improvement, not neural fine-tuning.

## Warning specificity

All 135 notices flagged by the new clause comparison had explicit bilingual evidence covering both expected issue spans after punctuation normalisation. All 135 were labelled incorrect; these include all 90 difficult errors. A review of one example from each of the 16 affected scenario families confirmed that the compared values describe the intended discrepancy. This is an evidence-coverage check and family-level review, not an independent bilingual adjudication of every warning. The other 158 caught notices rely on existing warnings, many of which only say the texts may contradict. Therefore 97.9% measures notice classification, not explanation correctness.

## Coverage and remaining dependence

Recorded candidate decision paths (a notice may have more than one path): {'frozen_fallback': 549, 'clause_facts_with_residual_review': 451, 'clause_facts': 135}.

The clause recognisers remain phrase-specific. They remove whole-notice layout dependence for supported clauses, but do not provide a general semantic parser. Unsupported paraphrases, coreference, quotations, and exceptions still need further work. Residual review remains necessary even on notices with recognised facts.

## Remaining errors by family

| Difficulty | Topic | Missed | False alarms |
|---|---|---:|---:|
| edge | Exception to exclusion | 4 | 0 |
| edge | Cross reference | 0 | 8 |
| edge | Grid assignment | 0 | 6 |
| edge | Embedded quotation | 3 | 0 |

## Remaining individual failures

### H0108 — FP — Cross reference
English: A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
— Storage and returns
Chinese: 寄存及退還 敬啟
甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0114 — FP — Cross reference
English: [Exhibition enquiries]

A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Chinese: 【展覽查詢】

甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0163 — FP — Cross reference
English: From: Campus facilities office

A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Chinese: 發訊單位：校園設施處

甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0241 — FN — Exception to exclusion
English: Operations desk
Late forms will be discarded unless the portal recorded a fault during your session. Even then, the fault must be reported by the applicant.
Chinese: 運作服務處
逾期表格一律作廢，惟系統有記錄閣下使用期間出現故障者除外。即使如此，該故障亦須由服務台報告。
Expected: Exception to exclusion: English specifies 'reported by the applicant' and Chinese specifies '由服務台報告'.
V9 warning: (none)

### H0311 — FN — Embedded quotation
English: Resident services unit
A notice marked “received” does not mean the request was approved. If a second notice says “ready”, the addressee may collect the item.
Chinese: 居民服務組
通知標示「已收到」並不代表申請獲批。只有在收到標示「可領取」的第二封通知後，任何人士方可領取物件。
Expected: Embedded quotation: English specifies 'the addressee' and Chinese specifies '任何人士'.
V9 warning: (none)

### H0420 — FP — Cross reference
English: From: Member services

A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Chinese: 發訊單位：會員服務

甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0466 — FN — Exception to exclusion
English: Community facility office
Late forms will be discarded unless the portal recorded a fault during your session. Even then, the fault must be reported by the applicant.
Chinese: 社區設施辦事處
逾期表格一律作廢，惟系統有記錄閣下使用期間出現故障者除外。即使如此，該故障亦須由服務台報告。
Expected: Exception to exclusion: English specifies 'reported by the applicant' and Chinese specifies '由服務台報告'.
V9 warning: (none)

### H0468 — FP — Grid assignment
English: Parcel enquiries
────────
Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
Chinese: 物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
────────
包裹查詢
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0475 — FP — Cross reference
English: A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
— District service kiosk
Chinese: 地區服務站 敬啟
甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0482 — FN — Embedded quotation
English: [District service kiosk]

A notice marked “received” does not mean the request was approved. If a second notice says “ready”, the addressee may collect the item.
Chinese: 【地區服務站】

通知標示「已收到」並不代表申請獲批。只有在收到標示「可領取」的第二封通知後，任何人士方可領取物件。
Expected: Embedded quotation: English specifies 'the addressee' and Chinese specifies '任何人士'.
V9 warning: (none)

### H0541 — FP — Cross reference
English: A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Issued by District service kiosk
Chinese: 地區服務站發布
甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0607 — FP — Grid assignment
English: [Media equipment desk]

Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
Chinese: 【媒體器材服務處】

物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0608 — FN — Exception to exclusion
English: Late forms will be discarded unless the portal recorded a fault during your session. Even then, the fault must be reported by the help desk.
Issued by Public records counter
Chinese: 公共紀錄櫃位發布
逾期表格一律作廢，惟系統有記錄閣下使用期間出現故障者除外。即使如此，該故障亦須由申請人報告。
Expected: Exception to exclusion: English specifies 'reported by the help desk' and Chinese specifies '由申請人報告'.
V9 warning: (none)

### H0697 — FP — Grid assignment
English: From: Service counter guide

Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
Chinese: 發訊單位：櫃位服務指南

物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0699 — FP — Cross reference
English: Student activities office
A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Chinese: 學生活動處
甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0719 — FN — Exception to exclusion
English: Media equipment desk
Late forms will be discarded unless the portal recorded a fault during your session. Even then, the fault must be reported by the applicant.
Chinese: 媒體器材服務處
逾期表格一律作廢，惟系統有記錄閣下使用期間出現故障者除外。即使如此，該故障亦須由服務台報告。
Expected: Exception to exclusion: English specifies 'reported by the applicant' and Chinese specifies '由服務台報告'.
V9 warning: (none)

### H0806 — FP — Grid assignment
English: Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
Issued by Resident services unit
Chinese: 居民服務組發布
物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0852 — FP — Grid assignment
English: Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
— Media equipment desk
Chinese: 媒體器材服務處 敬啟
物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0902 — FP — Cross reference
English: From: On-site instructions

A. Bring photo ID or a copy of the booking record.
B. For collection on behalf of someone else, the alternative in A cannot be used.
Chinese: 發訊單位：現場指引

甲、請帶備附相片的身分證明文件或預約紀錄副本。
乙、如代他人領取，甲項所列的預約紀錄副本不可作為替代文件。
Expected: Cross reference: English specifies 'cannot be used' and Chinese specifies '不可作為替代文件'.
V9 warning: Needs review: no confident Chinese counterpart
Needs review: no confident Chinese counterpart

### H0977 — FP — Grid assignment
English: Custody matrix
Key card → Reception
Visitor slips → Security
The recipient of each item signs once.
— School library services
Chinese: 學校圖書館服務 敬啟
物品交收表
接待處／門卡
保安處／訪客便條
每項物品均由接收者簽署一次。
Expected: Grid assignment: English specifies 'Security' and Chinese specifies '保安處'.
V9 warning: meaning may differ (similarity 0.38)

### H0985 — FN — Embedded quotation
English: [Visitor support]

A notice marked “received” does not mean the request was approved. If a second notice says “ready”, the addressee may collect the item.
Chinese: 【訪客服務】

通知標示「已收到」並不代表申請獲批。只有在收到標示「可領取」的第二封通知後，任何人士方可領取物件。
Expected: Embedded quotation: English specifies 'the addressee' and Chinese specifies '任何人士'.
V9 warning: (none)

## Reproducibility

Dataset SHA256: `d6b001a046e9d38409de9f65595f08c2dc216cc6c8fbf6606cbcacb0cfb3569b`
Candidate source SHA256: `2497f00d26f076da74278c300d619e585657e04bf3c59dd21109580c7dedaf92`
Run started: 2026-11-14T16:04:23.836293+00:00; completed: 2026-11-14T16:11:24.605684+00:00

Both versions ran fresh in the same Colab process with shared model objects. Inference receives only the bilingual text; scoring labels and rationales are used after prediction. The original CSV and frozen V8 were preserved. Five targeted parser tests passed, covering clause composition/reordering, numeric boundaries, retention of added content, duplicate extraction, and a misleading prefixed claim.

## Next validation

Freeze this version before testing again. A fresh evaluation should hold out entire phrasing and scenario families, include longer multi-clause notices and naturally authored formal Hong Kong Chinese, and score both the flag and its explanation. Report error recall and the false-alarm rate alongside accuracy; an always-clean checker already scores 70% on this class mix. Do not tune on the next holdout before reporting its initial score.
