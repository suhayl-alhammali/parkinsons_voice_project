# 12. Presentation guidance and expected questions

## 12.1 The four messages to land

1. **We built the measurement, not just the model.** Feature extraction
   from raw audio — 74 acoustic measurements grounded in speech
   physiology — is the core engineering contribution, not a downloaded
   feature table.
2. **We validated honestly.** No person appears in both training and
   testing, enforced by an assertion that halts the program. The same
   pipeline scores 0.909 under a deliberately leaky split versus 0.775
   under the correct one — a measured demonstration of why many published
   95%+ results are not trustworthy.
3. **We measured generalisation instead of assuming it.** Tested unadapted
   on a foreign dataset in another language: 0.701 AUC. Most undergraduate
   projects never attempt this.
4. **We built a system that admits uncertainty.** Scores near the boundary
   report "inconclusive". On the foreign dataset, 100% of elderly healthy
   speakers landed there — the system declined to mislabel them.

## 12.2 Suggested slide order

1. Motivation: Parkinson's, speech symptoms, why early screening matters
2. How the voice is produced and what the disease changes
3. Dataset: 37 subjects, 73 recordings, inspection findings
4. Pipeline diagram: audio → preprocessing → chunks → 74 features →
   model
5. The feature families, with the physiology behind each
6. **Validation: the leakage slide** (`validation_comparison.png`)
7. Results: the metrics table + ROC curve
8. Feature importance — what the model actually uses
9. The experiment study: 19 configurations and why we rejected the
   highest-scoring one
10. External validation: design, the bandwidth trap, results
    (`external_scores.png`)
11. The prototype: live demonstration
12. Limitations and ethics
13. Conclusion and future work

## 12.3 Demonstration advice

- **Safest demo:** a dataset recording via the command line or the app —
  in-domain, so the result is meaningful and fast to explain.
- **Most impressive demo:** record live with the microphone and let the
  system return *inconclusive* with condition warnings, then explain that
  this is the system working correctly, not failing. This turns the
  weakest technical point into evidence of scientific maturity.
- Prepare for the ~1 minute analysis time: start the recording analysis,
  then talk through the pipeline slide while it runs.
- Have screenshots ready in case the live demo misbehaves.

## 12.4 Expected questions and answers

**Q: Your accuracy is 82%, but published papers report 95–99% on this
dataset. Why is yours lower?**

Because those papers usually split the data at the recording or window
level, so the same person's voice appears in both training and testing.
We measured that effect directly: with a leaky chunk-level split our own
pipeline reports 0.909; with correct subject grouping it reports 0.775.
The difference is memorisation, not detection. Our number is lower because
it is honest.

**Q: Why didn't you use deep learning?**

Three reasons. First, 37 subjects is far too few to train a deep network
without severe overfitting. Second, the project requires explainability —
we can show that pitch range is the most important feature and connect it
to a known clinical sign, which a deep network would not provide. Third,
our own experiments showed that even a small neural network (MLP)
collapsed from 0.671 to 0.526 when we removed pitch features, revealing it
had been relying on a potential confound. Classical models were both more
accurate and more trustworthy here.

**Q: Why balanced accuracy instead of accuracy?**

Our data has 42 healthy and 31 patient recordings. A model that always
says "healthy" gets 57.5% accuracy while catching zero patients. Balanced
accuracy gives that model 50%, correctly exposing it as useless.

**Q: Your ensemble scored 0.840 — why did you use the 0.822 model?**

We fixed the rule before running the experiments: a more complex variant
must win by more than 0.02. The ensemble won by 0.018, which is smaller
than our seed-to-seed variation of about 0.03 — statistically it is a tie.
Choosing the most complex of several tied options means fitting the
validation procedure rather than the problem. We report the 0.840 openly;
we just did not let it drive the decision.

**Q: Can this diagnose Parkinson's disease?**

No, and it is not designed to. It reports whether a recording's acoustic
pattern resembles one dataset group or another. Many other conditions —
a cold, laryngitis, ageing, smoking — also change voice quality. Any
concern requires evaluation by a qualified clinician. That statement
appears before and after every result in the software.

**Q: What happens if I record myself right now?**

Most likely an "inconclusive" result, possibly with condition warnings.
That is correct behaviour: your microphone, room, and probably language
differ from the training data. We demonstrated exactly this on the Italian
dataset, where 100% of elderly healthy speakers fell in the inconclusive
band.

**Q: Isn't 37 subjects too few?**

Yes, and we say so in every report. It is the main limitation. We mitigate
it by reporting variation rather than single numbers, repeating validation
with three random seeds, using grouped validation so results are not
inflated, and testing externally on a second dataset of 61 speakers.

**Q: How do you know the model isn't just detecting male versus female
voices?**

We tested it. Absolute-pitch features are the ones most likely to encode
speaker sex, so we repeated the whole validation with them removed.
Performance held (0.768 → 0.780 for the selected model type), showing the
signal lives in the perturbation and spectral features. We report this
because the dataset ships no verified sex metadata, so we could not check
group composition directly.

**Q: What was the hardest technical problem?**

Detecting confounders that would have made results look better. The
clearest example: in the Italian dataset, every 44.1 kHz file belonged to
the Parkinson's group and every healthy file was 16 kHz — so a model could
have "detected Parkinson's" by detecting microphone bandwidth. We caught
it during inspection and downsampled everything to 16 kHz before
evaluating.

**Q: Why 10-second chunks?**

Long enough for stable acoustic measurements, short enough to produce
about 14 chunks per recording. Averaging many chunk measurements is more
stable than one measurement over a whole recording, and it improved
balanced accuracy from 0.780 to 0.822. Crucially, chunks inherit their
speaker's ID so grouped validation still holds — chunk-level splitting
without that grouping is exactly the leakage we demonstrated.

**Q: What would you do with more time?**

In order of expected value: collect or obtain more subjects, especially
with recording-condition diversity; add per-subject sex and age metadata
so confounding can be controlled rather than only bounded; test
longitudinally (comparing a person against their own earlier recordings,
which should be far more sensitive than comparing against a group); and
apply domain-adaptation techniques so the model transfers better across
microphones and languages.

**Q: Is the work reproducible?**

Yes. Every number in every report is regenerated by a script in the public
repository. The audio itself is not redistributed for licensing reasons,
but download instructions are included, and the pipeline configuration is
saved with the model so predictions can never silently use different
settings than training did.
