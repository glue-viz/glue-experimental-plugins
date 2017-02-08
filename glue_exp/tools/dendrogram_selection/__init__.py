def setup():

    from glue.logger import logger
    from glue.config import tool_registry
    from glue.viewers.image.qt import ImageWidget

    from .dendrogram_selection import DendrogramSelectionTool

    tool_registry.add(DendrogramSelectionTool, widget_cls=ImageWidget)
    print('dendrogram loaded')

    logger.info("Loaded VizieR importer plugin dendrogram selection")