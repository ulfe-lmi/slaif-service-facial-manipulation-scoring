FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake python3.10 python3.10-dev python3.10-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3.10 -m venv "$VIRTUAL_ENV"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app
COPY requirements/model-cu121.txt requirements/model-cu121.txt
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY vendor/SelfMADpp ./vendor/SelfMADpp
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements/model-cu121.txt \
    && python -m pip install . gunicorn

FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app/src:/app/vendor/SelfMADpp \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/cache/huggingface \
    TORCH_HOME=/cache/torch

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 python3.10 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system slaif \
    && useradd --system --gid slaif --home /app slaif \
    && mkdir -p /app/models /cache/huggingface /cache/torch \
    && chown -R slaif:slaif /app /cache

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app
WORKDIR /app
USER slaif
EXPOSE 8000

CMD ["gunicorn", "slaif_fms.api:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300"]
