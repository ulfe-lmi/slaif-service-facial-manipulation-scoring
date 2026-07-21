# STR-FFHQ-FM

## Evaluated scope

All 3,310 locally available metadata rows were attempted against an expected 3,311 rows. Author cropping and scoring succeeded for 3,288 images: 1,682 bona fide and 1,606 manipulated. This is 99.31% of the expected dataset and 99.34% of attempted rows.

## Result

| Bona fide mean | Manipulated mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.102 | 0.687 | 0.900 (0.889-0.911) | 0.180 (0.165-0.193) |

Manipulated images generally score higher, with strong ranking separation and overlapping tails. This is one of the strongest evaluated domains and is reasonably close to the model's original morph/manipulation purpose.

[Histogram](../frozen/str_ffhq_fm/str_ffhq_fm_histogram.png) | [ROC](../frozen/str_ffhq_fm/str_ffhq_fm_roc.png) | [Metrics](../frozen/str_ffhq_fm/str_ffhq_fm_metrics.json)

The result characterizes this dataset only. It does not imply that a score is a manipulation probability or support the reported EER threshold as a deployment threshold.
