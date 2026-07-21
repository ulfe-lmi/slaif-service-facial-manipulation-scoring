# Evaluated datasets

No dataset or benchmark image is distributed by this repository. Obtain data from its owner and review the applicable terms before running an adapter.

| Dataset | Domain | Primary source | Public evidence policy |
| --- | --- | --- | --- |
| STR-FFHQ-FM | portrait face manipulation | [STR Face Manipulation Datasets](https://stresearch.github.io/face-manipulation-datasets/) | aggregate results only; no explicit reusable image/data license was identified |
| READFake | mixed real and manipulated facial images | dataset archive supplied for the published benchmark | aggregate results only; redistribution terms were not present in the archive |
| CelebHQ-FM | portrait face manipulation | [STR Face Manipulation Datasets](https://stresearch.github.io/face-manipulation-datasets/) | aggregate results only; source-image terms also apply |
| FFHQR | professional portrait retouching | [Official repository](https://github.com/skylab-tech/ffhqr-dataset) | CC BY-NC-SA 4.0 plus source-image attribution and license terms |
| PPR10K | expert portrait retouching | [Official repository](https://github.com/csjliang/PPR10K) | aggregate results only; images and derived data are restricted to non-commercial research and reproduction is restricted |
| MFFI | multi-method face forgery | [Official repository](https://github.com/inclusionConf/MFFI) | aggregate results only; no explicit redistribution license was identified |
| RetouchingFFHQ | fine-grained face retouching | [Paper](https://arxiv.org/abs/2307.10642) and authors' access link | aggregate results only; the evaluated archive was supplied by the authors without public redistribution terms |
| FFHQ | untouched control portraits | [Official repository](https://github.com/NVlabs/ffhq-dataset) | dataset and per-image Flickr licenses apply |

## Dataset-specific definitions

Labels are normalized to `0 = bona fide` and `1 = manipulated/retouched` before evaluation. For CelebHQ-FM, bona fide means the original `orig` image; rows marked `EDIT_NAME=none` are not silently treated as originals. FFHQR and PPR10K evaluate retouched targets against their source portraits. RetouchingFFHQ uses matching de-duplicated FFHQ originals as the bona fide baseline.

MFFI results come from a class-balanced random sample of the locally available pool, not a class-proportional sample. RetouchingFFHQ uses proportional stratified sampling across available retouching categories. FFHQ is a one-class control and therefore has no AUC or EER.

## Publication rule

Per-image score rows and thumbnails are publishable only when the relevant dataset and source-image terms permit redistribution. The reporting tools can create full local tables and galleries for authorized users. Public reports fall back to aggregate statistics and checksums when rights are absent, unclear, or restrictive.

Apache-2.0 applies only to repository code. It does not override dataset terms.
