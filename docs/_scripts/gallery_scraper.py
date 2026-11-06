"""Sphinx-Gallery hooks for napari examples.

Kept in an importable module, rather than in ``conf.py``, so that other Sphinx
projects (such as a single-example preview build) can reuse them.

Viewers persist across the code blocks of an example, as they would in a
notebook, and are only closed between examples (see ``reset_napari``, which
runs before and after each example via ``reset_modules_order = 'both'``).
After each code block, ``napari_scraper`` screenshots every open viewer, but
only adds a screenshot to the page if that viewer looks different from the
last time it was shown. A block that does not change any viewer therefore
gets no image.
"""

import napari
import numpy as np
from napari.utils.io import imsave
from sphinx_gallery import scrapers

# The last screenshot shown for each open window, keyed by id(window).
_last_screenshots: dict[int, np.ndarray] = {}


def reset_napari(gallery_conf, fname):
    from napari.settings import get_settings
    from qtpy.QtWidgets import QApplication

    # Start every example from a clean slate.
    napari.Viewer.close_all()
    _last_screenshots.clear()

    settings = get_settings()
    settings.appearance.theme = 'dark'

    # Disabling `QApplication.exec` means example scripts can call `exec`
    # (scripts work when run normally) without blocking example execution by
    # sphinx-gallery. (from qtgallery)
    QApplication.exec = lambda _: None


def napari_scraper(block, block_vars, gallery_conf):
    """Screenshot every napari viewer that changed during this code block.

    `app.processEvents()` allows Qt events to propagate and prevents hanging.
    """
    imgpath_iter = block_vars['image_path_iterator']

    if app := napari.qt.get_qapp():
        app.processEvents()
    else:
        return ''

    img_paths = []
    for win in reversed(napari._qt.qt_main_window._QtMainWindow._instances):
        # flash=False: the flash animation would otherwise make the next
        # screenshot of an unchanged viewer look different.
        screenshot = win._window.screenshot(canvas_only=False, flash=False)

        previous = _last_screenshots.get(id(win))
        if previous is not None and np.array_equal(previous, screenshot):
            continue  # nothing changed in this viewer since it was last shown

        _last_screenshots[id(win)] = screenshot
        img_path = next(imgpath_iter)
        imsave(img_path, screenshot)
        img_paths.append(img_path)

    return scrapers.figure_rst(img_paths, gallery_conf['src_dir'])


# Settings that decide how examples run and are screenshotted. Shared by
# docs/conf.py and gallery_preview/conf.py, so the preview build cannot drift
# from the real one; each conf only adds its own paths and page options.
GALLERY_EXECUTION_CONF = {
    'ignore_pattern': 'README.rst|/*_.py',
    'image_scrapers': ('matplotlib', napari_scraper),
    'reset_modules': (reset_napari,),
    'reset_modules_order': 'both',
    'only_warn_on_example_error': False,
    'abort_on_example_error': True,
}
