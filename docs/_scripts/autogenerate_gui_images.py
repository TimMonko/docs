from pathlib import Path

from qtpy.QtCore import QTimer, QPoint
import napari

from napari._qt.qt_event_loop import get_qapp
from napari._qt.qt_resources import get_stylesheet
from napari._qt.dialogs.qt_modal import QtPopup
from qtpy.QtWidgets import QApplication

DOCS = REPO_ROOT_PATH = Path(__file__).resolve().parent.parent
IMAGES_PATH = DOCS / "images" / "_autogenerated"
IMAGES_PATH.mkdir(parents=True, exist_ok=True)
WIDGETS_PATH = IMAGES_PATH / "widgets"
WIDGETS_PATH.mkdir(parents=True, exist_ok=True)
MENUS_PATH = IMAGES_PATH / "menus"
MENUS_PATH.mkdir(parents=True, exist_ok=True)
POPUPS_PATH = IMAGES_PATH / "popups"
POPUPS_PATH.mkdir(parents=True, exist_ok=True)

def autogenerate_images():
    app = get_qapp()
    
    # Create viewer with visible window
    viewer = napari.Viewer(show=True)
    viewer.window._qt_window.resize(1000, 800)
    viewer.window._qt_window.setStyleSheet(get_stylesheet("dark"))
    
        # Ensure window is active
    viewer.window._qt_window.activateWindow()
    viewer.window._qt_window.raise_()
    app.processEvents()
    
    viewer.screenshot(str(IMAGES_PATH / "viewer_empty.png"), canvas_only=False)
    # Add sample data
    viewer.open_sample(plugin='napari', sample='cells3d')
    
    app.processEvents() # Ensure viewer is fully initialized
    viewer.screenshot(str(IMAGES_PATH / "viewer_cells3d.png"), canvas_only=False)
    
    # Open the console
    viewer_buttons = find_widget_by_class(viewer.window._qt_window, "QtViewerButtons")
    viewer_buttons.consoleButton.click()
    
    # Print Qt widget hierarchy
    # print_widget_hierarchy(viewer.window._qt_window)
    
    # Wait for viewer to fully initialize and render
    QTimer.singleShot(200, lambda: capture_elements(viewer))
    
    app.exec_()

def capture_elements(viewer):
    """Capture specific UI elements based on the widget hierarchy."""
    qt_window = viewer.window._qt_window
    
    # Main components - using the hierarchy you provided
    viewer_components = {
        "welcome_widget": find_widget_by_class(qt_window, "QtWelcomeWidget"),
        
        "console_dock": find_widget_by_name(qt_window, "console"),
        
        "dimension_slider": find_widget_by_class(qt_window, "QtDims"),
        
        # Layer list components
        "layer_list_dock": find_widget_by_name(qt_window, "layer list"),
        "layer_buttons": find_widget_by_class(qt_window, "QtLayerButtons"),
        "layer_list": find_widget_by_class(qt_window, "QtLayerList"),
        "viewer_buttons": find_widget_by_class(qt_window, "QtViewerButtons"),
        
        # Layer controls
        "layer_controls_dock": find_widget_by_name(qt_window, "layer controls"),
       
        # TODO: mouse over part of the image to show intensity stuff
        "status_bar": viewer.window._status_bar,
    }
    
    # Capture each component
    for name, widget in viewer_components.items():
        capture_widget(widget, name)
    
    menu_components = {
        "file_menu": find_widget_by_name(qt_window, "napari/file"),
        "samples_menu": find_widget_by_name(qt_window, "napari/file/samples/napari"),
        "view_menu": find_widget_by_name(qt_window, "napari/view"),
        "layers_menu": find_widget_by_name(qt_window, "napari/layers"),
        "plugins_menu": find_widget_by_name(qt_window, "napari/plugins"),
        "window_menu": find_widget_by_name(qt_window, "napari/window"),
        "help_menu": find_widget_by_name(qt_window, "napari/help"),
    }

    for name, menu in menu_components.items():
        capture_menu(menu, name)


    viewer_buttons = viewer_components["viewer_buttons"]
    
    popups_configs = [
        {
            "name": "ndisplay_2D_popup",
            "prep": lambda: setattr(viewer.dims, "ndisplay", 2),
            "button": viewer_buttons.ndisplayButton,
        },
        {
            "name": "roll_dims_popup",
            "prep": lambda: setattr(viewer.dims, "ndisplay", 2),
            "button": viewer_buttons.rollDimsButton,
        },
        {
            "name": "ndisplay_3D_popup",
            "prep": lambda: setattr(viewer.dims, "ndisplay", 3),
            "button": viewer_buttons.ndisplayButton,
        },
        {
            "name": "grid_popup",
            "prep": None,
            "button": viewer_buttons.gridViewButton,
        }
    ]

    for config in popups_configs:
        capture_popups(config)
    
    QTimer.singleShot(100, lambda: close_all(viewer))

def capture_popups(config):
    """Capture popups that appear when clicking on viewer buttons."""
    app = get_qapp()
    close_existing_popups()

    if config["prep"] is not None:
        config["prep"]()

    app.processEvents()
    config["button"].customContextMenuRequested.emit(QPoint())
    app.processEvents()
    popups = [w for w in QApplication.topLevelWidgets() if isinstance(w, QtPopup) and w.isVisible()]
    
    if not popups:
        return print(f"No popup found for {config['name']}")

    popup = popups[-1] # grab the most recent popup, just in case
    
    app.processEvents()

    pixmap = popup.grab()
    pixmap.save(str(POPUPS_PATH / f"{config['name']}.png"))
    popup.close()
    app.processEvents()

def capture_widget(widget, name):
    """Capture a widget and save it to a file."""
    if widget is None:
        return print(f"Could not find {name}")

    pixmap = widget.grab()
    pixmap.save(str(WIDGETS_PATH / f"{name}.png"))
    return

def capture_menu(menu, name):
    """Show a menu and take screenshot of it."""
    if menu is None:
        return print(f"Could not find menu {name}")
    
    menu.popup(menu.parent().mapToGlobal(menu.pos()))
    
    # Give menu time to appear
    def grab_menu():
        pixmap = menu.grab()
        pixmap.save(str(MENUS_PATH / f"{name}.png"))
        menu.hide()
    
    QTimer.singleShot(50, grab_menu)
    return

def close_all(viewer):
    viewer.close()
    QTimer.singleShot(100, lambda: get_qapp().quit())

def close_existing_popups():
    """Close any existing popups."""
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QtPopup):
            widget.close()
            
    get_qapp().processEvents()

def find_widget_by_name(parent, name):
    """Find a widget by its object name."""
    if parent.objectName() == name:
        return parent
        
    for child in parent.children():
        if hasattr(child, 'objectName') and child.objectName() == name:
            return child
        
        if hasattr(child, 'children'):
            found = find_widget_by_name(child, name)
            if found:
                return found
    
    return None

def find_widget_by_class(parent, class_name):
    """Find a child widget by its class name."""
    if parent.__class__.__name__ == class_name:
        return parent
        
    for child in parent.children():
        if child.__class__.__name__ == class_name:
            return child
        
        if hasattr(child, 'children'):
            found = find_widget_by_class(child, class_name)
            if found:
                return found
    
    return None


def print_widget_hierarchy(widget, indent=0, max_depth=None):
    """Print a hierarchy of child widgets with their class names and object names."""

    if max_depth is not None and indent > max_depth:
        return
        
    class_name = widget.__class__.__name__
    object_name = widget.objectName()
    name_str = f" (name: '{object_name}')" if object_name else ""
    print(" " * indent + f"- {class_name}{name_str}")
    
    for child in widget.children():
        if hasattr(child, "children"):
            print_widget_hierarchy(child, indent + 4, max_depth)

    
if __name__ == "__main__":
    autogenerate_images()