"""pvoice: voice signal analysis for Parkinson's disease screening research.

This package contains the full pipeline for the graduation project:

- config:      all fixed settings (sample rate, pitch range, MFCC settings, paths)
- dataset:     finding audio files, reading labels and subject IDs (MDVR-KCL)
- preprocess:  loading and cleaning raw audio in a consistent way
- features:    acoustic feature extraction (F0, jitter, shimmer, HNR, MFCC)
- modeling:    classical machine learning models and training
- evaluate:    subject-independent (grouped) validation and metrics
- predict:     prediction for a single new audio file

Important: this is a research screening prototype. It does NOT diagnose
Parkinson's disease.
"""

__version__ = "0.1.0"
