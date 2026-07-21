---
name: install-slaif-fms
description: Install, deploy, validate, upgrade, or troubleshoot the SLAIF Facial Manipulation Scoring API as a single-GPU Docker service on Linux. Use for fresh host setup, Docker/NVIDIA preflight checks, checksum-verified model retrieval, the Playwright checkpoint workaround, private API exposure, restart-safe operation, and beginner-friendly installation support. Never use it to obtain datasets, reproduce benchmarks, train models, or interpret scores.
---

# Install SLAIF FMS

Install the service incrementally and verify every boundary. Keep the user in
control of privileged commands and never download datasets.

## Rules

- Read the repository `AGENTS.md`, `docs/installation.md`, `docs/provenance.md`,
  `THIRD_PARTY_NOTICES.md`, `Dockerfile`, and current artifact downloader before
  changing anything.
- Preserve the pinned service and SelfMAD++ revisions unless the user explicitly
  requests an upgrade.
- Require exactly one visible CUDA GPU per container.
- Do not run training, evaluation, batch-scoring, dataset, or benchmark scripts.
- Never run a privileged command. If an unprivileged command fails for lack of
  permission, explain the need and ask the user to copy and paste the narrowest
  exact `sudo`-prefixed command. Wait for its output.
- Do not expose the unauthenticated API publicly by default.
- Keep a running `DEPLOYMENT_NOTES.md` with commands, versions, failures,
  workarounds, and validation results.

## 1. Establish the target

- If already inside this repository, do not clone it again. Record `git rev-parse
  HEAD` and `git submodule status --recursive`.
- Otherwise clone with `--recurse-submodules`; do not clone or download any
  dataset repository.
- Confirm the desired network reachability. Recommend localhost for same-host
  testing or a specific private IP for LAN/VPN testing. Use port 8000 unless it
  is occupied.
- Explain that the output is an uncalibrated manipulation-indication score, not
  an authenticity decision.

## 2. Run unprivileged preflight checks

Check and report:

- Linux distribution and architecture: `uname -a` and `/etc/os-release`.
- Free disk and RAM: `df -h .` and `free -h`.
- NVIDIA GPU, driver, and free VRAM: `nvidia-smi`.
- Docker client, daemon access, Compose, and NVIDIA runtime.
- Current addresses and listening ports with `ip -4 -brief address` and `ss -ltn`.

Do not ask the user where a tool is before checking. If Docker, the NVIDIA
Container Toolkit, or another system package must be installed, detect the
distribution and consult its current official instructions. Present one scoped
sudo command at a time for the user to run. Do not silently change firewall,
groups, daemon configuration, or package repositories.

## 3. Retrieve only model artifacts

Create the ignored `models/` directory. Never fetch datasets or example faces.

Require these final files and hashes:

- `models/SelfMADpp_SMDD.tar`:
  `642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4`
- `models/shape_predictor_81_face_landmarks.dat`:
  `8cae4375589dd915d9a0a881101bed1bbb4e9887e35e63b024388f1ca25ff869`

Try `python scripts/fetch_artifacts.py` first only when its URLs are reachable.
The authors' SharePoint checkpoint has returned HTTP 403 to curl and Python, and
the documented dlib 81-point URL has returned HTTP 404. Treat those as source
availability problems, not reasons to disable verification.

For the checkpoint, use the bundled
`scripts/download_checkpoint_playwright.cjs` through the official matching
Playwright image. The image supplies Chromium but not the Node package, so install
the pinned package only inside the disposable container:

```bash
mkdir -p models
docker run --rm --ipc=host \
  -v "$PWD/.codex/skills/install-slaif-fms/scripts:/skill:ro" \
  -v "$PWD/models:/downloads" \
  -w /tmp \
  mcr.microsoft.com/playwright:v1.61.1-noble \
  bash -lc 'npm init -y >/dev/null && npm install --no-save playwright@1.61.1 >/dev/null && NODE_PATH=/tmp/node_modules node /skill/download_checkpoint_playwright.cjs'
```

If Docker permission is denied, do not add sudo yourself. Ask the user to rerun
the displayed command with `sudo docker ...` and return the output. The helper
must download to `.part`, checksum it, and only then promote it.

For the predictor, use an immutable checksum-identical mirror only while the
documented source remains unavailable:

```bash
curl -fL --retry 3 \
  -o models/shape_predictor_81_face_landmarks.dat.part \
  'https://huggingface.co/matt3ounstable/dlib_predictor_recognition/resolve/a5b40d183fb2c3584518c349e2aabe19c3a781e0/shape_predictor_81_face_landmarks.dat'
```

Verify the pinned hashes before renaming the predictor:

```bash
printf '%s  %s\n' \
  '642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4' \
  'models/SelfMADpp_SMDD.tar' | sha256sum --check --strict
printf '%s  %s\n' \
  '8cae4375589dd915d9a0a881101bed1bbb4e9887e35e63b024388f1ca25ff869' \
  'models/shape_predictor_81_face_landmarks.dat.part' | sha256sum --check --strict
mv models/shape_predictor_81_face_landmarks.dat.part \
  models/shape_predictor_81_face_landmarks.dat
```

If a checksum fails, do not rename or use the file. Run the repository's
`slaif-fms verify-artifacts` command inside the final image as a second check.

## 4. Build and run the Docker service

Prefer the repository Dockerfile. Compose is optional; use plain Docker when the
plugin is absent. Build with a traceable tag based on the service commit:

```bash
docker build --pull -t slaif-fms:<short-commit> .
```

If Buildx is absent, omit BuildKit-only flags such as `--progress=plain`. Do not
rewrite the application merely to compensate for host tooling.

Create a named cache and start one restart-managed container. Substitute the
confirmed private address and image tag:

```bash
docker volume create slaif-fms-cache
docker run -d \
  --name slaif-fms \
  --restart unless-stopped \
  --gpus device=0 \
  -p <private-ip>:8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e SLAIF_FMS_CHECKPOINT_PATH=/app/models/SelfMADpp_SMDD.tar \
  -e SLAIF_FMS_LANDMARK_MODEL_PATH=/app/models/shape_predictor_81_face_landmarks.dat \
  -v "$PWD/models:/app/models:ro" \
  -v slaif-fms-cache:/cache \
  slaif-fms:<short-commit>
```

If the container name already exists, inspect it before proposing removal or
replacement. Explain any interruption and obtain confirmation before replacing a
working service. Do not expose multiple GPUs to one process.

## 5. Validate and hand off

Allow extra time on first startup while HRNet and OpenCLIP weights populate the
named cache. Diagnose with container state and logs; do not loop blindly.

Require all of the following:

- `GET /healthz` returns HTTP 200.
- `GET /readyz` returns HTTP 200 with the model loaded.
- The container sees CUDA, exactly one device, and the expected GPU name.
- Docker reports `unless-stopped`, the intended IP/port mapping, a read-only
  model mount, and the persistent cache volume.
- A generated blank PNG returns HTTP 200 with `status=unscorable` and
  `reason=no_face_detected`.
- An unsupported media type returns the documented HTTP 400 error.
- A controlled restart returns to readiness without redownloading the cache.

Do not fetch a face image for testing. State clearly that a scored forward pass
requires an operator-controlled face image. Provide:

```bash
curl -sS -F image=@portrait.jpg http://<private-ip>:8000/v1/score
```

Finish with the confirmed IP, port, container name, image tag, revisions,
artifact hashes, test results, and a link to `DEPLOYMENT_NOTES.md`. Never claim
success while `/readyz` is unavailable.
