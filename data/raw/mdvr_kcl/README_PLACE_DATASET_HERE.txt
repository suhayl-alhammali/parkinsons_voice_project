Place the extracted MDVR-KCL dataset in THIS folder.

MDVR-KCL = Mobile Device Voice Recordings at King's College London
(voice recordings of people with Parkinson's disease and healthy controls).

Download: https://zenodo.org/record/2867216

After extracting the downloaded archive, this folder should contain:

    data/raw/mdvr_kcl/
        ReadText/
            HC/   ID00_hc_0_0_0.wav  (and more .wav files)
            PD/   ID02_pd_2_1_1.wav  (and more .wav files)
        SpontaneousDialogue/
            HC/   ...
            PD/   ...

Then run (from the project folder, with .venv active):

    python scripts/inspect_dataset.py

Note: the audio files are NOT stored in the git repository (they are large
and the dataset has its own license). Only this instruction file is kept.
