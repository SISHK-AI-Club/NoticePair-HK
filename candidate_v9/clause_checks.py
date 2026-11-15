"""Compositional bilingual clause facts, with unresolved text retained for V8."""
import re
import unicodedata
from collections import defaultdict

CLAUSE_RULES = []
def clause(key, en, zh, en_value=None, zh_value=None):
    CLAUSE_RULES.append((key,re.compile(en,re.I),re.compile(zh),en_value,zh_value))

def normal(text):
    return unicodedata.normalize('NFKC',text).replace('，',',').replace('；',';')

def fixed(key,en,zh):
    clause(key,en,zh,lambda m:'present',lambda m:'present')

fixed('unregistered viewing',r'You may view the records without registering\.',r'查閱紀錄無須登記;')
clause('registration scope',r'Registration is compulsory (only if you want to download a copy|whether or not you want to download a copy)\.',r'(僅在需要下載副本時才|無論是否需要下載副本,均)必須登記。',lambda m:'download only' if m[1].startswith('only') else 'all viewers',lambda m:'download only' if m[1].startswith('僅') else 'all viewers')
fixed('application fee refund',r'Application fees can be refunded\.',r'申請費可退回。')
clause('courier refund on withdrawal before review',r'Courier charges are (excluded|also refunded), even when the application is withdrawn before review\.',r'即使申請在審閱前撤回,亦(不退還|會退還)速遞費。',lambda m:'excluded' if m[1]=='excluded' else 'refunded',lambda m:'excluded' if m[1]=='不退還' else 'refunded')
clause('children age eligibility',r'The desk serves children (aged (\d+) or younger|under (\d+)) for this activity\.',r'活動櫃位只受理((\d+)歲或以下|未滿(\d+)歲)兒童的申請。',lambda m:('<=' if m[2] else '<')+(m[2] or m[3]),lambda m:('<=' if m[2] else '<')+(m[2] or m[3]))
fixed('older children route',r'Older children should use the main booking page\.',r'年齡較大的兒童請使用主預約頁面。')
fixed('prefer upload',r'Use the upload page whenever possible\.',r'請盡量使用上載頁面;')
clause('postal submission condition',r'Send the file by post only if the page is (unavailable|available)\.',r'只在頁面(無法使用|可以使用)時才可郵寄文件。',lambda m:'page unavailable' if m[1]=='unavailable' else 'page available',lambda m:'page unavailable' if m[1]=='無法使用' else 'page available')
fixed('held for collection',r'The item will be held for collection\.',r'物件會保留待領;')
clause('authorised representative obligation',r'A nominated representative (may|must) collect it with written authorisation\.',r'獲提名的代表持書面授權(可|必須)代領。',lambda m:'permitted' if m[1]=='may' else 'required',lambda m:'permitted' if m[1]=='可' else 'required')
fixed('outbound postage payer',r'The requester pays for delivery\.',r'寄出費用由申請人負責;')
clause('return postage payer',r'For a return, the (recipient|requester) pays the postage\.',r'退回物件的郵費由(收件人|申請人)支付。',lambda m:m[1],lambda m:{'收件人':'recipient','申請人':'requester'}[m[1]])
clause('other items after partial cancellation',r'If you cancel one item, the other items are (kept on the order|removed from the order)\.',r'如取消其中一項,其餘項目(仍保留在訂單內|亦會從訂單移除)。',lambda m:'retained' if m[1].startswith('kept') else 'removed',lambda m:'retained' if m[1].startswith('仍') else 'removed')
fixed('confirmation number retained',r'Your confirmation number stays the same\.',r'確認編號維持不變。')
clause('retention start and duration',r'The retention period starts on the day staff (receive|approve) the form; it lasts (\d+) days\.',r'紀錄由職員(收到|批准)表格當日起保留(\d+)日。',lambda m:('receipt' if m[1]=='receive' else 'approval')+'; '+m[2]+' days',lambda m:('receipt' if m[1]=='收到' else 'approval')+'; '+m[2]+' days')
clause('priority when simultaneous',r'When both groups arrive together, serve people (with|without) an appointment first\.',r'兩組人士同時抵達時,請先為(已|未)預約人士提供服務。',lambda m:'booked' if m[1]=='with' else 'unbooked',lambda m:'booked' if m[1]=='已' else 'unbooked')
fixed('single waiting queue',r'Everyone should wait in the same line\.',r'所有人須在同一隊伍等候。')
clause('fee waiver threshold',r'The fee is waived on orders of (at least|more than) HK\$(\d+)\.',r'訂單金額(達|超過)(\d+)港元可免付費用;',lambda m:('>=' if m[1]=='at least' else '>')+m[2]+' HKD',lambda m:('>=' if m[1]=='達' else '>')+m[2]+' HKD')
fixed('ordinary fee otherwise',r'Otherwise, the usual fee applies\.',r'其餘訂單照常收費。')
clause('automated acknowledgement status',r'An automated reply confirms (receipt|approval) of the request\.',r'系統電郵只確認已(收到|批准)申請。',lambda m:m[1],lambda m:'receipt' if m[1]=='收到' else 'approval')
fixed('later decision after review',r'A decision will be sent separately after staff review\.',r'職員審查後會另行通知結果。')
fixed('countersigning officer',r'The duty officer countersigns each form;',r'每份表格由當值主任加簽,')
clause('signed original custodian',r'the (applicant|duty officer) keeps the signed original\.',r'正本由(申請人|當值主任)保管。',lambda m:m[1],lambda m:'applicant' if m[1]=='申請人' else 'duty officer')
fixed('shared scan destination',r'A scan goes into the shared folder\.',r'掃描本存入共用資料夾。')

# Common concrete attributes and instructions can be composed with any context.
clause('entry gate colour',r'Entry for this activity is through the (green|blue|red|yellow) gate\.',r'本活動參加者請經(綠色|藍色|紅色|黃色)閘口入場;',lambda m:m[1],lambda m:{'綠色':'green','藍色':'blue','紅色':'red','黃色':'yellow'}[m[1]])
fixed('concourse available',r'The main concourse remains open as usual\.',r'大堂照常開放。')
clause('signed record tray',r'When finished, leave the signed record in the (outgoing|incoming) tray beside the printer\.',r'簽署後,請將紀錄放入打印機旁的(待發|來件)文件盤。',lambda m:m[1],lambda m:'outgoing' if m[1]=='待發' else 'incoming')
clause('card reference side',r'The reference is printed on the (back|front) of your card\.',r'編號印在卡的(背面|正面),',lambda m:m[1],lambda m:'back' if m[1]=='背面' else 'front')
fixed('reference spacing',r'Type it without spaces\.',r'輸入時請勿留空格。')
clause('access code delivery channel',r'The updated access code will be sent by (text message|email)\.',r'更新後的通行碼將以(短訊|電郵)發送,',lambda m:m[1],lambda m:'text message' if m[1]=='短訊' else 'email')
fixed('contact details current',r'Please keep your contact details current\.',r'請確保聯絡資料為最新。')

def extract_clauses(text,lang):
    text=normal(text)
    facts=defaultdict(list)
    spans=[]
    for key,ep,zp,ev,zv in CLAUSE_RULES:
        pattern,value=(ep,ev) if lang=='en' else (zp,zv)
        for match in pattern.finditer(text):
            # Only consume whole clause boundaries, including labelled list items.
            prefix=text[:match.start()].rstrip()
            if prefix and prefix[-1] not in '.。,;:!?\n' and not text[:match.start()].endswith('\n'):
                continue
            if any(match.start()<end and match.end()>start for start,end in spans):
                continue
            facts[key].append(dict(value=value(match),span=match[0]))
            spans.append(match.span())
    chars=list(text)
    for start,end in spans:
        chars[start:end]=' '* (end-start)
    remainder=''.join(chars)
    remainder=re.sub(r'(?m)^\s*[-─]+\s*$','',remainder)
    return facts,remainder.strip()

_v8_original_check=check_notice

def check_notice(chinese_text,english_text):
    z,zremain=extract_clauses(chinese_text,'zh')
    e,eremain=extract_clauses(english_text,'en')
    shared=set(z)&set(e)
    if not shared:
        return _v8_original_check(chinese_text,english_text)
    # Put unmatched or repeated facts back into residual text for contextual review.
    evidence=[]
    for key in sorted(set(z)|set(e)):
        if key not in shared or len(z[key])!=1 or len(e[key])!=1:
            zremain+='\n'+'\n'.join(x['span'] for x in z[key])
            eremain+='\n'+'\n'.join(x['span'] for x in e[key])
            continue
        if z[key][0]['value']!=e[key][0]['value']:
            evidence.append(dict(category=key,chinese_value=z[key][0]['value'],english_value=e[key][0]['value'],chinese_span=z[key][0]['span'],english_span=e[key][0]['span']))
    if zremain.strip() or eremain.strip():
        result=_v8_original_check(zremain,eremain)
        result['decision_path']='clause_facts_with_residual_review'
    else:
        result=pd.DataFrame([dict(status='✅ OK',chinese=chinese_text,english=english_text,why='',decision_path='clause_facts')])
    if evidence:
        reasons=[f"{x['category']} differs: English {x['english_value']} [{x['english_span']}]; Chinese {x['chinese_value']} [{x['chinese_span']}]" for x in evidence]
        result=pd.concat([result,pd.DataFrame([dict(status='⚠️ Check',chinese=chinese_text,english=english_text,why='; '.join(reasons),semantic_evidence=evidence,decision_path='clause_facts')])],ignore_index=True)
    return result
