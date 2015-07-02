def setup():

    from glue.logger import logger
    from glue.config import tool_registry
    from glue.qt.widgets.image_widget import ImageWidget

    from .contour_selection import ContourSelectionTool

    tool_registry.add(ContourSelectionTool, widget_cls=ImageWidget)

    logger.info("Loaded VizieR importer plugin")
