# MFFI

## Evaluated scope

The locally available pool contained 853,739 images, 83.37% of the paper's approximately 1.024 million samples. A uniformly random, class-balanced 5% sample of the local pool selected 21,344 images per class. Scoring succeeded for 42,374: 21,273 bona fide and 21,101 manipulated. This is 4.14% of the paper total and 99.26% of the selected sample.

## Result

| Bona fide mean | Manipulated mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.457 | 0.774 | 0.782 (0.778-0.787) | 0.287 (0.283-0.292) |

MFFI is the broadest and most difficult forgery domain in this report. A morph-oriented detector retains useful ranking information, but both classes contain many high scores and overlap heavily. This supports SelfMAD++ as an off-label specialist signal, not a general forgery verdict.

[Histogram](../frozen/mffi/mffi_histogram.png) | [ROC](../frozen/mffi/mffi_roc.png) | [Metrics](../frozen/mffi/mffi_metrics.json)

The frozen score manifest does not carry reliable per-forgery-method labels, so method-level results are not inferred from filenames. No identified score rows or images are published because MFFI has no explicit redistribution license in its public repository.
