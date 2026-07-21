<div align="center">
  <a href="https://www.slaif.si">
    <img src="https://slaif.si/img/logos/SLAIF_logo_ANG_barve.svg" width="400" height="400" alt="SLAIF">
  </a>
</div>

# SLAIF Facial Manipulation Scoring

[![CI](https://github.com/ulfe-lmi/slaif-service-facial-manipulation-scoring/actions/workflows/ci.yml/badge.svg)](https://github.com/ulfe-lmi/slaif-service-facial-manipulation-scoring/actions/workflows/ci.yml)
[![CodeQL](https://github.com/ulfe-lmi/slaif-service-facial-manipulation-scoring/actions/workflows/codeql.yml/badge.svg)](https://github.com/ulfe-lmi/slaif-service-facial-manipulation-scoring/actions/workflows/codeql.yml)

SLAIF Facial Manipulation Scoring is a reproducible service wrapper and evaluation suite for [SelfMAD++](https://github.com/LeonTodorov/SelfMADpp), a single-image morphing attack detector developed at the University of Ljubljana. It accepts a facial image and returns the model's continuous class-1 score after the preprocessing prescribed by the model authors.

> [!IMPORTANT]
> The score is an **uncalibrated model output**, not the probability that an image is manipulated and not an authenticity decision. This project does not prescribe a threshold. Performance depends on the image domain and manipulation family; published benchmark behavior does not establish correctness for an individual image.

The project provides:

- exact author-crop preprocessing and a versioned SelfMAD++ scoring interface;
- a command-line tool, Python API, and stateless FastAPI endpoint;
- manifest-driven benchmark tooling with fixed score polarity;
- reference-distribution profiling for users evaluating their own untouched images;
- frozen, reproducible benchmark reports with coverage, ROC curves, and score histograms.

The repository contains no model checkpoint and no benchmark images. Dataset and model access remain subject to their owners' terms.

## Status

The MVP score service, CLI, exact author preprocessing, evaluation toolkit, reference profiler, and frozen benchmark report are implemented. The service remains research software and requires operators to validate behavior in their own domain.

## Quick Start

Clone the pinned SelfMAD++ submodule, create a Python 3.10 environment, and install the CUDA dependencies:

```bash
git clone --recurse-submodules https://github.com/ulfe-lmi/slaif-service-facial-manipulation-scoring.git
cd slaif-service-facial-manipulation-scoring
python3.10 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/model-cu121.txt
python -m pip install -e .
python scripts/fetch_artifacts.py
slaif-fms verify-artifacts
```

Bind the process to exactly one GPU and score an image. Author cropping is always applied by the command:

```bash
CUDA_VISIBLE_DEVICES=0 slaif-fms score portrait.jpg
```

Run the API with one process per visible GPU:

```bash
CUDA_VISIBLE_DEVICES=0 uvicorn slaif_fms.api:app --host 0.0.0.0 --port 8000 --workers 1
curl -sS -F image=@portrait.jpg http://localhost:8000/v1/score
```

See [Installation and deployment](docs/installation.md) for artifact caching, Docker, two-GPU deployment, response schemas, and failure behavior.

For reproducible score tables, fixed-polarity metrics, customer reference profiling, and rights-aware exemplar galleries, see [Evaluation and reference profiling](docs/evaluation.md).

## Service Contract

Higher scores mean that SelfMAD++ found stronger evidence for the model's learned morph/manipulation class. The service:

- does not classify an image as authentic or manipulated;
- does not enforce or recommend a threshold;
- does not authenticate a person or an identity document;
- does not detect arbitrary document edits or every form of image manipulation;
- does not convert its output into a calibrated probability.

Users may evaluate scores on representative untouched data from their own domain and define their own policy. Such a policy is external to this service and must account for the customer's costs, risks, population, acquisition process, and manipulation threats. See [Service contract](docs/service-contract.md).

## Reproducibility

The reference implementation is pinned to:

- SelfMAD++ commit `75bcbe08ad66b758d1e6d7a1630a91bb797d8019`;
- SelfMAD++ SMDD checkpoint SHA-256 `642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4`;
- dlib 81-point landmark model SHA-256 `8cae4375589dd915d9a0a881101bed1bbb4e9887e35e63b024388f1ca25ff869`;
- upstream `utils/preprocessing/crop.py` blob SHA-256 `a9a5f667e9e85e8b7f6b255221e5855ddbcfbd7de3c8e23324fa967990922ad6`.

See [Provenance](docs/provenance.md) for artifact links and verification rules and [Datasets](docs/datasets.md) for source pages, access conditions, evaluated scope, and redistribution status.

## Frozen Benchmark Snapshot

All values below use the author crop and fixed `1 = manipulated` score direction. EER is a conventional dataset statistic, not a service threshold.

| Dataset | Dataset evaluated | Bona fide n | Manipulated n | Bona fide mean | Manipulated mean | AUC | EER |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| STR-FFHQ-FM | 99.31% | 1,682 | 1,606 | 0.102 | 0.687 | 0.900 | 0.180 |
| READFake | 99.95% | 716 | 1,419 | 0.200 | 0.475 | 0.688 | 0.373 |
| CelebHQ-FM | 99.75% | 1,722 | 12,732 | 0.435 | 0.920 | 0.944 | 0.134 |
| FFHQR | 2.85% | 1,994 | 1,997 | 0.095 | 0.123 | 0.598 | 0.429 |
| PPR10K | 58.04% | 6,400 | 19,510 | 0.235 | 0.216 | 0.467 | 0.522 |
| MFFI | 4.14% | 21,273 | 21,101 | 0.457 | 0.774 | 0.782 | 0.287 |
| RetouchingFFHQ | 6.75% | 34,064 | 49,939 | 0.094 | 0.167 | 0.686 | 0.367 |
| FFHQ control | 98.71% | 69,098 | - | 0.095 | - | - | - |

`Dataset evaluated` is the successfully scored share of the official or stated reference total. For RetouchingFFHQ, it is 49,939 scored retouched rows out of the supplied archive's 739,317 manifest rows; the 34,064 bona fide samples are unique matching FFHQ originals added as the comparison baseline. MFFI uses the paper's approximately 1.024 million samples as its denominator. FFHQR uses all 140,000 original and retouched class samples as its denominator.

The strongest ranking separation appears on CelebHQ-FM and STR-FFHQ-FM. MFFI shows useful but overlapping cross-domain separation. Professional/aesthetic retouching is weakly separated or not separated, depending on the dataset. This supports a narrow manipulation-indication score, not a claim to detect every edited image.

See the [full frozen report](results/README.md), [service datasheet](docs/service-datasheet.md), exact coverage percentages, confidence intervals, ROC plots, histograms, ECDFs, operation tables, and publication notes.

## License and Citation

Repository code is licensed under [Apache-2.0](LICENSE). That license does not apply to SelfMAD++ checkpoints, dlib model data, datasets, benchmark images, or other third-party material. Consult [Third-party notices](THIRD_PARTY_NOTICES.md) before use or redistribution.

If this software or its benchmark report contributes to research, cite the SelfMAD++ paper:

```bibtex
@article{IVANOVSKA2026103921,
  title = {SelfMAD++: Self-supervised foundation model with local feature enhancement for generalized morphing attack detection},
  journal = {Information Fusion},
  volume = {127},
  pages = {103921},
  year = {2026},
  author = {Marija Ivanovska and Leon Todorov and Peter Peer and Vitomir Struc},
  doi = {10.1016/j.inffus.2025.103921}
}
```

## Maintainers

- [Janez Pers](https://github.com/jpers1), [Laboratory for Machine Intelligence](https://lmi.fe.uni-lj.si/), University of Ljubljana
- [Laboratory for Machine Intelligence](https://lmi.fe.uni-lj.si/), University of Ljubljana

We acknowledge the support of the EC/EuroHPC JU and the Slovenian Ministry of HESI via the project SLAIF (grant number 101254461). Project website: [www.slaif.si](https://www.slaif.si).
