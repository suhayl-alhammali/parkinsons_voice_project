# 9. Limitations and ethics

## 9.1 Why this document exists

A screening system that touches health decisions must be explicit about
what it cannot do. Everything below appears in the project's reports and
must appear in the final written report and the defence presentation.

## 9.2 Limitations of the data

1. **Very small sample.** 37 subjects (21 healthy, 16 patients). Each
   cross-validation fold tests only 7–8 people, so a single person's
   classification moves the score by several points. This is why every
   result is reported as mean ± standard deviation.
2. **One recording setup.** All training recordings come from one mobile
   device in one controlled environment. The model cannot distinguish
   "this voice is unhealthy" from "this recording is unfamiliar".
3. **One language.** English only. The external test showed the drop this
   causes.
4. **No demographic metadata.** The distributed audio carries no verified
   age or sex per subject. Since pitch strongly reflects sex, and
   Parkinson's is age-related, demographic confounding cannot be fully
   excluded — only bounded (the absolute-F0 ablation changed subject
   balanced accuracy by less than 0.02 for the selected model type).
5. **Class imbalance** (42 healthy vs 31 patient recordings), handled with
   balanced class weights and balanced accuracy, but still a limitation.
6. **No disease-severity information** used. A person with very early
   Parkinson's and one with advanced disease are treated as the same
   class, although their voices may differ greatly. The system's real
   sensitivity to *early* cases is therefore unmeasured — which matters,
   since early detection is the project's stated motivation.

## 9.3 Limitations of the method

1. **Perturbation features are used outside their classic setting.**
   Jitter, shimmer, and HNR were designed for sustained vowels. On
   continuous speech they are noisier proxies. CPPS and pause statistics
   partly compensate.
2. **Temporal detail is discarded.** Averaging features over chunks
   deliberately removes information about *when* things happen, in
   exchange for explainability and stability.
3. **Scores are not calibrated probabilities.** A score of 0.7 does not
   mean "70% chance of having Parkinson's". It is a model output, whose
   meaning depends entirely on the training distribution.
4. **Cross-sectional only.** The system compares a person against a group,
   never against their own earlier recordings. Tracking change over time
   would likely be far more sensitive, but requires longitudinal data.

## 9.4 Limitations of the evidence

1. **One external dataset.** 0.701 AUC on Italian data is one data point
   about generalisation, not a complete picture.
2. **Cross-validation measures the dataset, not any individual.** A
   balanced accuracy of 0.822 describes performance over this population;
   it says nothing reliable about a specific future user.
3. **The 0.02 adoption margin is a judgement call.** It was fixed in
   advance and applied consistently, but a different reasonable threshold
   would have selected the ensemble instead.

## 9.5 Ethical requirements followed

### Wording rules

**Always used:**
- "research screening-support prototype"
- "non-diagnostic indication"
- "Parkinson's-related voice changes"
- "the acoustic pattern was classified by the research model as closer to
  the PD / HC class"
- "requires evaluation by a qualified healthcare professional"

**Never used:**
- "diagnoses Parkinson's disease"
- "detects Parkinson's with certainty"
- "medical decision system"
- "clinically validated tool"
- any phrasing presenting the score as a person's medical risk or
  probability of disease

The mandatory disclaimer appears before and after every result in both
interfaces.

### Why the wording matters practically

Two concrete harms are being avoided:

- **False reassurance.** Someone with genuine symptoms who sees "HC" might
  delay seeing a doctor. Sensitivity is 0.771 internally — roughly 1 in 4
  patients is missed.
- **False alarm.** Someone healthy who sees "PD" may suffer real anxiety.
  Externally, roughly 4 in 10 healthy speakers were wrongly flagged.

The inconclusive band exists specifically to reduce both harms in
uncertain cases.

### Data handling

- The datasets are used under their licences for academic research.
- Recordings uploaded or recorded in the prototype are written to a
  temporary file and deleted immediately after processing; nothing is
  stored, transmitted, or logged.
- The audio datasets are excluded from the public GitHub repository; only
  code, reports, and download instructions are published.

## 9.6 Honest framing for the defence

The strongest and most defensible summary:

> This project does not claim to detect Parkinson's disease. It shows that
> measurable acoustic properties of speech differ between a group of
> Parkinson's patients and a group of healthy controls, that a classical
> machine learning model can exploit those differences with about 82%
> balanced accuracy on unseen *people* from the same dataset, that roughly
> 70% ranking ability survives transfer to a completely different dataset
> and language, and that a responsible prototype should report uncertainty
> rather than a confident label when the input falls outside its
> experience.
