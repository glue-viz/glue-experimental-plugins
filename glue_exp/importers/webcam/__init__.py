# This plugin requires OpenCV to be installed, and returns a PIL Image object


def setup():

    from .qt_widget import QtWebcamImporter
    from glue.config import importer
    from glue.core import Data

    @importer("Import from webcam")
    def webcam_importer():
        wi = QtWebcamImporter()
        wi.exec_()
        if wi.image_data is None:
            return []
        else:
            data = Data(red=wi.image_data[::-1,::-1,0],
                         green=wi.image_data[::-1,::-1,1],
                         blue=wi.image_data[::-1,::-1,2])
            data.label = "Webcam Snapshot"
            return [data]
