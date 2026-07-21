# Contributing

Use Python 3.10 and install the development dependencies with `python -m pip install -e '.[dev]'`.

Run before opening a pull request:

```bash
ruff check .
pytest
```

Do not commit model checkpoints, landmark models, dataset files, face crops, local manifests containing absolute paths, credentials, or outputs whose redistribution terms are unknown. New benchmark evidence must state the model revision, preprocessing revision, selection denominator, attempted count, scored count, failures, and fixed score direction.
