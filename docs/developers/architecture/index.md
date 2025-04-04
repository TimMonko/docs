(architecture-index)=

# napari architecture guide

These pages provide a guide to the napari software architecture
and is aimed at contributors who would like a better understanding of the napari
code base. For advanced napari usage documentation, see [](explanations).

- [](napari-directory-organization): Guide to the napari directory organization.
- [](ui-sections): Explains how napari GUI sections map to the napari source code
directory organization.
- [](napari-model-event): Explains napari python models and how they are
  connected to Qt classes and Vispy classes.
- [](app-model): Explains the napari application model, a declarative schema for
  keeping track of commands, menus and keybindings of the napari GUI.
- [](magicgui_type_registration): Explains how `magicgui` widgets declared by users
  or plugins are automatically created, inputs updated and outputs added to the
  `Viewer` for registered `napari` types.