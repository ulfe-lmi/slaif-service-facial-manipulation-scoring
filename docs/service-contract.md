# Service contract

## Output semantics

The service exposes the unchanged SelfMAD++ class-1 softmax output as an `uncalibrated_model_score`. Operationally, this is used as a bona fide deviation score: lower values indicate greater compatibility and higher values indicate lower compatibility with the fixed model's learned bona fide side of its decision boundary. The value is bounded to `[0, 1]` by softmax, but it is not a calibrated probability or a general geometric distance from all possible bona fide images.

The score has no universal decision boundary. Dataset ROC curves and distribution summaries characterize aggregate behavior only. They do not establish that a particular image is bona fide or manipulated.

## Intended use

The service is intended as a specialist bona fide compatibility signal that another system may inspect, combine, calibrate, or ignore. A user can score representative bona fide images from its own acquisition process, examine the empirical distribution, and independently define an operating policy.

This repository does not determine whether such a policy is suitable. A threshold chosen from a reference distribution describes that reference distribution; it does not by itself establish manipulation recall, future false-positive rates, fairness, or validity under domain shift.

## Out of scope

- hard authenticity or fraud decisions;
- determining that an individual image is bona fide or manipulated;
- identifying a manipulation type, method, or generator;
- identity matching or biometric verification;
- full identity-document authentication;
- document field, template, portrait-replacement, or security-feature analysis;
- guarantees for manipulation families or capture pipelines not represented in evaluation;
- probability calibration or a recommended threshold.

## Input domain

The input must contain at least one detectable face. The author preprocessing selects the largest detected face, computes a bounding box over 81 landmarks, expands that box by 12.5 percent, clips it to the image, and passes the resulting crop to the model's 512 by 512 evaluation transform. It does not perform FFHQ alignment, similarity warping, or morph-style geometric normalization.

An input with no detected face is `unscorable`; it is not assigned a low score. Multiple faces are not rejected, but only the largest detected face is scored.

## Versioning

Every result identifies the service version, SelfMAD++ source revision, checkpoint checksum, and preprocessing revision. Changing any of these produces a new model/preprocessing version. Scores from different versions must not be assumed interchangeable.
