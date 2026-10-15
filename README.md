# OMT II – Trigger Point Muscle Quiz
Mobile MCQ quiz (origins, insertions, actions) for the 52 muscles in the OMT II trigger-point course PDF (Catalyst University slides), cross-checked with Kenhub/TeachMeAnatomy.

**Add muscles:** add an entry to `muscles.json` (`id`, `name`, `region`, `origin`, `insertion`, `action`, optional `x` = ids of muscles too similar to use as distractors), then run `python3 build.py`. That regenerates `questions.json` and the embedded JSON block in `index.html`. Edit `template.html` for UI changes.
