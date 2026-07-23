# PPR10K

## Evaluated scope

All 11,161 source portraits and three expert-retouched targets per source were attempted, for 44,644 class samples. Author cropping/scoring succeeded for 25,910: 6,400 source and 19,510 retouched images. The 58.04% yield is a material limitation; 18,734 rows had no crop accepted by the dlib/81-landmark author procedure.

## Result

| Bona fide mean | Retouched mean | AUC (95% CI) | EER (95% CI) |
| ---: | ---: | ---: | ---: |
| 0.235 | 0.216 | 0.467 (0.459-0.475) | 0.522 (0.515-0.529) |

PPR10K does not separate in the intended direction. Retouched images score slightly lower on average, meaning they are no less compatible with the model's learned bona fide side than the source portraits. Polarity was deliberately not reversed to improve the result. The data therefore provides no support for using this score to distinguish the evaluated expert aesthetic-retouching domain from its bona fide references.

[Histogram](../frozen/ppr10k/ppr10k_histogram.png) | [ROC](../frozen/ppr10k/ppr10k_roc.png) | [Metrics](../frozen/ppr10k/ppr10k_metrics.json)

PPR10K restricts image and derived-data use/reproduction. Only aggregate evidence is published.
