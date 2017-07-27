def setup():
    from glue.viewers.image.qt import ImageViewer
    from .floodfill_selection import FloodfillSelectionTool  # noqa
    ImageViewer.tools.append('Flood fill')
