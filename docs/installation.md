# Installation and deployment

## Requirements

- Linux and Python 3.10;
- an NVIDIA CUDA-capable GPU with enough memory for SelfMAD++;
- a CUDA 12.1-compatible driver;
- build tools and CMake for dlib;
- Git submodules initialized at the pinned revision.

The tested experiment environment used NVIDIA RTX 2080 Ti GPUs. CPU inference is not supported by the reference service because the pinned upstream model assigns its internal branches to CUDA devices during construction.

## Native installation

```bash
git submodule update --init --recursive
python3.10 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/model-cu121.txt
python -m pip install -e .
python scripts/fetch_artifacts.py
slaif-fms verify-artifacts
```

`fetch_artifacts.py` downloads the authors' SMDD checkpoint and dlib 81-point predictor into the ignored `models/` directory. It deletes a downloaded artifact and fails if the pinned checksum does not match. The SelfMAD++ constructor also obtains pretrained HRNet and OpenCLIP assets on first load; preserve `TORCH_HOME` and `HF_HOME` caches for offline restarts.

Configuration uses the `SLAIF_FMS_` prefix. See [`.env.example`](../.env.example) for every setting. Model artifacts are never read from an upload and must be mounted read-only in production.

## CLI

```bash
CUDA_VISIBLE_DEVICES=0 slaif-fms score image.jpg --output json
CUDA_VISIBLE_DEVICES=0 slaif-fms score-batch images/ -o scores.jsonl --format jsonl
```

The batch output can be JSON Lines or a compact CSV. Batch paths are local operator paths and must be sanitized before publication.

## HTTP API

Start one process with one visible GPU:

```bash
CUDA_VISIBLE_DEVICES=0 uvicorn slaif_fms.api:app --host 0.0.0.0 --port 8000 --workers 1
```

`POST /v1/score` accepts one multipart field named `image`. JPEG, PNG, and WebP are supported. Defaults limit compressed uploads to 20 MiB and decoded images to 40 million pixels.

A scored response contains a nullable score, stable score semantics, model identity, preprocessing identity, source dimensions, face count, and crop box. If no face is found, the service returns HTTP 200 with `status=unscorable`, `score=null`, and `reason=no_face_detected`. Malformed, oversized, and unsupported uploads receive typed 4xx errors.

`GET /healthz` reports process liveness. `GET /readyz` reports 200 only after model loading succeeds.

The API has no authentication. Place it behind the SLAIF API gateway or another authenticated private ingress. Do not log request bodies or image bytes.

## Docker

The image uses CUDA 12.1 and one Gunicorn/Uvicorn worker:

```bash
docker compose build
docker compose up
```

Populate `models/` before starting. The compose file mounts model artifacts read-only and stores foundation-model caches in a named volume.

For two GPUs, run two containers or processes with distinct ports and `CUDA_VISIBLE_DEVICES=0` and `CUDA_VISIBLE_DEVICES=1`, then load-balance between them. Do not expose both GPUs to one process: the pinned model changes its internal device placement when it sees multiple devices, which defeats process-level parallelism and increases cross-device transfers.
