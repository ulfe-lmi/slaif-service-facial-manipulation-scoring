# Score-tail image examples

The image examples requested for this evaluation were generated from the exact author-cropped files represented by the frozen scores. They are intentionally not stored in Git.

Run:

```bash
python scripts/generate_local_galleries.py \
  --source-root /path/to/frozen-run-root \
  --output-root /path/to/local-gallery \
  --summary results/examples/local_gallery_summary.csv \
  --extremes-summary results/examples/score_extremes.csv
```

Each two-class dataset receives lowest/highest bona fide and lowest/highest manipulated examples. FFHQ receives its lowest/highest control examples. RetouchingFFHQ additionally receives the four examples for each operation.

To publish an image, use `slaif-fms evaluation gallery --public --permissions permissions.json`. The permission record must identify the exact asset and include source URL, author, license, and license URL. Repository-level dataset access is not sufficient attribution for an individual face image.
