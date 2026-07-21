# CelebHQ-FM

## Evaluated scope

All 14,490 rows were attempted and 14,454 scored: 1,722 bona fide originals and 12,732 manipulated images. Coverage is 99.75%.

The bona fide definition is important. Original `_orig` images are used. `EDIT_NAME=none` output from the manipulation pipeline is not treated as an untouched original.

## Result

| Bona fide mean | Manipulated mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.435 | 0.920 | 0.944 (0.939-0.950) | 0.134 (0.124-0.141) |

CelebHQ-FM has the strongest ranking separation in this report. Its bona fide mean is nevertheless high, demonstrating why the raw value cannot be interpreted with a universal threshold or as a calibrated probability. The domain raises both classes while retaining strong relative separation.

[Histogram](../frozen/celebhq_fm/celebhq_fm_histogram.png) | [ROC](../frozen/celebhq_fm/celebhq_fm_roc.png) | [Metrics](../frozen/celebhq_fm/celebhq_fm_metrics.json)
