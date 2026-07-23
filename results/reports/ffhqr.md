# FFHQR

## Evaluated scope

FFHQR contains 70,000 original/retouched pairs, or 140,000 class samples. The local archive contained the 10,000-pair ID slice 60000-69999. A balanced 20% of that slice was selected: 2,000 originals and 2,000 retouched images. Scoring succeeded for 3,991 images. The sample is 2.86% of the official class samples and has 99.78% score yield.

## Result

| Bona fide mean | Retouched mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.095 | 0.123 | 0.598 (0.579-0.615) | 0.429 (0.413-0.444) |

Professional portrait retouching causes little systematic score elevation, so most retouched samples remain close to the dataset's bona fide score distribution. The deviation score does not systematically distinguish this ordinary professional-retouching domain. This does not prove that an individual retouched image will score low or is bona fide.

[Histogram](../frozen/ffhqr/ffhqr_histogram.png) | [ROC](../frozen/ffhqr/ffhqr_roc.png) | [Metrics](../frozen/ffhqr/ffhqr_metrics.json)

Sanitized per-image score rows are published under the accompanying data notice; images are not published because complete source-image attribution was unavailable.
