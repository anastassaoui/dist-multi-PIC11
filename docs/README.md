# Documentation Build Instructions

This directory contains Sphinx documentation for the distillation backend package.

## Setup

1. Install documentation requirements:
```bash
pip install -r ../requirements-doc.txt
```

## Build Documentation

### Windows
```bash
make.bat html
```

### Linux/Mac
```bash
make html
```

## View Documentation

After building, open:
```
docs/_build/html/index.html
```

## Clean Build Files

### Windows
```bash
make.bat clean
```

### Linux/Mac
```bash
make clean
```

## Output Location

Generated HTML documentation: `docs/_build/html/`

## Hosted Documentation

To host on GitHub Pages:
1. Build HTML: `make html`
2. Copy `_build/html/*` to repository root `docs/` folder
3. Enable GitHub Pages in repository settings
4. Select `docs/` folder as source
