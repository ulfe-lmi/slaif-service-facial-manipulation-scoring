# READFake

## Evaluated scope

All 2,136 annotated archive rows were attempted. Scoring succeeded for 2,135 images: 716 bona fide and 1,419 manipulated. One row failed author cropping, giving 99.95% score coverage.

## Result

| Bona fide mean | Manipulated mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.200 | 0.475 | 0.688 (0.665-0.710) | 0.373 (0.348-0.395) |

The model provides weak-to-moderate ranking information, but the distributions overlap substantially. READFake supports only a narrow conclusion that the score can be additive in this domain; it is not a reliable independent decision signal.

[Histogram](../frozen/readfake/readfake_histogram.png) | [ROC](../frozen/readfake/readfake_roc.png) | [Metrics](../frozen/readfake/readfake_metrics.json)

The archive did not contain clear redistribution terms, so no identified rows or example images are published.
