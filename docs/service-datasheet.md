# Service datasheet

## Service identity

- **Name:** SLAIF Bona Fide Compatibility Scoring for Facial Images
- **Initial model:** SelfMAD++ trained on SMDD
- **Output:** continuous, uncalibrated class-1 softmax score in `[0, 1]`
- **Direction:** higher means lower bona fide compatibility
- **Decision:** none
- **Preprocessing:** pinned SelfMAD++ author crop, largest detected face, 81 landmarks, 12.5% landmark-box margin, then 512 by 512 resize

## Intended interpretation

The unchanged SelfMAD++ output is used as a bona fide deviation score. Lower values indicate greater compatibility and higher values indicate lower compatibility with the model's learned bona fide side of its decision boundary. It is not a probability, authenticity finding, identity-verification result, manipulation-type classification, or recommended decision threshold.

A user may characterize the score distribution on representative bona fide images from its own acquisition process and define an external policy. That empirical exercise does not establish attack recall or guarantee future false-positive rates.

An AUC describes ranking on one labeled dataset. For example, AUC 0.900 means that a randomly chosen manipulated sample ranked above a randomly chosen bona fide sample about 90% of the time in that dataset. It does not mean that an image with score 0.900 has a 90% probability of being manipulated.

EER is reported for comparison with detector literature. Its threshold is selected from the labeled test distribution and is not used by the service.

## Supported input

- JPEG, PNG, or WebP containing at least one detectable face;
- maximum upload and decoded-pixel limits controlled by deployment settings;
- largest face selected when more than one face is detected;
- `unscorable` result when no face is detected.

The service does not geometrically align or warp a face to an FFHQ/morph template. It performs the bounding-box crop published by the SelfMAD++ authors.

## Evaluation evidence

The [frozen benchmark report](../results/README.md) uses face manipulation, face forgery, portrait retouching, and an untouched FFHQ control to characterize where different image classes fall relative to their bona fide score distributions. It publishes exact selection/scoring coverage, 1,000-resample row-bootstrap intervals, normalized score distributions, ROC points, and per-operation RetouchingFFHQ results.

The confidence intervals characterize row resampling only. Related derivatives of one source image are correlated, so these intervals can be narrower than an identity- or source-cluster bootstrap. Results are not estimates for an unspecified deployment population.

## Principal limitations

- The initial SelfMAD++ backend was designed for single-image morphing attack detection; this is model provenance, not the service's claimed task.
- Scores shift substantially by dataset and capture pipeline; a universal threshold is not supported.
- Some untouched domains receive high scores, notably the CelebHQ-FM and MFFI bona fide groups.
- FFHQR and PPR10K show that common portrait retouching may not elevate scores.
- A low score does not establish that an image is bona fide, and a high score does not identify how an image was produced.
- Print/scan, screenshot, document capture, glare, compression, recapture, and camera effects need channel-specific evaluation.
- No claim is made about demographic parity, identity-level independence, or unseen manipulation generators.
- No document text, template, portrait replacement, liveness, or identity matching is performed.

## Data and privacy

The reference API is stateless and need not retain images. It supports an optional API key for the scoring endpoint; operators remain responsible for enabling and distributing that key, TLS, broader access control, logging, retention, and legal basis. Uploaded image bytes and API keys must not be written to application logs.

Datasets, score-row derivatives, and example images have separate terms. The repository contains no benchmark images. Full identified score rows are published only for FFHQ and FFHQR under explicit data notices; restricted or unclear datasets receive aggregate evidence only.

## Change control

Changing the SelfMAD++ commit, checkpoint, landmark model, crop behavior, decoder, resize transform, or score direction creates a new scoring version and requires fresh validation. Every response includes model and preprocessing identities.
