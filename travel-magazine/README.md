# Morrow Tide Journal source kit

This kit creates a two-page fictional travel magazine.

The PDF uses original copy and licensed stock photographs.

## Create the PDF

Run this command from the repository root:

```bash
uv run --with reportlab --with pillow python examples/travel-magazine/generate.py \
  --output output/pdf/morrow-tide-journal-atlantic.pdf
```

The generator reads all content and assets from this directory.

The output uses a 210 by 270 mm page size.

The generator uses fixed metadata and deterministic PDF settings.

## Contents

- `content.json` contains the original English copy.
- `generate.py` contains the page layout.
- `assets/photos` contains the stock photographs.
- `assets/fonts` contains the embedded fonts and their licenses.
- `ASSET-LICENSES.md` records the asset sources and SHA-256 values.

This kit does not contain a change manifest or a modified PDF.
