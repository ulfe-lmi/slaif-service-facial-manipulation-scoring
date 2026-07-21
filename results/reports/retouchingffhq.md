# RetouchingFFHQ

## Evaluated scope

The supplied archive produced 739,317 retouched manifest rows, of which 729,281 could be paired with available FFHQ originals. A proportional stratified sample selected 50,000 retouched rows and 49,939 scored successfully. Overall metrics compare them with 34,064 unique matching FFHQ originals.

The paper reports 652,568 retouched images, which differs from the supplied archive manifest. Both denominators are disclosed; percentages use the archive actually evaluated.

## Overall result

| Bona fide mean | Retouched mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.094 | 0.167 | 0.686 (0.682-0.690) | 0.367 (0.363-0.370) |

[Histogram](../frozen/retouchingffhq/retouchingffhq_histogram.png) | [ROC](../frozen/retouchingffhq/retouchingffhq_roc.png) | [Metrics](../frozen/retouchingffhq/retouchingffhq_metrics.json)

## By operation

| Operation | Bona fide mean | Retouched mean | AUC | EER |
| --- | ---: | ---: | ---: | ---: |
| Eye enlarging | 0.094 | 0.179 | 0.706 | 0.352 |
| Face lifting | 0.093 | 0.165 | 0.682 | 0.370 |
| Smoothing | 0.094 | 0.232 | 0.809 | 0.261 |
| Whitening | 0.093 | 0.142 | 0.645 | 0.398 |

Smoothing is most strongly associated with elevated SelfMAD++ scores. Separation also increases with operation count: AUC is 0.641 for one operation, 0.692 for two, 0.756 for three, and 0.798 for four.

Operation groups overlap and are not independent. Full provider, level, operation-count, and fine-grained category tables are in [`categories`](../frozen/retouchingffhq/categories/).

No images or identified rows are published because the archive was supplied by the authors without public redistribution terms.
