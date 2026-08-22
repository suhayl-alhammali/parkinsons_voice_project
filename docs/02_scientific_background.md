# 2. Scientific background

This document explains, from first principles, why a voice recording can
carry information about Parkinson's disease, and what each family of
measurements in this project actually measures.

## 2.1 How the human voice is produced

Speaking uses three stages:

1. **The power source — the lungs.** Air is pushed up out of the lungs
   through the windpipe. This airflow is the energy that becomes sound.
2. **The vibrator — the vocal folds (larynx).** Two small muscular folds
   sit across the airway. When brought together, escaping air forces them
   open and elastic recoil snaps them shut, hundreds of times per second.
   Each open-close cycle releases a puff of air; the stream of puffs is
   the raw buzzing sound of the voice.
3. **The filter — the vocal tract.** The throat, mouth, tongue, and lips
   form a resonating tube. Moving them emphasises some frequencies and
   suppresses others, turning the buzz into vowels and consonants.

Two consequences matter for this project:

- **The rate of vocal-fold vibration is the pitch** (fundamental
  frequency, `F0`). Roughly 85–180 Hz for adult men, 165–255 Hz for adult
  women — which is why pitch partly encodes speaker sex, a confound we
  had to check.
- **The regularity of the vibration determines voice quality.** Healthy
  vibration is highly periodic: each cycle nearly identical to the last.

## 2.2 What Parkinson's disease does to the voice

Parkinson's disease reduces dopamine in brain regions that control
movement. The classic symptoms — tremor, rigidity, slowness (bradykinesia),
reduced movement amplitude (hypokinesia) — apply to *every* muscle,
including the small muscles that control the vocal folds, tongue, lips,
and breathing.

The resulting speech disorder is called **hypokinetic dysarthria**, and it
appears in ways we can measure:

| Clinical sign | Physical cause | Measurable effect |
|---|---|---|
| Reduced loudness, monotone speech | Reduced movement amplitude; weaker breath support | Lower variation in pitch and amplitude |
| Breathy or hoarse voice | Vocal folds close incompletely, letting air leak through | More noise relative to tone (lower HNR, lower CPPS) |
| Unstable voice | Tremor and irregular muscle control | More cycle-to-cycle irregularity (higher jitter and shimmer) |
| Imprecise consonants | Slower, smaller tongue and lip movements | Different and slower-changing spectral shape (MFCC, delta-MFCC) |
| Hesitations, inappropriate pauses | Difficulty initiating and sustaining movement | More and longer pauses |

Crucially, these changes often appear **early** — sometimes before motor
symptoms are obvious enough to prompt a clinical visit. That is the entire
motivation for voice-based screening research: a microphone is cheap,
non-invasive, and could in principle flag people who should see a
neurologist.

> **What this project does NOT claim:** that these measurements diagnose
> Parkinson's disease. Many other conditions (a cold, laryngitis, ageing,
> smoking, fatigue) also change voice quality. The system reports
> *similarity to a dataset group*, nothing more.

## 2.3 The measurement families and why each is used

### Fundamental frequency statistics (F0) — 7 features

`F0` is how many times per second the vocal folds vibrate. We track it
across the recording and summarise it: mean, median, standard deviation,
minimum, maximum, range, and the fraction of time voicing was detected
at all.

**Why it matters:** monotone speech is a hallmark of Parkinson's, so the
*variation* of pitch (standard deviation, range) is more clinically
meaningful than its absolute value. Absolute pitch mostly encodes speaker
sex, which is why we deliberately tested whether the model depended on it.

### Jitter — 4 features

Jitter measures **irregularity in the timing** of vocal-fold cycles. If
one cycle lasts 5.0 milliseconds and the next 5.4 milliseconds, that
difference is jitter. It is expressed as a fraction (a percentage) so it
does not depend on the speaker's pitch.

The four variants differ in how they average across neighbouring cycles:
`local` (cycle to cycle), `local absolute` (in seconds rather than a
ratio), `RAP` (average over 3 cycles), `PPQ5` (average over 5 cycles).
The multi-cycle variants are less sensitive to short random fluctuations.

**Why it matters:** unstable neuromuscular control produces less regular
vibration timing. Healthy sustained voice is typically under about 1%
jitter.

### Shimmer — 5 features

Shimmer is the same idea applied to **amplitude** instead of timing: how
much the loudness of each vibration cycle differs from the next. Variants:
`local`, `local dB`, `APQ3`, `APQ5`, `APQ11` (averaged over 3, 5, or 11
neighbouring cycles).

**Why it matters:** weak or inconsistent vocal-fold closure produces
uneven puff strength, heard as a rough or unsteady voice.

### Harmonics-to-Noise Ratio (HNR) — 1 feature

Voice is a mixture of an ordered, periodic component (the harmonics) and
a disordered, noise-like component (turbulent air). HNR is their ratio in
decibels. A clean voice might reach 20 dB or more; a breathy voice, much
less.

**Why it matters:** incomplete vocal-fold closure lets air escape as
turbulent noise — the physical basis of a breathy voice.

### Cepstral Peak Prominence, smoothed (CPPS) — 1 feature

This is the most technically advanced measure in the project, and the one
best suited to *continuous speech*.

Intuition: a cepstrum is what you get by analysing the spectrum of a
spectrum. When a voice is strongly periodic, its spectrum contains evenly
spaced harmonic peaks, and that regular spacing itself produces a sharp
peak in the cepstrum. **CPPS measures how far that peak stands above the
surrounding background.** A strong, clear voice gives a prominent peak; a
breathy or noisy voice gives a weak one.

**Why it matters:** unlike jitter and shimmer, CPPS does not require the
algorithm to identify individual vibration cycles reliably — which is
exactly what fails on running speech. It is widely regarded in the
clinical literature as the most robust acoustic marker of breathiness and
overall dysphonia.

### Pause and timing statistics — 4 features

Using energy-based detection, the recording is divided into speech
stretches and silences. Gaps of at least 0.2 seconds count as pauses. We
compute: pauses per minute, mean pause duration, the fraction of the
recording spent pausing, and the mean length of continuous speech
stretches.

**Why it matters:** difficulty initiating and sustaining movement produces
more hesitations and a more fragmented speech rhythm. These features have
a useful bonus property: they depend on *timing*, not on frequency
content, so they are relatively robust to changes of microphone.

### MFCC and delta-MFCC — 52 features

**MFCC** (Mel-Frequency Cepstral Coefficients) compactly describe the
*shape of the spectrum* — essentially the filtering effect of the vocal
tract, on a frequency scale that mimics human hearing. We keep 13
coefficients and summarise each one's mean and standard deviation across
the recording (26 numbers).

**Delta-MFCC** describes how fast each coefficient *changes* from moment
to moment — the dynamics of articulation — again summarised as mean and
standard deviation (26 numbers).

**Why it matters:** imprecise, slowed articulation changes both the
average spectral shape and the speed of spectral movement. The standard
deviations proved especially informative in our final model.

**Caveat:** MFCCs are sensitive to microphone, room, and language, which
is a major reason performance dropped on the Italian dataset.

## 2.4 An important honest limitation

Jitter, shimmer, and HNR were originally defined for **sustained vowels**
(saying "aaaaah" steadily for several seconds), where every cycle should
be identical and any irregularity is meaningful. Our dataset contains
**continuous speech** (reading and conversation), where pitch and loudness
change constantly for perfectly normal linguistic reasons.

This makes these three measures noisier and less clinically pure than in
a classic voice-clinic protocol. It is why CPPS, pause statistics, and
the spectral features were added — they are designed for, or tolerant of,
running speech. This limitation is stated in every report.
