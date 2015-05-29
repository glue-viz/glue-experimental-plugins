def setup():

    from .qt_widget import CategoricalReorder
    from glue.config import menubar_plugin

    @menubar_plugin("Re-order categorical components")
    def reorderer(session, data_collection):
        wi = CategoricalReorder(session=session, data_collection=data_collection)
        wi.exec_()

    from glue.logger import logger
    logger.info("Loaded categorical reorderer importer plugin")
