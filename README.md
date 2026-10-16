# Physio Year 2 – Study Quizzes
Mobile MCQ quiz site for Nóra's Year 2 physiotherapy classes. Live: https://sanz1987.github.io/omt-trigger-point-quiz/

Classes (home menu → class): each has 20 random questions per session, a topic filter, and a per-class "Review mistakes" list (stored in the browser).
- **OMT II · Trigger point muscles**: generated from `muscles.json` (origins, insertions, actions, nerves), checked against the Catalyst University slides (page numbers given in explanations).
- **OMT II · Techniques**, **Pathology of Trauma**, **Biomechanics**, **Research Methodology**, **Pathophysiological Foundations I**: hand-written banks in `classes/*.txt`, based on the course PDFs.

## Editing
- Question format in `classes/<id>.txt`: `@ Topic`, then blocks of `question` / `* correct` / `- wrong` (x3) / `E: explanation (source)`, separated by blank lines.
- Run `python3 build.py`. It validates the banks, then writes `questions.json` and embeds them in `index.html`. The UI is in `template.html`.

## Images
`img/` holds resized free-licence images from Wikimedia Commons (public-domain Gray's Anatomy plates plus CC BY-SA works). Author, licence and source for each image are in `img/attribution.json`, and they're shown on the in-app credits page. No Netter or Kenhub images.
