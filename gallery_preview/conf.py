"""Minimal Sphinx project that builds only selected gallery examples.

Used by ``pixi run gallery-example <pattern> [examples_dir]``. It runs the
same scraper hooks as the real docs (from ``docs/_scripts``) but skips the
rest of the docs, so iterating on an example takes seconds, not minutes.

Configured through environment variables, which the pixi task sets:

- ``GALLERY_EXAMPLE``: regex matched against example paths; only matching
  examples are executed.
- ``GALLERY_EXAMPLES_DIR``: the napari ``examples`` folder, absolute or
  relative to the root of this repo. Defaults to ``../napari/examples``.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]

sys.path.insert(0, str(REPO_ROOT / 'docs'))
from _scripts.gallery_scraper import napari_scraper, reset_napari  # noqa: E402

examples_dir = REPO_ROOT / os.environ.get('GALLERY_EXAMPLES_DIR', '../napari/examples')

project = 'napari gallery preview'
extensions = ['sphinx_gallery.gen_gallery', 'sphinx_tags']
exclude_patterns = ['_build']

# Examples use the `tags` directive; render it, but skip the tag pages.
tags_create_tags = False

sphinx_gallery_conf = {
    'examples_dirs': str(examples_dir.resolve()),
    'gallery_dirs': 'gallery',
    'filename_pattern': os.environ.get('GALLERY_EXAMPLE', '$^'),
    'ignore_pattern': 'README.rst|/*_.py',
    'download_all_examples': False,
    'image_scrapers': ('matplotlib', napari_scraper),
    'reset_modules': (reset_napari,),
    'reset_modules_order': 'both',
}
