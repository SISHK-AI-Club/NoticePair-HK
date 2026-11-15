from IPython.display import HTML, display
summary_rows=[]
for tier in ['routine','difficult','edge']:
    a,b=by_tier['frozen'][tier],by_tier['candidate'][tier]
    n=sum(a.values()); positives=a['TP']+a['FN']
    summary_rows.append({'Difficulty':tier.title(),'Cases':n,
       'Accuracy: V8 → V9':f"{(a['TP']+a['TN'])/n:.1%} → {(b['TP']+b['TN'])/n:.1%}",
       'Errors caught: V8 → V9':f"{a['TP']}/{positives} → {b['TP']}/{positives}",
       'Missed: V8 → V9':f"{a['FN']} → {b['FN']}",
       'False alarms: V8 → V9':f"{a['FP']} → {b['FP']}"})
a,b=counts['frozen'],counts['candidate']
display(HTML('<h2>V9 versus frozen V8 — 1000-case comparison</h2>'
    '<p><strong>Development results: these 1000 cases informed V9. This is not a new held-out score.</strong></p>'
    +pd.DataFrame(summary_rows).to_html(index=False)
    +f"<p>Overall accuracy: <strong>{(a['TP']+a['TN'])/1000:.1%} → {(b['TP']+b['TN'])/1000:.1%}</strong>. "
    +f"Errors caught: {a['TP']}/300 → {b['TP']}/300. False alarms: {a['FP']}/700 → {b['FP']}/700.</p>"
    +'<p>Both versions ran fresh using the same model objects, original thresholds, and checksum-verified CSV. Original model weights were not fine-tuned.</p>'
    +'<p>To check another notice, call <code>candidate["check_notice"](chinese_text, english_text)</code>.</p>'))
