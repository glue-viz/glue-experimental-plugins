def setup():

    from glue.viewers.image.qt import ImageWidget
    from .zoom_buttons import ZoomInTool, ZoomOutTool  # noqa

    # glue >= 0.9
    ImageWidget.tools.append('Zoom In')
    ImageWidget.tools.append('Zoom Out')
