def setup():
    from glue.viewers.image.qt import ImageViewer
    from .zoom_buttons import ZoomInTool, ZoomOutTool  # noqa
    ImageViewer.tools.append('Zoom In')
    ImageViewer.tools.append('Zoom Out')
