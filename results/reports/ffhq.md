# FFHQ untouched control

## Evaluated scope

FFHQ officially contains 70,000 images. The available archive contained 69,343; author cropping and scoring succeeded for 69,098. This is 98.71% of the official dataset and 99.65% of attempted local images.

## Score distribution

| Mean | Median | 95th percentile | 99th percentile | Fraction at or above 0.5 |
| ---: | ---: | ---: | ---: | ---: |
| 0.095 | 0.074 | 0.212 | 0.473 | 0.887% |

This one-class control provides a broad untouched FFHQ reference, not a manipulation benchmark; AUC and EER do not apply. It demonstrates that author cropping alone does not generally elevate standard FFHQ portraits into a high-score regime, while a small high-score tail remains.

[Histogram](../frozen/ffhq/ffhq_histogram.png) | [ECDF](../frozen/ffhq/ffhq_ecdf.png) | [Metrics](../frozen/ffhq/ffhq_metrics.json)

Sanitized score rows are published under the accompanying data notice. Images are not published because the exact tail candidates lacked complete individual Flickr attribution records.
