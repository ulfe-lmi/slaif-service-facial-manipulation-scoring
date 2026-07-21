# Repository agent guidance

## Current scope

Help only with installing and running the SLAIF Facial Manipulation Scoring API
as a GPU-backed Docker service on Linux. Use
`.codex/skills/install-slaif-fms/SKILL.md` for every installation, deployment,
upgrade, startup, or installation-troubleshooting request.

Do not use this repository guidance for model development, training, evaluation,
dataset acquisition, benchmark reproduction, or score interpretation. Never
download datasets or benchmark images as part of installation.

## Audience and communication

Assume the user may be unfamiliar with Linux, terminals, Docker, networking, and
GPU tooling. Explain briefly what each stage does, use copy-pasteable commands,
show how to recognize success, and translate errors into plain language. Prefer
safe defaults and one small stage at a time.

## Privileged commands

Never assume that sudo exists, that passwordless sudo is enabled, or that the
agent may exercise administrator privileges.

- Run unprivileged, read-only checks first.
- Never run `sudo`, `sudo -n`, `su`, or `pkexec` yourself.
- If a privileged command is necessary, explain why, provide the narrowest exact
  `sudo`-prefixed command, and politely ask the user to copy and paste it.
- Wait for the user to return the output before continuing.
- Do not ask the user to pipe a remote script into sudo.
- Do not add the user to the `docker` group without explaining that it grants
  root-equivalent access and obtaining explicit agreement.

If Docker works without sudo, continue without introducing privilege changes.

## Safety defaults

- Treat model files as external artifacts and require the pinned SHA-256 values.
- Use exactly one visible NVIDIA GPU per service process.
- Keep model artifacts mounted read-only and foundation-model caches persistent.
- Bind the unauthenticated API to localhost or a private interface by default;
  require explicit user approval before binding it to all interfaces.
- Do not upload user images, log image contents, or fetch a face image merely to
  test inference. Use health checks and a generated blank image, then let the user
  test with an image they control.
- Record documentation mismatches, workarounds, final commands, versions, and
  verification results in `DEPLOYMENT_NOTES.md`.
