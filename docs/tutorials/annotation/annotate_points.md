(annotating-points)=

# Annotating videos with napari

```{Admonition} DEPRECATED ATTRIBUTES
:class: warning
As of napari 0.5.0, `edge_*` attributes are being renamed to
`border_*` attributes. We have yet to update the images and/or videos in
this tutorial. Please use `border` in place of `edge` for all `Points` attributes moving forward.

The code in this tutorial uses the latest API. Only images and videos may be out of date.
```

**Note**: this tutorial has been updated and is now compatible with napari > 0.4.5 and magicgui > 0.2.5. For details, see [this pull request](https://github.com/napari/napari.github.io/pull/114).

In this tutorial, we will use napari (requires version 0.3.2 or greater) to make a simple GUI application for annotating points in videos.
This GUI could be useful for making annotations required to train algorithms for markless tracking of animals (e.g., [DeepLabCut](http://www.mackenziemathislab.org/deeplabcut)).
In this tutorial, we will cover creating and interacting with a Points layer with features (i.e., labels for the points), connecting custom UI elements to events, and creating custom keybindings.

At the end of this tutorial, we will have created a GUI for annotating points in videos that we can simply call by:

```python
im_path = '<path to directory with data>/*.png'
point_annotator(im_path, labels=['ear_l', 'ear_r', 'tail'])
```

The resulting viewer looks like this (images from [Mathis et al., 2018](https://www.nature.com/articles/s41593-018-0209-y), downloaded from [here](https://github.com/DeepLabCut/DeepLabCut/tree/f21321ef8060c537f9df0ce9346189bda07701b5/examples/openfield-Pranav-2018-10-30/labeled-data/m4s1)):

```{raw} html
<figure>
  <video width="100%" controls autoplay loop muted playsinline>
    <source src="../../_static/images/point_annotator_demo.webm" type="video/webm" />
    <source src="../../_static/images/point_annotator_demo.mp4" type="video/mp4" />
    <img src="../../_static/images/point_annotator_demo.png"
      title="Your browser does not support the video tag"
      alt="Demo of point annotator shows user adding keypoint labels to a video of a mouse, frame by frame. The user navigates the viewer mostly with keyboard shortcuts, and uses the computer mouse to click on keypoints like the mouse's ears and tail."
    >
  </video>
</figure>
```

You can explore the project in [this repository](https://github.com/kevinyamauchi/PointAnnotator) or check out the main function below.
We will walk through the code in the following sections.

```python
from typing import List

from dask_image.imread import imread
from magicgui.widgets import ComboBox, Container
import napari
import pandas as pd

COLOR_CYCLE = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf'
]


def create_label_menu(points_layer, labels):
    """Create a label menu widget that can be added to the napari viewer dock

    Parameters
    ----------
    points_layer : napari.layers.Points
        a napari points layer
    labels : List[str]
        list of the labels for each keypoint to be annotated (e.g., the body parts to be labeled).

    Returns
    -------
    label_menu : Container
        the magicgui Container with our dropdown menu widget
    """
    # Create the label selection menu
    label_menu = ComboBox(label='feature_label', choices=labels)
    label_widget = Container(widgets=[label_menu])


    def update_label_menu(event):
        """Update the label menu when the point selection changes"""
        new_label = str(points_layer.feature_defaults['label'][0])
        if new_label != label_menu.value:
            label_menu.value = new_label

    points_layer.events.feature_defaults.connect(update_label_menu)

    def label_changed(selected_label):
        """Update the Points layer when the label menu selection changes"""
        feature_defaults = points_layer.feature_defaults
        feature_defaults['label'] = selected_label
        points_layer.feature_defaults = feature_defaults
        points_layer.refresh_colors()

    label_menu.changed.connect(label_changed)

    return label_widget


def point_annotator(
        im_path: str,
        labels: List[str],
):
    """Create a GUI for annotating points in a series of images.

    Parameters
    ----------
    im_path : str
        glob-like string for the images to be labeled.
    labels : List[str]
        list of the labels for each keypoint to be annotated (e.g., the body parts to be labeled).
    """
    stack = imread(im_path)

    viewer = napari.view_image(stack)
    points_layer = viewer.add_points(
        ndim=3,
        features=pd.DataFrame({'label': pd.Categorical([], categories=labels)}),
        border_color='label',
        border_color_cycle=COLOR_CYCLE,
        symbol='o',
        face_color='transparent',
        border_width=0.5,  # fraction of point size
        size=12,
    )
    points_layer.border_color_mode = 'cycle'

    # add the label menu widget to the viewer
    label_widget = create_label_menu(points_layer, labels)
    viewer.window.add_dock_widget(label_widget)

    @viewer.bind_key('.')
    def next_label(event=None):
        """Keybinding to advance to the next label with wraparound"""
        feature_defaults = points_layer.feature_defaults
        default_label = feature_defaults['label'][0]
        ind = list(labels).index(default_label)
        new_ind = (ind + 1) % len(labels)
        new_label = labels[new_ind]
        feature_defaults['label'] = new_label
        points_layer.feature_defaults = feature_defaults
        points_layer.refresh_colors()

    def next_on_click(layer, event):
        """Mouse click binding to advance the label when a point is added"""
        if layer.mode == 'add':
            # By default, napari selects the point that was just added.
            # Disable that behavior, as the highlight gets in the way
            # and also causes next_label to change the color of the
            # point that was just added.
            layer.selected_data = set()
            next_label()

    points_layer.mode = 'add'
    points_layer.mouse_drag_callbacks.append(next_on_click)

    @viewer.bind_key(',')
    def prev_label(event):
        """Keybinding to decrement to the previous label with wraparound"""
        feature_defaults = points_layer.feature_defaults
        default_label = feature_defaults['label'][0]
        ind = list(labels).index(default_label)
        n_labels = len(labels)
        new_ind = ((ind - 1) + n_labels) % n_labels
        feature_defaults['label'] = labels[new_ind]
        points_layer.feature_defaults = feature_defaults
        points_layer.refresh_colors()

    napari.run()
```

## `point_annotator()`

We will create the GUI within a function called `point_annotator()`.
Wrapping the GUI creation in the function allows us to integrate it into other functions (e.g., a command line interface) and applications.
See below for the function definition.

```python
def point_annotator(
        im_path: str,
        labels: List[str],
):
    """Create a GUI for annotating points in a series of images.

    Parameters
    ----------
    im_path : str
        glob-like string for the images to be labeled.
    labels : List[str]
        list of the labels for each keypoint to be annotated (e.g., the body parts to be labeled).
    """
```

## Loading the video

First, we load the movie to be annotated.
Since behavior movies can be quite long, we will use a lazy loading strategy (i.e., we will only load the frames as they are used).
Using [`dask-image`](https://github.com/dask/dask-image), we can construct an object that we can pass to napari for lazy loading in just one line.
For more explanation on using dask to lazily load images in napari, see [our Dask tutorial](dask-napari).

```python
stack = imread(im_path)
```

We can then start the viewer.

```python
viewer = napari.view_image(stack)
napari.run()
```

## Annotating with points

We will annotate the features of interest using points in a napari Points layer.
Each feature will be given a different label so that we can track them across frames.
To achieve this, we will store the label in the `Points.features` table in the 'label' column.
We will instantiate the `Points` layer without any points.
However, we will initialize `Points.features` with the feature values we will be using to annotate the images.
To do so, we will define a feature table with a categorical column named `label` with category values from `labels`.
The key, 'label', is the name of the feature we are storing.
The values, 'labels', is the list of the names of the features we will be annotating (defined above in the "point_annotator()" section).

We add the `Points` layer to the viewer using the `viewer.add_points()` method.
As discussed above, we will be storing which feature of interest each point corresponds to via the `label` feature we defined in the `features` table.
To visualize the feature each point represents, we set the border color as a color cycle mapped to the `label` feature (`border_color='label'`).

```python
points_layer = viewer.add_points(
    ndim=3,
    features=pd.DataFrame({'label': pd.Categorical([], categories=labels)}),
    border_color='label',
    border_color_cycle=COLOR_CYCLE,
    symbol='o',
    face_color='transparent',
    border_width=0.5,  # fraction of point size
    size=12,
)
```

Note that we set the `border_color_cycle` to `COLOR_CYCLE`.
You can define your own color cycle as a list of colors.
The colors can be defined as hex strings, standard color names or RGBA arrays.
For example, the [category10 color palette](https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category10) would be:

```python
COLOR_CYCLE = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf'
]
```

We set the points `ndim` to 3 so that the coordinates for the point annotations we add will be 3 dimensional (time + 2D).

Finally, we set the border color to a color cycle:

```python
    points_layer.border_color_mode = 'cycle'
```

## Adding a GUI for selecting points

First, we will define a function  to create a GUI for select the labels for
points. The function `create_label_menu()` will take the points layer we created
and the list of labels we will annotate with and return the label menu GUI.
Additionally, we will create and connect all the required callbacks to make the
GUI interactive.

```python
def create_label_menu(points_layer, labels):
    """Create a label menu widget that can be added to the napari viewer dock

    Parameters
    -----------
    points_layer : napari.layers.Points
        a napari points layer
    labels : List[str]
        list of the labels for each keypoint to be annotated (e.g., the body parts to be labeled).

    Returns
    --------
    label_menu : Container
        the magicgui Container with our dropdown menu widget
    """
```

Within `create_label_menu()`, we will use magicgui to add a dropdown menu for selecting which the label for the point we are about to add or the point we have selected.
[magicgui](https://github.com/napari/magicgui) is a library from the napari team for building GUIs from functions and works by applying function decorators.
To make the a dropdown menu populated with the valid point labels, we simply create a magicgui `ComboBox`. We set the label (title) for the `ComboBox` with the `label` keyword argument and we set the dropdown menu options via the `choices` keyword argument. Recall that the labels names are passed to the `create_label_menu()` function as a list via the `labels` parameter. Next, we wrap the `label_menu` in a magicgui `Container` to finish our GUI widget.

```python
# Create the label selection menu
label_menu = ComboBox(label='feature_label', choices=labels)
label_widget = Container(widgets=[label_menu])
```

We then need to connect the dropdown menu (`label_menu`) to the points layer to ensure the menu selection is always synchronized to the `Points` layer model.

First, we define a function to update the label dropdown menu GUI when the value of the selected point or next point to be added is changed.
On the points layer, the feature values of the next point to be added are stored in the `feature_defaults` property.
The points layer has an event that gets emitted when the `feature_defaults` property is changed (`points_layer.events.feature_defaults`).
We connect the function we created to the event so that `update_label_menu()` is called whenever `Points.feature_defaults` is changed.

```python
def update_label_menu(event):
    """Update the label menu when the point selection changes"""
    new_label = str(points_layer.feature_defaults['label'][0])
    if new_label != label_menu.value:
        label_menu.value = new_label

points_layer.events.feature_defaults.connect(update_label_menu)
```

Next, we define a function to update the points layer if the selection in the labels dropdown menu is changed.
Similar to the points layer, the magicgui object has an event that gets emitted whenever the selected label is changed (`label_menu.changed`).
To ensure the points layer is updated whenever the GUI selection is changed, we connect `label_changed()` to the `label_menu.changed` event.

```python
def label_changed(selected_label):
    """Update the Points layer when the label menu selection changes"""
    feature_defaults = points_layer.feature_defaults
    feature_defaults['label'] = selected_label
    points_layer.feature_defaults = feature_defaults
    points_layer.refresh_colors()

label_menu.changed.connect(label_changed)
```

Finally, we add the GUI created by magicgui to the napari viewer dock.

```python
# add the label menu widget to the viewer
label_widget = create_label_menu(points_layer, labels)
viewer.window.add_dock_widget(label_widget)
```

## Keybindings for switching labels

For convenience, we can also define functions to increment and decrement the currently selected label and bind them to key presses using the napari keybindings framework.

First, we define a function to increment to the next label and decorate it with the viewer key binding decorator.
The decorator requires that we pass the key to bind the function to as a string and the decorated function should take an event as an input argument.
In this case, we are binding `next_label()` to the {kbd}`.` key.

```python
@viewer.bind_key('.')
def next_label(event=None):
    """Keybinding to advance to the next label with wraparound"""
    feature_defaults = points_layer.feature_defaults
    default_label = feature_defaults['label'][0]
    ind = list(labels).index(default_label)
    new_ind = (ind + 1) % len(labels)
    new_label = labels[new_ind]
    feature_defaults['label'] = new_label
    points_layer.feature_defaults = feature_defaults
    points_layer.refresh_colors()
```

We can do the same with another function that instead decrements the label with wraparound.

```python
@viewer.bind_key(',')
def prev_label(event):
    """Keybinding to decrement to the previous label with wraparound"""
    feature_defaults = points_layer.feature_defaults
    default_label = feature_defaults['label'][0]
    ind = list(labels).index(default_label)
    n_labels = len(labels)
    new_ind = ((ind - 1) + n_labels) % n_labels
    feature_defaults['label'] = labels[new_ind]
    points_layer.feature_defaults = feature_defaults
    points_layer.refresh_colors()
```

## Mousebinding to iterate through labels

Like keybindings, we can also bind functions to mouse events such as clicking or dragging.
Here, we create a function that will increment the label after a point is added (i.e., the mouse is clicked in the viewer canvas when in the point adding mode).
This is convenient for quickly adding all labels to a frame, as one can simply click each feature in order without having to manually swap labels.
To achieve this, we first check if the points layer is the the adding mode (`layer.mode == 'add'`).
If so, we then reuse the `next_label()` function we defined above in the keybindings to increment the label.
Finally,

```python
def next_on_click(layer, event):
    """Mouse click binding to advance the label when a point is added"""
    if layer.mode == 'add':
        # By default, napari selects the point that was just added.
        # Disable that behavior, as the highlight gets in the way
        # and also causes next_label to change the color of the
        # point that was just added.
        layer.selected_data = set()
        next_label()
```

After creating the function, we then add it to the `points_layer` mouse drag callbacks.
In napari, clicking and dragging events are both handled under the `mouse_drag_callbacks`.
For more details on how mouse event callbacks work,
see the examples [[1](https://github.com/napari/napari/blob/main/examples/custom_mouse_functions.py), [2](https://github.com/napari/napari/blob/main/examples/mouse_drag_callback.py)].

```python
# bind the callback to the mouse drag event
points_layer.mouse_drag_callbacks.append(next_on_click)
```

## Using the GUI

### Launching the GUI

Now that you've put it all together, you should be ready to test! You can call the function as shown below.

```python
im_path = '<path to directory with data>/*.png'

point_annotator(im_path, labels=['ear_l', 'ear_r', 'tail'])
```

### Saving the annotations

Once we are happy with the annotations, we can save them to a CSV file using the building CSV writer for the points layer.
To do so, first, select the "Points" layer in the layer list and then click "Save Selected layer(s)"  in the "File" menu or press {kbd}`control+S` ({kbd}`cmd+S` on Mac OS)  to bring up the file save dialog.
From here you can enter the file path and save the annotation coordinates as a CSV.

![Viewer with green box around a points layer in layer list. Label in green says "1. Select Points layer in the layer list". Dialog in the middle of the viewer has options to add save file name and choose save location, with Cancel and Save buttons in the bottom right.](../../_static/images/points_save_dialog.png)

Alternatively, we can use the `points_layer.save()` method to save the coordinates from the points layer to a CSV file.
We can enter the command either in the script (e.g., bind a save function to a hot key) or the napari terminal.

```python
points_layer.save('path/to/file.csv')
```
