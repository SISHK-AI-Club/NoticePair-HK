
# CELL 2
!pip -q install sentence-transformers gradio sentencepiece

import re
import itertools
import pandas as pd
import numpy as np
import torch

# CELL 4
rows = [
  # notice_id, chinese, english, has_error, error_type
  (1, "報名截止日期為2026年12月5日。", "The application deadline is 5 December 2026.", 0, "none"),
  (1, "報名截止日期為2026年12月5日。", "The application deadline is 15 December 2026.", 1, "number"),
  (2, "本活動只限65歲或以上長者參加。", "This activity is only open to elderly people aged 65 or above.", 0, "none"),
  (2, "本活動只限65歲或以上長者參加。", "This activity is open to everyone aged 65 or below.", 1, "meaning"),
  (3, "參加者毋須繳付任何費用。", "Participants do not need to pay any fee.", 0, "none"),
  (3, "參加者毋須繳付任何費用。", "Participants need to pay a fee.", 1, "negation"),
  (4, "報名截止日期為11月20日，活動將於11月27日舉行。", "The application deadline is 20 November, and the activity will be held on 27 November.", 0, "none"),
  (4, "報名截止日期為11月20日，活動將於11月27日舉行。", "The application deadline is 27 November, and the activity will be held on 20 November.", 1, "date_role"),
  (5, "請於11月20日下午5時前交回表格。", "Please return the form by 5 p.m. on 20 November.", 0, "none"),
  (5, "請於11月20日下午5時前交回表格。", "Please return the form by 5 p.m. on 30 November.", 1, "number"),
  (6, "如遇八號或以上颱風信號，活動將會取消。", "If Typhoon Signal No. 8 or above is hoisted, the activity will be cancelled.", 0, "none"),
  (6, "如遇八號或以上颱風信號，活動將會取消。", "If Typhoon Signal No. 8 or above is hoisted, the activity will still go ahead.", 1, "meaning"),
  (7, "名額有限，先到先得。", "Places are limited and will be allocated on a first-come, first-served basis.", 0, "none"),
  (7, "名額有限，先到先得。", "The quota is limited, first arrive first get.", 1, "awkward"),
  (8, "學生必須由家長陪同出席。", "Students must be accompanied by a parent.", 0, "none"),
  (8, "學生必須由家長陪同出席。", "Students may attend without a parent.", 1, "negation"),
  (9, "查詢請致電2345 6789。", "For enquiries, please call 2345 6789.", 0, "none"),
  (9, "查詢請致電2345 6789。", "For enquiries, please call 2345 6798.", 1, "number"),
  (10, "參加者必須於活動當日帶備身份證明文件。", "Participants must bring an identity document on the day of the activity.", 0, "none"),
  (10, "參加者必須於活動當日帶備身份證明文件。", "Participants may bring an identity document on the day of the activity.", 1, "meaning"),
  (11, "只限香港居民申請。", "Only Hong Kong residents may apply.", 0, "none"),
  (11, "只限香港居民申請。", "Applications are open to everyone, including visitors.", 1, "meaning"),
  (12, "活動將於2026年12月12日（星期六）舉行。", "The activity will be held on Saturday, December 12, 2026.", 0, "none"),
  (12, "活動將於2026年12月12日（星期六）舉行。", "The activity will be held on Sunday, December 13, 2026.", 1, "number"),
  (13, "申請截止日期為12月1日，課程將於12月8日開始。", "Applications close on 1 December, and the course starts on 8 December.", 0, "none"),
  (13, "申請截止日期為12月1日，課程將於12月8日開始。", "Applications close on 8 December, and the course starts on 1 December.", 1, "date_role"),
]
df = pd.DataFrame(rows, columns=["notice_id", "chinese", "english", "has_error", "error_type"])

import os
if os.path.exists("notices.csv"):          # upload notices.csv with the folder icon to use the full starter set
    df = pd.read_csv("notices.csv")

# Split by notice: about 1/3 of notices for tuning (dev), the rest for the final score (test).
# Nothing is ever tuned on test rows.
ids = sorted(df["notice_id"].unique())
dev_ids = set(ids[: max(1, len(ids) // 3)])
df["split"] = df["notice_id"].apply(lambda i: "dev" if i in dev_ids else "test")
print(df["split"].value_counts())
df

# CELL 6
def length_ratio(zh, en):
    return len(en.split()) / max(1, len(re.sub(r"\s", "", zh)))

dev_ok = df[(df.split == "dev") & (df.has_error == 0)]
ratios = [length_ratio(z, e) for z, e in zip(dev_ok.chinese, dev_ok.english)]
LOW, HIGH = min(ratios) * 0.8, max(ratios) * 1.2
print(f"Allowed English-words-per-Chinese-character range: {LOW:.2f} to {HIGH:.2f}")

def baseline_flag(zh, en):
    r = length_ratio(zh, en)
    return (r < LOW or r > HIGH), (["length looks off"] if (r < LOW or r > HIGH) else [])

# CELL 8
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = "cuda" if torch.cuda.is_available() else "cpu"
labse = SentenceTransformer("sentence-transformers/LaBSE", device=device)

NLI_NAME = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
nli_tok = AutoTokenizer.from_pretrained(NLI_NAME)
nli_model = AutoModelForSequenceClassification.from_pretrained(NLI_NAME).to(device).eval()
# find which output position means "contradiction" from the model's own label list
CONTRA = [i for i, name in nli_model.config.id2label.items() if "contra" in name.lower()][0]
print("NLI labels:", nli_model.config.id2label)

def similarity(zh, en):
    a, b = labse.encode([zh, en], convert_to_tensor=True, normalize_embeddings=True)
    return float(util.cos_sim(a, b))

def contradiction(zh, en):
    # probability that the two sentences contradict each other (higher of the two directions)
    scores = []
    for premise, hypothesis in [(zh, en), (en, zh)]:
        inputs = nli_tok(premise, hypothesis, truncation=True, max_length=256, return_tensors="pt").to(device)
        with torch.no_grad():
            probs = torch.softmax(nli_model(**inputs).logits[0], -1)
        scores.append(float(probs[CONTRA]))
    return max(scores)

# CELL 10
CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNITS = {"十": 10, "百": 100, "千": 1000}
CN_NUM = "零〇一二兩三四五六七八九十百千"

def cn_to_int(s):
    if s.isdigit():
        return int(s)
    total, num = 0, 0
    for ch in s:
        if ch in CN_DIGITS:
            num = CN_DIGITS[ch]
        elif ch in CN_UNITS:
            total += (num or 1) * CN_UNITS[ch]
            num = 0
    return total + num

MONTH_NAMES = ["january", "february", "march", "april", "may", "june", "july",
               "august", "september", "october", "november", "december"]
MONTHS = {m: i + 1 for i, m in enumerate(MONTH_NAMES)}
EN_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}

def numbers_zh(text):
    text = re.sub(r"(星期|週|周|禮拜)[一二三四五六日天]", "", text)   # weekdays are not numbers
    nums = {int(n) for n in re.findall(r"\d+", text)}
    nums |= {cn_to_int(m) for m in re.findall(rf"[{CN_NUM}]+", text)}
    return nums

def numbers_en(text):
    t = text.lower()
    nums = {int(n) for n in re.findall(r"\d+", t)}
    nums |= {v for k, v in {**MONTHS, **EN_WORDS}.items() if k != "may" and re.search(rf"\b{k}\b", t)}
    if re.search(r"\d\s*may\b|\bmay\s*\d", t):   # "may" is only a month next to a number
        nums.add(5)
    return nums

NEG_ZH = re.compile(r"不|毋|無須|无须|未|沒|没|勿|別|非")
NEG_EN = re.compile(r"\b(not|no|never|without|cannot|none|nobody)\b|n't")

def has_neg_en(text):
    text = re.sub(r"\bNo\.\s*\d", "", text)   # "No. 8" means "number 8", not a negation
    return bool(NEG_EN.search(text.lower()))

# CELL 11
# ---- Date roles: is this date an application deadline or an event date? ----
DEADLINE_ZH = re.compile(r"截止|報名|申請|遞交|交回|提交|日前|時前|或之前")
EVENT_ZH = re.compile(r"舉行|舉辦|進行|開始|開課|上課")
DEADLINE_EN = re.compile(r"\b(deadline|apply|application|applications|submit|return|enrol|enroll|enrolment|"
                         r"enrollment|register|registration|close|closes|closing|by|before)\b")
EVENT_EN = re.compile(r"\b(held|take place|takes place|start|starts|begin|begins|commence|commences)\b")

MONTH_RE = "|".join(MONTH_NAMES)

def dates_in_zh(clause):
    return {(cn_to_int(m), cn_to_int(d)) for m, d in re.findall(rf"([\d{CN_NUM}]+)月([\d{CN_NUM}]+)[日號号]", clause)}

def dates_in_en(clause):
    t = clause.lower()
    found = {(MONTHS[m], int(d)) for d, m in re.findall(rf"(?<!\d)(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({MONTH_RE})\b", t)}
    found |= {(MONTHS[m], int(d)) for m, d in re.findall(rf"\b({MONTH_RE})\s+(\d{{1,2}})(?!\d)", t)}
    return found

def role_of(clause, sentence, deadline_re, event_re):
    for text in (clause, sentence):          # look in the clause first, then the whole sentence
        if deadline_re.search(text):
            return "deadline"
        if event_re.search(text):
            return "event"
    return "other"

def date_roles(text, lang):
    roles = {"deadline": set(), "event": set(), "other": set()}
    if lang == "zh":
        sentences = [s for s in re.split(r"[。！？\n]", text) if s.strip()]
        for s in sentences:
            for clause in re.split(r"[，；、]", s):
                for d in dates_in_zh(clause):
                    roles[role_of(clause, s, DEADLINE_ZH, EVENT_ZH)].add(d)
    else:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])|\n", text) if s.strip()]
        for s in sentences:
            for clause in re.split(r"[;]|,\s+(?=and\b|but\b|while\b)", s):
                for d in dates_in_en(clause):
                    roles[role_of(clause.lower(), s.lower(), DEADLINE_EN, EVENT_EN)].add(d)
    return roles

def show_dates(ds):
    return ", ".join(f"{d} {MONTH_NAMES[m - 1].title()}" for m, d in sorted(ds))

def date_role_reasons(zh, en):
    rz, re_ = date_roles(zh, "zh"), date_roles(en, "en")
    names = {"deadline": "application deadline", "event": "event date"}
    out = []
    for role, label in names.items():
        if rz[role] and re_[role] and rz[role] != re_[role]:
            out.append(f"{label} differs: Chinese says {show_dates(rz[role])}, English says {show_dates(re_[role])}")
    return out

def rule_reasons(zh, en):
    reasons = []
    nz, ne = numbers_zh(zh), numbers_en(en)
    if nz != ne:
        missing, extra = sorted(nz - ne), sorted(ne - nz)
        parts = ([f"{missing} only in Chinese"] if missing else []) + ([f"{extra} only in English"] if extra else [])
        reasons.append("numbers differ: " + "; ".join(parts))
    if bool(NEG_ZH.search(zh)) != has_neg_en(en):
        reasons.append("one version says 'not/no/without' and the other doesn't")
    reasons += date_role_reasons(zh, en)
    return reasons

# quick check of the new rule
print(date_role_reasons("報名截止日期為11月20日，活動將於11月27日舉行。",
                        "The application deadline is 27 November, and the activity will be held on 20 November."))

# CELL 13
# ---- Improvement 1: "一" / "one" used as a word ("一名成人" = "an adult", "一經" = "once") is not a number to compare
_old_numbers_zh, _old_numbers_en = numbers_zh, numbers_en

def numbers_zh(text):
    text = re.sub(rf"(?<![{CN_NUM}])一(?![{CN_NUM}月日號时時])", "", text)   # drop a lone 一
    return _old_numbers_zh(text)

def numbers_en(text):
    return _old_numbers_en(re.sub(r"\bone\b", "", text, flags=re.I))

# ---- Improvement 2: weekdays must match (星期一 = Monday)
WEEKDAYS_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEKDAY_ZH = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}

def weekday_reasons(zh, en):
    wz = {WEEKDAY_ZH[d] for d in re.findall(r"(?:星期|週|周|禮拜)([一二三四五六日天])", zh)}
    we = {i for i, d in enumerate(WEEKDAYS_EN) if re.search(rf"\b{d}s?\b", en.lower())}
    if wz and we and wz != we:
        show = lambda s: ", ".join(WEEKDAYS_EN[i].title() for i in sorted(s))
        return [f"weekday differs: Chinese says {show(wz)}, English says {show(we)}"]
    return []

_old_rule_reasons = rule_reasons
def rule_reasons(zh, en):
    return _old_rule_reasons(zh, en) + weekday_reasons(zh, en)

# CELL 15
import unicodedata

def normalise_text(text, lang):
    text = unicodedata.normalize("NFKC", text)
    if lang == "en":
        text = re.sub(r"\bnoon\b", "12 p.m.", text, flags=re.I)
        text = re.sub(r"\bmidnight\b", "12 a.m.", text, flags=re.I)
    return text

_prev_numbers_zh, _prev_numbers_en = numbers_zh, numbers_en

def numbers_zh(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"一併|一同|一起|一致|一般", "", text)
    return _prev_numbers_zh(text)

def numbers_en(text):
    t = normalise_text(text, "en").lower()
    # "may" followed by a verb is the modal, not the month ("the 12 may apply")
    t = re.sub(r"\bmay(?=\s+(?:reserve|apply|attend|submit|register|bring|enrol|make|book)\b)", "can", t)
    nums = _prev_numbers_en(t)
    nums |= {v for k, v in {"both": 2, "second": 2}.items() if re.search(rf"\b{k}\b", t)}
    return nums

def negation_pair(zh, en):
    # paired grammatical equivalents keep the meaning of the whole clause
    if re.search(r"\bunless\b", en, re.I):
        zh = zh.replace("除非", "")
    if re.search(r"\bunder\b|\bbelow\b|less than", en, re.I):
        zh = zh.replace("未滿", "")
    zh = zh.replace("不同", "").replace("不論", "").replace("不管", "")
    return bool(NEG_ZH.search(zh)), has_neg_en(en)

def clock_values(text, lang):
    # every clock time in the text, as minutes after midnight
    text = normalise_text(text, lang)
    values = []
    if lang == "en":
        for hour, minute, half in re.findall(r"\b(\d{1,2})(?:[:.](\d{2}))?\s*([ap])\.?m\.?", text, re.I):
            hour = int(hour)
            if 1 <= hour <= 12:
                values.append((hour % 12 + (12 if half.lower() == "p" else 0)) * 60 + int(minute or 0))
    else:
        # "下午2時至6時" -> "下午2時至下午6時"
        text = re.sub(r"(上午|下午|中午|正午|晚上|凌晨)(\d{1,2})[時点點](至|到)(\d{1,2})[時点點]",
                      lambda m: f"{m[1]}{m[2]}時{m[3]}{m[1]}{m[4]}時", text)
        for half, hour, minute in re.findall(r"(上午|下午|中午|正午|晚上|凌晨)(\d{1,2})[時点點](?:(\d{1,2})分?)?", text):
            hour = int(hour)
            if hour <= 12:
                values.append((hour % 12 + (12 if half in ("下午", "中午", "正午", "晚上") else 0)) * 60 + int(minute or 0))
    return set(values)

def rule_reasons(zh, en):
    reasons = []
    nz, ne = numbers_zh(zh), numbers_en(en)
    if nz != ne:
        missing, extra = sorted(nz - ne), sorted(ne - nz)
        parts = ([f"{missing} only in Chinese"] if missing else []) + ([f"{extra} only in English"] if extra else [])
        reasons.append("numbers differ: " + "; ".join(parts))
    zc, ec = clock_values(zh, "zh"), clock_values(en, "en")
    if zc and ec and zc != ec:
        fmt = lambda vs: ", ".join(f"{v // 60:02d}:{v % 60:02d}" for v in sorted(vs))
        reasons.append(f"clock times differ: Chinese {fmt(zc)}; English {fmt(ec)}")
    zn, en_neg = negation_pair(zh, en)
    if zn != en_neg:
        reasons.append("one version says 'not/no/without' and the other doesn't")
    return reasons + date_role_reasons(zh, en) + weekday_reasons(zh, en)

# quick checks
assert numbers_en("noon") == {12}
print(rule_reasons("活動於下午2時開始。", "The activity starts at 2 a.m."))

# CELL 17
CN_DIGITS["○"] = 0
CN_NUM += "○"
_unit_cn_to_int = cn_to_int

def cn_to_int(s):
    # 二○二六 -> 2026 (digits written one by one, with no 十/百/千)
    if not s.isdigit() and len(s) > 1 and all(ch in CN_DIGITS for ch in s):
        return int("".join(str(CN_DIGITS[ch]) for ch in s))
    return _unit_cn_to_int(s)

_merged_numbers_zh, _merged_numbers_en, _merged_negation_pair = numbers_zh, numbers_en, negation_pair

def numbers_zh(text):
    text = re.sub(r"^\s*[（(][一二三四五六七八九十\d]+[)）]", "", text)   # list marker
    return _merged_numbers_zh(text)

def numbers_en(text):
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)                     # 1,370 -> 1370
    return _merged_numbers_en(text)

NOT_NEGATION_ZH = re.compile(r"分別|特別|個別|類別|性別|級別|區別|不等|不少|非常|未來")

def negation_pair(zh, en):
    return _merged_negation_pair(NOT_NEGATION_ZH.sub("", zh), en)

_digit_clock_values = clock_values

def clock_values(text, lang):
    if lang == "zh":   # 上午七時十五分 -> 上午7時15分
        text = re.sub(rf"[{CN_NUM}]+(?=[時点點分])", lambda m: str(cn_to_int(m[0])), text)
    return _digit_clock_values(text, lang)

assert numbers_en("from $330 to $1,370") == {330, 1370}
assert clock_values("上午七時起", "zh") == {420}
assert numbers_zh("二○二六年") == {2026}

# CELL 19
EN_ORDINALS = {"third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
_blind_numbers_zh, _blind_numbers_en, _blind_negation_pair = numbers_zh, numbers_en, negation_pair

def numbers_zh(text):
    text = re.sub(r"[一兩二三四]年一度", "", text)          # 兩年一度 = biennial: a frequency word, not a count
    return _blind_numbers_zh(text)

def numbers_en(text, zh=""):
    t = text.lower()
    t = re.sub(r"\bfutsal\b", "5-a-side football", t)        # 五人足球
    if re.search(r"半費|半價|一半", zh):                      # 半費 = "50 per cent" / "half price"
        t = re.sub(r"\b50\s*(?:per\s*cent|percent|%)", "half", t)
    nums = _blind_numbers_en(t)
    nums |= {v for k, v in EN_ORDINALS.items() if re.search(rf"\b{k}\b", t)}
    return nums

NOT_NEGATION_ZH_2 = re.compile(r"組別|識別|辨別")

def negation_pair(zh, en):
    return _blind_negation_pair(NOT_NEGATION_ZH_2.sub("", zh), en)

def rule_reasons(zh, en):
    reasons = []
    nz, ne = numbers_zh(zh), numbers_en(en, zh)
    if nz != ne:
        missing, extra = sorted(nz - ne), sorted(ne - nz)
        parts = ([f"{missing} only in Chinese"] if missing else []) + ([f"{extra} only in English"] if extra else [])
        reasons.append("numbers differ: " + "; ".join(parts))
    zc, ec = clock_values(zh, "zh"), clock_values(en, "en")
    if zc and ec and zc != ec:
        fmt = lambda vs: ", ".join(f"{v // 60:02d}:{v % 60:02d}" for v in sorted(vs))
        reasons.append(f"clock times differ: Chinese {fmt(zc)}; English {fmt(ec)}")
    zn, en_neg = negation_pair(zh, en)
    if zn != en_neg:
        reasons.append("one version says 'not/no/without' and the other doesn't")
    return reasons + date_role_reasons(zh, en) + weekday_reasons(zh, en)

# web links are not sentences: hide them from the pretrained models
URL_RE = re.compile(r"(?:https?://)?(?:[\w-]+\.)+[a-z]{2,}(?:/[\w./%-]*)?", re.I)
_raw_similarity, _raw_contradiction = similarity, contradiction

def similarity(zh, en):
    return _raw_similarity(URL_RE.sub("", zh), URL_RE.sub("", en))

def contradiction(zh, en):
    return _raw_contradiction(URL_RE.sub("", zh), URL_RE.sub("", en))

assert numbers_zh("兩年一度的運動會設有六個項目") == {6}
assert not rule_reasons("招募評審工作預計於二○二六年第三季完成。", "Assessment is expected to be completed around the third quarter of 2026.")
assert URL_RE.sub("", "visit hk.art.museum/en/web/ma/VB-Internship.html.").strip() == "visit"

# CELL 21
df["similarity"] = [similarity(z, e) for z, e in zip(df.chinese, df.english)]
df["contradiction"] = [contradiction(z, e) for z, e in zip(df.chinese, df.english)]
df["rule_reasons"] = [rule_reasons(z, e) for z, e in zip(df.chinese, df.english)]
df[["split", "error_type", "similarity", "contradiction", "rule_reasons", "english"]].round(2)

# CELL 22
def model_reasons(sim, contra, sim_t, nli_t):
    reasons = []
    if sim < sim_t:
        reasons.append(f"meaning may differ (similarity {sim:.2f})")
    if contra > nli_t:
        reasons.append(f"the two versions may contradict each other ({contra:.0%})")
    return reasons

def tune(dev, use_rules):
    best, best_key = (0.0, 1.0), (-1, -1, -1)
    for sim_t, nli_t in itertools.product(np.arange(0.40, 0.96, 0.02), np.arange(0.30, 1.0, 0.05)):
        flags = [bool(model_reasons(s, c, sim_t, nli_t) or (use_rules and r))
                 for s, c, r in zip(dev.similarity, dev.contradiction, dev.rule_reasons)]
        flags = np.array(flags); err = dev.has_error.values == 1
        tp, fp = (flags & err).sum(), (flags & ~err).sum()
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / err.sum()
        # reach 90% precision first, then most errors caught, then fewest false alarms, then the most cautious thresholds
        key = (precision >= 0.9, recall, -fp, nli_t, -sim_t)   # on ties, prefer the most cautious thresholds
        if key > best_key:
            best_key, best = key, (float(sim_t), float(nli_t))
    return best

dev = df[df.split == "dev"]
SIM_T_B, NLI_T_B = tune(dev, use_rules=False)   # B: pretrained models only
SIM_T, NLI_T = tune(dev, use_rules=True)        # C: full checker
print(f"B (models only): flag if similarity < {SIM_T_B:.2f} or contradiction > {NLI_T_B:.2f}")
print(f"C (full checker): flag if similarity < {SIM_T:.2f} or contradiction > {NLI_T:.2f}")

def checker_flag(zh, en, sim=None, contra=None):
    model_zh, model_en = normalise_text(zh, "zh"), normalise_text(en, "en")
    sim = similarity(model_zh, model_en) if sim is None else sim
    contra = contradiction(model_zh, model_en) if contra is None else contra
    reasons = rule_reasons(zh, en) + model_reasons(sim, contra, SIM_T, NLI_T)
    return bool(reasons), reasons

# CELL 24
# Trade-off on all development rows: how the contradiction threshold changes errors caught vs false alarms
err = df.has_error.values == 1
rows_t = []
for t in [0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8, 0.9, 0.95]:
    flags = np.array([bool(r) or c > t or s < SIM_T
                      for r, c, s in zip(df.rule_reasons, df.contradiction, df.similarity)])
    rows_t.append({"contradiction threshold": t,
                   "errors caught": f"{(flags & err).sum()} / {err.sum()}",
                   "false alarms": f"{(flags & ~err).sum()} / {(~err).sum()}"})
pd.DataFrame(rows_t)

# CELL 25
# Locked settings (chosen from the table above; change only with a written reason)
NLI_T = 0.65
NLI_T_B = 0.65
print(f"Locked: flag if similarity < {SIM_T:.2f} or contradiction > {NLI_T:.2f}")

# CELL 27
SYSTEMS = {
    "Baseline: length rule": lambda r: baseline_flag(r.chinese, r.english),
    "A. Rules only": lambda r: (bool(r.rule_reasons), r.rule_reasons),
    "B. Pretrained models only": lambda r: (lambda rs: (bool(rs), rs))(model_reasons(r.similarity, r.contradiction, SIM_T_B, NLI_T_B)),
    "C. Full checker": lambda r: checker_flag(r.chinese, r.english, r.similarity, r.contradiction),
}
FULL = "C. Full checker"

def evaluate(frame, title):
    frame = frame.copy()
    summary = []
    for name, fn in SYSTEMS.items():
        out = frame.apply(fn, axis=1)
        frame[name] = [o[0] for o in out]
        frame[name + " reasons"] = [o[1] for o in out]
        errs, oks = frame[frame.has_error == 1], frame[frame.has_error == 0]
        summary.append({"system": name,
                        "errors caught": f"{int(errs[name].sum())} / {len(errs)}",
                        "false alarms": f"{int(oks[name].sum())} / {len(oks)}"})
    print(title)
    display(pd.DataFrame(summary))
    print("Errors caught, by error type")
    display(frame[frame.has_error == 1].groupby("error_type")[list(SYSTEMS)].agg(lambda s: f"{int(s.sum())} / {len(s)}"))
    print("MISSED ERRORS (full checker)")
    display(frame[(frame.has_error == 1) & (~frame[FULL])][["error_type", "chinese", "english", "similarity", "contradiction"]])
    print("FALSE ALARMS (full checker)")
    display(frame[(frame.has_error == 0) & (frame[FULL])][["chinese", "english", FULL + " reasons"]])
    return frame

dev_results = evaluate(df, "DEVELOPMENT RESULTS (all starter rows)")

# CELL 29
import os
TEST_FILES = {"fresh_test.csv": "FIRST TEST SET, AFTER ALL FIXES (blind score was 20/22 caught, 12/26 false alarms)",
              "fresh_test_2.csv": "FINAL TEST SET, AFTER LATER FIXES (blind score was 19/21 caught, 7/26 false alarms)"}
test_results = {}
for path, title in TEST_FILES.items():
    if not os.path.exists(path):
        print(f"No {path} found yet. Upload it, then run this cell.")
        continue
    fresh = pd.read_csv(path)
    fresh["similarity"] = [similarity(z, e) for z, e in zip(fresh.chinese, fresh.english)]
    fresh["contradiction"] = [contradiction(z, e) for z, e in zip(fresh.chinese, fresh.english)]
    fresh["rule_reasons"] = [rule_reasons(z, e) for z, e in zip(fresh.chinese, fresh.english)]
    print(len(fresh), "rows:", fresh.has_error.value_counts().to_dict())
    test_results[path] = evaluate(fresh, title)

# CELL 31
from scipy.optimize import linear_sum_assignment

def split_zh(text):
    # keep conditions attached; split separate availability statements after a comma
    return [s.strip() for s in re.split(r"(?<=[。！？；])|\n|(?<=，)(?=(?:不設|設有))", text) if s and s.strip()]

def split_en(text):
    # split after . ! ? only when the next sentence starts with a capital letter,
    # so "5 p.m. on" and "No. 8" stay together
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?<=;)\s*|\n", text) if s and s.strip()]

def alignment_text(text, lang):
    # hide digits while matching, so a sentence is not matched just because its number is the same
    return re.sub(r"\d+", " ", normalise_text(text, lang))

def check_notice(chinese_text, english_text):
    zh, en = split_zh(chinese_text), split_en(english_text)
    if not zh or not en:
        return pd.DataFrame([{"status": "⚠️ Check", "chinese": chinese_text, "english": english_text, "why": "Paste both versions first."}])
    ez = labse.encode([alignment_text(s, "zh") for s in zh], convert_to_tensor=True, normalize_embeddings=True)
    ee = labse.encode([alignment_text(s, "en") for s in en], convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(ez, ee).cpu().numpy()
    # one-to-one matching over the whole notice, so two Chinese sentences cannot reuse one English sentence
    ii, jj = linear_sum_assignment(-sims)
    matches = dict(zip(ii.tolist(), jj.tolist()))
    used, out = set(), []
    for i, z in enumerate(zh):
        j = matches.get(i)
        if j is None or sims[i, j] < 0.25:
            out.append({"status": "⚠️ Check", "chinese": z, "english": "", "why": "Needs review: no confident English counterpart"})
            continue
        used.add(j)
        flagged, reasons = checker_flag(z, en[j])
        out.append({"status": "⚠️ Check" if flagged else "✅ OK", "chinese": z, "english": en[j], "why": "; ".join(reasons)})
    for j, e in enumerate(en):
        if j not in used:
            out.append({"status": "⚠️ Check", "chinese": "", "english": e, "why": "Needs review: no confident Chinese counterpart"})
    for reason in date_role_reasons(chinese_text, english_text):   # whole-notice date roles
        if not any(reason in row["why"] for row in out):
            out.append({"status": "⚠️ Check", "chinese": "(whole notice)", "english": "(whole notice)", "why": reason})
    return pd.DataFrame(out)

# CELL 33
fixture_zh = "報名截止日期為11月20日。活動將於11月27日舉行。參加者毋須繳付任何費用。"

fixtures = {
    "1. Clean pair (expect all OK)":
        "The application deadline is 20 November. The activity will be held on 27 November. Participants do not need to pay any fee.",
    "2. Swapped dates (expect a deadline warning)":
        "The application deadline is 27 November. The activity will be held on 20 November. Participants do not need to pay any fee.",
    "3. Reordered and reformatted (expect all OK)":
        "Participants do not need to pay any fee. The activity will be held on November 27. The application deadline is November 20.",
}
pd.set_option("display.max_colwidth", 120)
for name, english in fixtures.items():
    print("\n" + name)
    display(check_notice(fixture_zh, english))

# CELL 35
import gradio as gr

gr.Interface(
    fn=check_notice,
    inputs=[gr.Textbox(label="Traditional Chinese version", lines=8, value=fixture_zh),
            gr.Textbox(label="English version", lines=8, value=fixtures["2. Swapped dates (expect a deadline warning)"])],
    outputs=gr.Dataframe(label="Findings", wrap=True),
    title="Public Notice Check",
    description="A last check before a bilingual notice goes out. It flags sentences to review; a person makes the final call.",
).launch()

# CELL 37
import csv, json, time
from pathlib import Path
bench_path = Path("public_notice_benchmark.csv")
if bench_path.exists():
    with open(bench_path, encoding="utf-8-sig", newline="") as source:
        benchmark_cases = list(csv.DictReader(source))
    print(len(benchmark_cases), "cases; thresholds", SIM_T, NLI_T, "device", device)
    assert len(split_zh("網上報到於中午12時截止，不設即場名額。")) == 2
    output_path = Path("public_notice_predictions.jsonl")
    with output_path.open("w", encoding="utf-8") as sink:
        for n, case in enumerate(benchmark_cases, 1):
            start = time.perf_counter()
            result = {"case_id": case["case_id"]}
            try:
                result["rows"] = check_notice(case["chinese"], case["english"]).to_dict("records")
            except Exception as exc:
                result["error"] = repr(exc)
            result["seconds"] = round(time.perf_counter() - start, 3)
            sink.write(json.dumps(result, ensure_ascii=False) + "\n")
            if n % 10 == 0:
                print(n, "/", len(benchmark_cases))
    print("Benchmark complete: see", output_path)
else:
    print("No public_notice_benchmark.csv uploaded, skipping.")
