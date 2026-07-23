# Evaluation and reference profiling

## Canonical score table

Evaluation consumes CSV with one scored image per row. Required concepts are:

| Concept | Accepted columns | Meaning |
| --- | --- | --- |
| identifier | `relative_id`, `relpath`, `manifest_relpath`, `virtual_path`, or `path` | stable image identifier |
| label | `label`, `label_id`, or `target_label` | `0` bona fide, `1` manipulated |
| score | `score` or `prob_morph` | SelfMAD++ class-1 softmax |

The service uses this unchanged scalar as a bona fide deviation score: higher values indicate lower bona fide compatibility. `prob_morph` remains an accepted legacy/native input-column name for reproducibility; it does not limit the service framing to face morphs. Scores are never inverted for product presentation or per-dataset evaluation.

Optional grouping columns include `operation`, `provider`, `operation_count`, `operation_level`, `method`, and `category`. Local `path` is used only to generate a local exemplar gallery and must never be published.

Rows marked `unscorable` or `error` are excluded from score metrics and must be reported separately as preprocessing/scoring failures. They must never be converted into zero scores.

## Generate evidence

```bash
python -m pip install -e '.[evaluation]'
slaif-fms evaluation report scores.csv --dataset example --output-dir results/example
```

The command writes class summaries, machine-readable metrics, ROC points, class-normalized histogram bins, ROC PNG/SVG, histogram PNG/SVG, ECDF PNG/SVG, and any available grouping tables. Positive-label polarity is permanently fixed to `1 = manipulated`. EER is the nearest discrete crossing of FPR and FNR, matching the frozen experiment scripts.

Bootstrap confidence intervals use deterministic stratified resampling. Rows derived from the same source identity are not independent; for formal claims, prepare identity-disjoint data and use an identity-aware statistical analysis.

## Dataset adapters

Dataset-specific label normalization is implemented in `slaif_fms.evaluation.adapters`. In particular, CelebHQ-FM only accepts original `_orig` images as bona fide; `EDIT_NAME=none` pipeline output is rejected as a bona fide source. The public dataset registry is packaged in `slaif_fms/resources/datasets.json`.

Create deterministic balanced samples with:

```bash
slaif-fms evaluation sample-balanced full_manifest.csv \
  --output sample.csv --fraction 0.05 --seed 20260718
```

## Bona fide reference profiling

After scoring representative untouched images with the same model and preprocessing:

```bash
slaif-fms evaluation profile-reference untouched_scores.csv \
  --output-dir reference-profile --name enrollment-channel \
  --percentiles 0.95,0.99,0.999
```

This reports empirical percentiles and distributions for the user's bona fide acquisition domain. Lower scores are more compatible and higher scores are less compatible with the model's learned bona fide side of its decision boundary. The profile does not calibrate the score into a probability, establish that an image is bona fide, estimate attack recall, recommend a threshold, or guarantee future false-positive rates.

## Exemplars and publication

```bash
slaif-fms evaluation gallery scores.csv \
  --dataset mffi --output-dir local-gallery --local-only
```

The local gallery contains lowest/highest bona fide and lowest/highest manipulated examples plus a manifest. Public mode fails unless the dataset policy and a per-asset permission file authorize every copied image with source URL, author, license, and license URL.

`sanitize-public-rows` removes local paths and refuses identified-row publication for datasets whose terms are restrictive or unclear. Aggregate metrics remain publishable independently of score-row and image redistribution.

For RetouchingFFHQ, add `--group-by operation` to produce the four overall exemplars plus four exemplars for every operation represented in the score table.

## Parallel scoring

SelfMAD++ should run as two processes, each seeing one GPU. Score raw source images with author cropping in memory, or use `--preprocessed` only when the manifest points to crops already created by the pinned author procedure:

```bash
slaif-fms evaluation score-manifest manifest.csv \
  --dataset mffi --output scores.csv --raw
```

`scripts/run_two_gpu_workers.py` appends deterministic shard arguments and substitutes `{shard}` and `{gpu}` in command arguments. Use a distinct output file per shard:

```bash
python scripts/run_two_gpu_workers.py -- \
  slaif-fms evaluation score-manifest manifest.csv \
  --dataset mffi --output 'scores_shard{shard}.csv' --raw
```

CPU author cropping of a subsequent dataset may run concurrently with GPU scoring, provided output manifests remain separate and every stage records its input checksum.
