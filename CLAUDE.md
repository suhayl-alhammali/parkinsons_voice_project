# CLAUDE.md

## Project mission

Build a graduation project prototype titled:

**Voice Signal Analysis Using Machine Learning for Early Detection of Parkinson's Disease**

The system must analyze raw voice recordings, extract acoustic features, train machine learning classifiers, evaluate them using subject independent validation, and provide a simple prototype for file based prediction.

This is a biomedical engineering graduation project. The goal is a clear, reproducible, explainable research prototype, not a production medical device.

## Operating mode

You are Claude Code running with high autonomy.

You may make normal technical implementation decisions independently. Do not ask for approval for routine implementation choices.

You should work in large phase sized chunks, not tiny step by step increments.

After each major phase, stop and provide a concise summary for the student to paste into ChatGPT. The summary must include:

1. What was completed.
2. Files created or changed.
3. Commands that were run.
4. Results or errors.
5. Any decisions you made.
6. Any risks or open questions.
7. Whether the next phase can proceed.

## Fixed project decisions

These decisions are already approved and must be treated as project constraints:

1. Default dataset: MDVR KCL.
2. Main data type: raw audio.
3. Pre extracted feature datasets are not allowed for the main implementation.
4. Feature extraction is a core contribution of the project.
5. Live microphone recording is deferred until good dataset based results are achieved.
6. Use Python.
7. Use a project virtual environment only.
8. Do not install Python packages globally.
9. Work only inside the dedicated project folder.
10. UI framework is your decision.
11. The project output is a non diagnostic screening prototype.
12. The project must be explainable and suitable for a biomedical engineering graduation project.

## Autonomy rules

You may decide independently:

1. Repository and file structure.
2. Python module structure.
3. Streamlit, CLI, or another simple prototype approach.
4. Exact preprocessing implementation details.
5. Exact feature extraction implementation details.
6. Model code organization.
7. Plotting and report generation.
8. Helper scripts.
9. Tests.
10. Refactoring.
11. Error handling.
12. Dependency versions, unless installation fails or creates serious conflicts.
13. Hyperparameter search strategy, provided it remains explainable and computationally reasonable.

Do not ask for approval on these unless there is a serious risk.

## Decisions requiring ChatGPT review

Stop and ask for ChatGPT review if any of the following occur:

1. The MDVR KCL dataset structure is unclear.
2. Labels are unclear.
3. Subject IDs are missing, ambiguous, or difficult to extract.
4. Grouped subject independent validation may not be possible.
5. You suspect data leakage.
6. Model accuracy is suspiciously high, especially 95 percent or higher.
7. Dependency installation fails in a way that affects the project architecture.
8. The implementation cannot run reasonably on a normal student laptop.
9. You need to materially change the project architecture.
10. You want to add live microphone recording.
11. You want to use deep learning as the main approach.
12. You believe the project should use a different dataset.
13. You believe raw audio processing is not feasible.
14. You believe pre extracted features are needed.
15. You find a serious scientific validity problem.

## Decisions requiring Hussein

ChatGPT may escalate some issues to Hussein. However, you should explicitly flag these as high level issues when they appear.

Hussein must be consulted for:

1. Changing the dataset away from MDVR KCL.
2. Switching from raw audio to pre extracted features.
3. Abandoning custom feature extraction.
4. Making live microphone recording part of the core scope.
5. Using deep learning as the primary project method.
6. Proceeding when subject independent validation is impossible.
7. Proceeding when labels or subject IDs are unreliable.
8. Reframing the project medically or clinically.
9. Accepting suspiciously high results without investigation.
10. Any supervisor requested change that affects scope, dataset, validation, or claims.

## Scientific constraints

These rules are mandatory.

### Dataset

Use MDVR KCL as the default dataset.

First inspect the dataset before training anything.

Create a dataset inspection report that includes:

1. Folder structure.
2. Number of audio files.
3. Audio formats.
4. Sampling rates.
5. Durations.
6. Class labels.
7. Subject identifiers.
8. Number of subjects per class.
9. Number of recordings per subject.
10. Missing, corrupt, very short, silent, or suspicious files.
11. How labels and subject groups are inferred.
12. Risks in the dataset.

Do not begin serious modeling until the dataset structure, labels, and subject grouping are understood.

### Raw audio requirement

The main pipeline must start from raw audio files.

Do not use pre extracted feature datasets for the main implementation.

Feature extraction must be implemented as part of this project.

### Same pipeline rule

The same preprocessing and feature extraction pipeline must be used for:

1. Training data.
2. Evaluation data.
3. New audio file prediction.

Do not train on features produced one way and predict on features produced another way.

### Preprocessing

Build a consistent audio preprocessing pipeline.

Required concepts:

1. Convert to mono.
2. Use a fixed sample rate.
3. Remove DC offset.
4. Normalize amplitude.
5. Trim silence or unstable regions where appropriate.
6. Keep perturbation sensitive features protected from aggressive filtering.
7. Use separate conditioning for perturbation and cepstral features if needed.

Avoid heavy denoising unless you verify it does not damage jitter, shimmer, F0, or HNR.

### Feature extraction

Use a clear, documented feature vector.

Required feature families:

1. F0 statistics.
2. Jitter variants.
3. Shimmer variants.
4. Harmonic to noise ratio.
5. MFCC summary statistics.

Preferred tools:

1. Parselmouth or Praat based logic for F0, jitter, shimmer, and HNR.
2. Librosa for MFCCs.
3. NumPy and SciPy for general signal processing.
4. Pandas for feature tables.
5. Scikit learn for machine learning.

Optional features may be added if they do not destabilize the project:

1. Delta MFCC.
2. Delta delta MFCC.
3. Additional dysphonia or nonlinear measures.

Do not let optional features delay the MVP.

### Modeling

Use explainable classical machine learning first.

Required models:

1. Logistic Regression baseline.
2. Support Vector Machine.
3. Random Forest.
4. Multilayer Perceptron, if reasonable.

You may add other classical models if useful, but do not make the project dependent on them.

Use feature scaling where appropriate.

Save trained model artifacts and preprocessing configuration.

### Validation

Validation must be subject independent.

Recordings from the same subject must never appear in both training and test sets.

Use grouped validation, such as:

1. GroupKFold.
2. Stratified group split if available and appropriate.
3. GroupShuffleSplit for train/test split if needed.

If reliable subject IDs cannot be extracted, stop and ask for review.

Never use random recording level splits when multiple recordings per subject exist.

### Metrics

Report at least:

1. Accuracy.
2. Precision.
3. Recall.
4. F1 score.
5. Confusion matrix.

Where possible, include:

1. ROC AUC.
2. Class distribution.
3. Per fold results.
4. Mean and standard deviation across folds.

Clearly explain that high performance on small controlled datasets may not generalize.

### Prototype

Build a file based prototype first.

The prototype should allow the user to select or upload an audio file, run the same preprocessing and feature extraction pipeline, load the trained model, and display a non diagnostic screening output.

The prediction must use cautious language, such as:

"This result is a research screening indication only. It is not a medical diagnosis."

Do not add live microphone recording until dataset based results are good and Hussein approves.

## Project phases

Work in these large phases.

### Phase 1: Project initialization

Create the project structure, environment files, README draft, and initial scripts.

Expected outputs:

1. Repository structure.
2. requirements.txt or pyproject.toml.
3. Setup instructions.
4. Initial README.
5. Dataset folder convention.
6. A script or notebook for dataset inspection.

Stop after this phase and summarize.

### Phase 2: Dataset inspection

Inspect MDVR KCL after the student places it in the expected data folder.

Expected outputs:

1. dataset_report.md.
2. Dataset metadata table if possible.
3. Audio duration and sampling rate summary.
4. Label extraction method.
5. Subject grouping method.
6. Risk notes.

Stop after this phase and summarize.

### Phase 3: Preprocessing and feature extraction

Build and test the raw audio processing pipeline.

Expected outputs:

1. Reusable preprocessing code.
2. Feature extraction code.
3. Feature configuration.
4. Feature table generation script.
5. Basic tests or validation checks.
6. Feature table saved to disk.

Stop after this phase and summarize.

### Phase 4: Modeling and evaluation

Train and evaluate classical machine learning models with subject independent validation.

Expected outputs:

1. Training script.
2. Evaluation script.
3. Metrics report.
4. Confusion matrix.
5. Saved model.
6. Notes about leakage risk and limitations.

Stop after this phase and summarize.

### Phase 5: File based prototype

Build a simple prototype for prediction from an audio file.

Expected outputs:

1. App or CLI.
2. Prediction pipeline.
3. Model loading.
4. Cautious display wording.
5. Instructions for running the prototype.

Stop after this phase and summarize.

### Phase 6: Documentation and final polish

Prepare the project for demonstration and supervisor review.

Expected outputs:

1. Clean README.
2. Reproducibility instructions.
3. Explanation of methodology.
4. Limitations.
5. Screenshots if applicable.
6. Final project report support files if requested.

Stop after this phase and summarize.

## Environment rules

Use a virtual environment only.

Recommended commands:

```bash
python -m venv .venv
```

Windows activation:

```bash
.venv\Scripts\activate
```

macOS or Linux activation:

```bash
source .venv/bin/activate
```

Install dependencies only while the virtual environment is active.

Do not use global pip installs.

Do not modify unrelated folders.

Do not delete user files outside the project folder.

## Coding standards

Write maintainable Python code.

Prefer clear, simple, well documented code over clever code.

Use configuration files or constants for:

1. Sample rate.
2. Pitch floor and ceiling.
3. MFCC settings.
4. Dataset paths.
5. Model settings.
6. Output paths.

Use functions and modules that can be reused by training, evaluation, and prediction.

Avoid duplicating pipeline logic.

Include error messages that a non expert can understand.

## Documentation standards

The student is not fluent in English and is not comfortable with computers.

Write technical documentation in clear English, but avoid unnecessary complexity.

For every command the student must run, provide:

1. Where to run it.
2. The exact command.
3. What successful output should look like.
4. What to copy into ChatGPT if it fails.

## Medical and ethical wording

Never claim the system diagnoses Parkinson's disease.

Use terms such as:

1. Screening prototype.
2. Parkinson's related voice changes.
3. Non diagnostic indication.
4. Research demonstration.
5. Requires clinical evaluation.

Avoid terms such as:

1. Diagnoses Parkinson's.
2. Detects Parkinson's with certainty.
3. Medical decision system.
4. Clinically validated tool.

## Final reminder

Autonomy is encouraged. Scientific validity is mandatory.

When in doubt about code, make a reasonable technical decision and continue.

When in doubt about dataset validity, subject grouping, clinical claims, or scope, stop and ask for review.
