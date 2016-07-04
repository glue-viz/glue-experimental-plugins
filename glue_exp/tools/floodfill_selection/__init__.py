def setup():

    from glue.logger import logger
    from glue.config import tool_registry
    from glue.viewers.image.qt import ImageWidget

    from .floodfill_selection import FloodfillSelectionTool

    tool_registry.add(FloodfillSelectionTool, widget_cls=ImageWidget)

    logger.info("Loaded VizieR importer plugin")
