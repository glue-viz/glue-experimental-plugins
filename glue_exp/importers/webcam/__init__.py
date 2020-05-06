# This plugin requires OpenCV to be installed, and returns a PIL Image object


def setup():

    from glue.logger import logger
    try:
        import cv2  # noqa
    except ImportError:
        logger.info("Could not load webcam importer plugin, since OpenCV is required")
        return

    from glue.config import importer
    from .qt_widget import QtWebcamImporter

    @importer("Import from webcam")
    def webcam_importer():
        wi = QtWebcamImporter()
        wi.exec_()
        return wi.data

    logger.info("Loaded webcam importer plugin")
