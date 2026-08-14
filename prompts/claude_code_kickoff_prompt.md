# Kickoff prompt for Claude Code

You are Claude Code working on a biomedical engineering graduation project.

Project title:

**Voice Signal Analysis Using Machine Learning for Early Detection of Parkinson's Disease**

You are authorized to work autonomously in auto mode inside this project folder. Make normal technical implementation decisions yourself. Do not ask for approval for routine decisions such as file structure, helper scripts, exact implementation details, UI framework, plotting approach, refactoring, or dependency organization.

Stop only for vital issues: dataset ambiguity, labels or subject IDs unclear, subject independent validation risk, suspected data leakage, major dependency failure, need to change dataset, need to use pre extracted features, need to abandon raw audio processing, need to add live microphone recording as core scope, need to use deep learning as the primary method, suspiciously high results, or any serious scientific validity problem.

The student using this project is not fluent in English and is not strong with computers. Keep your instructions practical and clear.

## Fixed decisions

Use these as hard constraints:

1. Default dataset: MDVR KCL.
2. Use raw audio.
3. Do not use pre extracted features for the main implementation.
4. Feature extraction is a core project contribution.
5. Use a Python virtual environment only.
6. Do not install packages globally.
7. Work only inside the dedicated project folder.
8. Live microphone recording is deferred until good dataset based results are achieved.
9. The project is a non diagnostic screening prototype.
10. Use subject independent validation.
11. The same preprocessing and feature extraction pipeline must be used for training, evaluation, and new file prediction.

## Technical expectations

Build a Python project that can:

1. Inspect the MDVR KCL dataset.
2. Load raw audio.
3. Preprocess audio consistently.
4. Extract acoustic features.
5. Train classical machine learning models.
6. Evaluate models using subject independent validation.
7. Save model artifacts and reports.
8. Provide a simple file based prediction prototype.

Required feature families:

1. F0 statistics.
2. Jitter variants.
3. Shimmer variants.
4. Harmonic to noise ratio.
5. MFCC summary statistics.

Preferred libraries:

1. Parselmouth or Praat based methods for F0, jitter, shimmer, and HNR.
2. Librosa for MFCCs.
3. NumPy and SciPy for signal processing.
4. Pandas for tables.
5. Scikit learn for models.
6. Matplotlib for plots if needed.

Required models:

1. Logistic Regression baseline.
2. Support Vector Machine.
3. Random Forest.
4. Multilayer Perceptron, if reasonable.

Required metrics:

1. Accuracy.
2. Precision.
3. Recall.
4. F1 score.
5. Confusion matrix.

Use grouped validation by subject. Recordings from the same subject must never appear in both training and test sets. If subject IDs cannot be extracted reliably, stop and ask for review.

## First large task

Complete Phase 1.

Create the project foundation:

1. Inspect the current folder.
2. Create a clean Python project structure.
3. Create or update `CLAUDE.md` using the project rules above.
4. Create `README.md` with clear setup and project overview.
5. Create `requirements.txt` or another appropriate dependency file.
6. Create folders for data, models, reports, and source code.
7. Create initial source files for configuration, dataset inspection, preprocessing, feature extraction, training, evaluation, and prediction.
8. Add a dataset inspection script that will later inspect MDVR KCL once the dataset is placed in the correct folder.
9. Add clear comments and instructions for where the dataset should be placed.
10. Do not train a model yet unless a valid dataset is already present and clearly understood.

At the end of Phase 1, stop and give a concise summary for the student to paste into ChatGPT. Include:

1. What you completed.
2. Files created or changed.
3. Commands run.
4. Any assumptions.
5. Any errors.
6. Whether the project is ready for Phase 2.
7. The exact next action the student should take.
