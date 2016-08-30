def setup():

    from glue.viewers.image.qt import ImageWidget

    from .floodfill_selection import FloodfillSelectionTool

    try:
        from glue.config import tool_registry
    except ImportError:  # glue >= 0.9
        ImageWidget.tools.append('Flood fill')
    else:
        tool_registry.add(FloodfillSelectionTool, widget_cls=ImageWidget)
