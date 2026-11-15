# Warning audit

An independent agent reviewed all 150 issue-labelled cases in the first full Colab output against the bilingual source text, including the evidence values, not just the detector labels.

- 84 notices had an explicit relationship or contextual value difference.
- 21 had correct complete deadline dates.
- 45 had correct differing numeric values.
- None relied only on a generic warning, identified only a wrong issue, or lacked a warning.

The review found six unsupported secondary subject-name alarms. The final adapter no longer emits isolated-subject alarms when explicit discrepancy evidence exists. It also changes the inherited misleading “application deadline” wording to the neutral “deadline” label, retaining the correct date values.

The final export is checked to ensure every substantive issue warning from the reviewed run is retained, with these explanation corrections, and no “Notice subject needs review” alarm remains. The score comparison uses the earlier reviewed V7 warning ratings only when the fallback warning is unchanged except for the deadline label.

63 generic contradiction messages accompanied correct numeric differences in the reviewed run; they were not the sole basis for any detection. They remain auxiliary messages in the inherited fallback.

F275 uses awkward source wording “上午12時.” The canonical clock conversion follows the inherited AM convention, while the underlying numeric disagreement (12 versus 9) is valid independently of that boundary interpretation. The warning retains the source wording for inspection.

F048 and F075 include extra month changes introduced by the original dataset generator. Their specific correction warnings describe those actual text differences; the approved CSV was not changed.

This is an AI-assisted warning review, not bilingual human adjudication or an independent held-out benchmark.
