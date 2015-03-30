# This plugin requires OpenCV to be installed, and returns a PIL Image object


def setup():

    from .qt_widget import QtWebcamImporter
    from glue.config import importer

    @importer("Import from webcam")
    def webcam_importer():
        wi = QtWebcamImporter()
        wi.exec_()
        return wi.data
