def setup():
    from glue.viewers.image.qt import ImageViewer
    from .contour_selection import ContourSelectionTool  # noqa
    ImageViewer.tools.append('Contour selection')
