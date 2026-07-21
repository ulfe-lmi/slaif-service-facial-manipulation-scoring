# Frozen benchmark report

## Scope and method

These results were scored on 18-20 July 2026 and imported on 21 July 2026. Every image used the pinned SelfMAD++ author `crop.py` procedure: dlib frontal-face detection, the largest face by 81-landmark bounding-box area, a 12.5% margin, and the model's 512 by 512 resize. There was no FFHQ alignment, similarity warp, or morph-template normalization.

The score is the fixed SelfMAD++ class-1 softmax output: `0 = bona fide`, `1 = manipulated`. Polarity was never selected per dataset. No model inference was run while creating this report; plots and tables were regenerated from frozen score CSVs whose SHA-256 values are recorded in [`provenance/source_artifacts.csv`](provenance/source_artifacts.csv).

## Headline results

| Dataset | Bona fide n | Manipulated n | AUC (95% row-bootstrap CI) | EER (95% row-bootstrap CI) |
| --- | ---: | ---: | ---: | ---: |
| STR-FFHQ-FM | 1,682 | 1,606 | 0.900 (0.889-0.911) | 0.180 (0.165-0.193) |
| READFake | 716 | 1,419 | 0.688 (0.665-0.710) | 0.373 (0.348-0.395) |
| CelebHQ-FM | 1,722 | 12,732 | 0.944 (0.939-0.950) | 0.134 (0.124-0.141) |
| FFHQR | 1,994 | 1,997 | 0.598 (0.579-0.615) | 0.429 (0.413-0.444) |
| PPR10K | 6,400 | 19,510 | 0.467 (0.459-0.475) | 0.522 (0.515-0.529) |
| MFFI | 21,273 | 21,101 | 0.782 (0.778-0.787) | 0.287 (0.283-0.292) |
| RetouchingFFHQ | 34,064 | 49,939 | 0.686 (0.682-0.690) | 0.367 (0.363-0.370) |

AUC is the primary description for a score-only service. EER is included as a conventional research statistic; its labeled-test threshold is neither deployed nor recommended. Row-bootstrap intervals do not account for source-image or identity correlation.

## Class means

| Dataset | Bona fide mean | Manipulated/retouched mean | Interpretation |
| --- | ---: | ---: | --- |
| STR-FFHQ-FM | 0.102 | 0.687 | strong elevation, with overlapping tails |
| READFake | 0.200 | 0.475 | weak-to-moderate elevation |
| CelebHQ-FM | 0.435 | 0.920 | strong ranking despite high bona fide baseline |
| FFHQR | 0.095 | 0.123 | little systematic elevation |
| PPR10K | 0.235 | 0.216 | no separation in the intended direction |
| MFFI | 0.457 | 0.774 | useful cross-domain elevation with substantial overlap |
| RetouchingFFHQ | 0.094 | 0.167 | weak overall retouching elevation |
| FFHQ control | 0.095 | - | 69,098-image untouched reference only |

Machine-readable values are in [`headline_metrics.csv`](headline_metrics.csv) and [`category_means.csv`](category_means.csv).

## Retouching operations

Operation groups overlap because one image may contain several operations. Each operation uses matching, de-duplicated FFHQ originals as its bona fide comparison.

| Operation | Bona fide n/mean | Retouched n/mean | AUC | EER |
| --- | ---: | ---: | ---: | ---: |
| Eye enlarging | 19,786 / 0.094 | 22,670 / 0.179 | 0.706 | 0.352 |
| Face lifting | 19,559 / 0.093 | 22,669 / 0.165 | 0.682 | 0.370 |
| Smoothing | 19,636 / 0.094 | 22,710 / 0.232 | 0.809 | 0.261 |
| Whitening | 19,783 / 0.093 | 22,753 / 0.142 | 0.645 | 0.398 |

Smoothing is the retouching operation most strongly associated with elevated scores. Full provider, operation count, level, and 486 fine-grained combination rows are in [`frozen/retouchingffhq/categories`](frozen/retouchingffhq/categories/).

## Coverage

| Dataset | Selected/reference | Successfully scored/reference | Scored/selected |
| --- | ---: | ---: | ---: |
| STR-FFHQ-FM | 3,310/3,311 (99.97%) | 3,288/3,311 (99.31%) | 99.34% |
| READFake | 2,136/2,136 (100%) | 2,135/2,136 (99.95%) | 99.95% |
| CelebHQ-FM | 14,490/14,490 (100%) | 14,454/14,490 (99.75%) | 99.75% |
| FFHQR | 4,000/140,000 (2.86%) | 3,991/140,000 (2.85%) | 99.78% |
| PPR10K | 44,644/44,644 (100%) | 25,910/44,644 (58.04%) | 58.04% |
| MFFI | 42,688/1,024,000 (4.17%) | 42,374/1,024,000 (4.14%) | 99.26% |
| RetouchingFFHQ | 50,000/739,317 (6.76%) | 49,939/739,317 (6.75%) | 99.88% |
| FFHQ control | 69,343/70,000 (99.06%) | 69,098/70,000 (98.71%) | 99.65% |

Important denominator details:

- FFHQR sampled 20% of the locally available 10,000-pair ID slice, which is 2.86% of the official 70,000 pairs/140,000 class samples.
- MFFI selected exactly 5% of the 853,739-image local pool, class-balanced at 21,344 per class. The local pool is 83.37% of the paper's approximately 1.024 million images.
- RetouchingFFHQ had 739,317 manifest rows and 729,281 pairable rows. The sample is 6.86% of pairable rows. The paper reports 652,568 retouched images; the supplied archive/manifest count is larger and is therefore reported separately rather than reconciled silently.
- PPR10K's low score yield is due to 18,734 author-crop no-face failures, commonly on portraits for which dlib did not produce the required face/landmark crop.

Exact values and selection descriptions are in [`coverage.csv`](coverage.csv).

## Plots and reports

| Dataset | Histogram | ROC | Detailed report |
| --- | --- | --- | --- |
| STR-FFHQ-FM | [PNG](frozen/str_ffhq_fm/str_ffhq_fm_histogram.png) | [PNG](frozen/str_ffhq_fm/str_ffhq_fm_roc.png) | [Report](reports/str-ffhq-fm.md) |
| READFake | [PNG](frozen/readfake/readfake_histogram.png) | [PNG](frozen/readfake/readfake_roc.png) | [Report](reports/readfake.md) |
| CelebHQ-FM | [PNG](frozen/celebhq_fm/celebhq_fm_histogram.png) | [PNG](frozen/celebhq_fm/celebhq_fm_roc.png) | [Report](reports/celebhq-fm.md) |
| FFHQR | [PNG](frozen/ffhqr/ffhqr_histogram.png) | [PNG](frozen/ffhqr/ffhqr_roc.png) | [Report](reports/ffhqr.md) |
| PPR10K | [PNG](frozen/ppr10k/ppr10k_histogram.png) | [PNG](frozen/ppr10k/ppr10k_roc.png) | [Report](reports/ppr10k.md) |
| MFFI | [PNG](frozen/mffi/mffi_histogram.png) | [PNG](frozen/mffi/mffi_roc.png) | [Report](reports/mffi.md) |
| RetouchingFFHQ | [PNG](frozen/retouchingffhq/retouchingffhq_histogram.png) | [PNG](frozen/retouchingffhq/retouchingffhq_roc.png) | [Report](reports/retouchingffhq.md) |
| FFHQ control | [PNG](frozen/ffhq/ffhq_histogram.png) | not applicable | [Report](reports/ffhq.md) |

SVG versions, ECDF plots, histogram bins, and ROC points are beside each linked plot.

## Responsible conclusion

SelfMAD++ transfers beyond its original morph-detection purpose, especially on STR-FFHQ-FM, CelebHQ-FM, and MFFI. It is not a general edit detector: FFHQR and PPR10K show little or reversed separation for professional/aesthetic retouching, while RetouchingFFHQ varies markedly by operation. The evidence supports publishing a continuous manipulation-indication score with dataset-specific characterization. It does not support a universal threshold, automatic rejection, or an individual-image authenticity claim.

## Examples and data rights

Forty-six actual high/low scored crops were generated locally: four per two-class dataset, two FFHQ control tails, and twenty RetouchingFFHQ overall/per-operation examples. See [`examples/local_gallery_summary.csv`](examples/local_gallery_summary.csv) and [`examples/score_extremes.csv`](examples/score_extremes.csv).

The images are not committed because PPR10K restricts reproduction and derived data; READFake, STR, CelebHQ-FM, MFFI, and RetouchingFFHQ lack adequate public redistribution terms; and FFHQ/FFHQR candidates lack complete per-image attribution records. The checked-in gallery command can reproduce all examples locally. No absence is evidence that the example does not exist; it is a rights boundary.
