def setup():

    from glue.viewers.image.qt import ImageWidget

    from .contour_selection import ContourSelectionTool

    try:
        from glue.config import tool_registry
    except ImportError:  # glue >= 0.9
        ImageWidget.tools.append('Contour selection')
    else:
        tool_registry.add(ContourSelectionTool, widget_cls=ImageWidget)
