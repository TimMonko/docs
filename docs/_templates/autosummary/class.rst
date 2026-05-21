{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

{% if objname == "ArrayBase" %}
.. autodata:: {{ objname }}
{% elif objname == "nbscreenshot" %}
.. autoclass:: napari.utils.notebook_display.NotebookScreenshot
   :members:
   :show-inheritance:
{% else %}
{% set visible_methods = methods | public_members -%}
{% set visible_attributes = attributes | autosummary_attributes(name, module) -%}
.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   {#- These classes inherit docstrings from the raw qt source, which generates rst syntax errors when building the docs #}
{%- if objname not in ["progress", "cancelable_progress"] %}
   :inherited-members:
{%- endif %}
{%- block methods %}
{%- if visible_methods %}

   .. rubric:: {{ _('Methods') }}

   .. autosummary::
{%- for item in visible_methods %}
      ~{{ name }}.{{ item }}
{%- endfor %}
{%- endif %}
{%- endblock %}
{%- block attributes %}
{%- if visible_attributes %}

   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
{%- for item in visible_attributes %}
      {{ item }}
{%- endfor %}
{%- endif %}
{%- endblock %}

   .. rubric:: {{ _('Details') }}
{% endif %}
