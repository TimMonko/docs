"""Sphinx-Gallery hooks for napari examples.

Kept in an importable module, rather than in ``conf.py``, so that other Sphinx
projects (such as a single-example preview build) can reuse them.
"""

import napari
from sphinx_gallery import scrapers


def reset_napari(gallery_conf, fname):
    from napari.settings import get_settings
    from qtpy.QtWidgets import QApplication

    settings = get_settings()
    settings.appearance.theme = 'dark'

    # Disabling `QApplication.exec` means example scripts can call `exec`
    # (scripts work when run normally) without blocking example execution by
    # sphinx-gallery. (from qtgallery)
    QApplication.exec = lambda _: None


def napari_scraper(block, block_vars, gallery_conf):
    """Basic napari window scraper.

    Looks for any QtMainWindow instances and takes a screenshot of them.

    `app.processEvents()` allows Qt events to propagateo and prevents hanging.
    """
    imgpath_iter = block_vars['image_path_iterator']

    if app := napari.qt.get_qapp():
        app.processEvents()
    else:
        return ''

    img_paths = []
    for win, img_path in zip(
        reversed(napari._qt.qt_main_window._QtMainWindow._instances),
        imgpath_iter,
    ):
        img_paths.append(img_path)
        win._window.screenshot(img_path, canvas_only=False)

    napari.Viewer.close_all()
    app.processEvents()

    return scrapers.figure_rst(img_paths, gallery_conf['src_dir'])
