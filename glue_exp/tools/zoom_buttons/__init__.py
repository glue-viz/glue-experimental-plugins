def setup():

    from glue.logger import logger
    from glue.config import tool_registry
    from glue.viewers.image.qt import ImageWidget

    from .zoom_buttons import ZoomButtonsTool

    tool_registry.add(ZoomButtonsTool, widget_cls=ImageWidget)

    logger.info('Loaded Zoom buttons plugin')
