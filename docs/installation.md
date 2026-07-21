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

### Optional API-key authentication

By default, the service looks for `secrets/api_key`. If that file is absent, authentication is
disabled for backward compatibility. If it is present, every `POST /v1/score` request must include
its value in the `X-API-Key` header. Generate a 256-bit key before starting the service:

```bash
python scripts/generate_api_key.py
```

The command displays the new key once and writes `secrets/api_key` with owner-only (`0600`)
permissions. Store the displayed value in the calling web server's secret store. The local file is
excluded from Git and the Docker build context. The generator refuses to replace an existing key;
use `--force` only when intentionally rotating it:

```bash
python scripts/generate_api_key.py --force
```

The service reads the key once at startup. Restart it after rotation. An empty, unreadable, or
non-file key path stops startup instead of silently disabling authentication. A missing file
intentionally disables authentication.

Call the protected endpoint with the key printed by the generator:

```bash
curl -sS -H "X-API-Key: <generated-key>" \
  -F image=@portrait.jpg http://localhost:8000/v1/score
```

Missing and incorrect keys receive HTTP 401 with the same `invalid_api_key` response. The
`GET /healthz` and `GET /readyz` probes, as well as `/docs` and `/openapi.json`, remain available
without a key so health checks and operational tooling continue to work.

Change the file location with `SLAIF_FMS_API_KEY_FILE`. Continue to place the service behind a
private ingress or VPN with TLS; the API key is an additional access control, not a replacement for
transport security. Do not log request bodies, image bytes, or the API key.

## Docker

The image uses CUDA 12.1 and one Gunicorn/Uvicorn worker:

```bash
docker compose build
docker compose up
```

Populate `models/` before starting. The compose file mounts model artifacts read-only and stores foundation-model caches in a named volume.

Compose also mounts the local `secrets/` directory read-only. When `secrets/api_key` exists, the
container startup helper copies it into a private runtime file readable by the non-root `slaif`
process, then drops privileges before starting Gunicorn. This allows the host copy to remain mode
`0600`. If the file is absent, the same Compose service starts with authentication disabled.

For plain Docker, include the equivalent read-only mount and setting:

```bash
docker run --gpus device=0 -p 127.0.0.1:8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e SLAIF_FMS_API_KEY_FILE=/run/secrets/api_key \
  -v "$PWD/models:/app/models:ro" \
  -v "$PWD/secrets:/run/secrets:ro" \
  -v model-cache:/cache \
  slaif-fms:<tag>
```

After generating or rotating a key used by Compose, restart the process so it reloads the file:

```bash
docker compose restart scorer
```

For two GPUs, run two containers or processes with distinct ports and `CUDA_VISIBLE_DEVICES=0` and `CUDA_VISIBLE_DEVICES=1`, then load-balance between them. Do not expose both GPUs to one process: the pinned model changes its internal device placement when it sees multiple devices, which defeats process-level parallelism and increases cross-device transfers.
