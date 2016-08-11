import os

try:
    from glue.external.qt import QtGui, QtCore
except ImportError:
    from qtpy import QtGui, QtCore

from glue.utils.qt.helpers import load_ui

from .webcam_helpers import Webcam, frame_to_data

UI_FILE = os.path.join(os.path.dirname(__file__), 'webcam.ui')


class WebcamView(QtGui.QWidget):

    def __init__(self, parent=None):

        super(WebcamView, self).__init__()

        self._frozen = False

        self._webcam = Webcam()

        self._update_image()

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_image)
        self._timer.start(100)

    def freeze(self):
        self._frozen = True

    def resume(self):
        self._frozen = False

    def paintEvent(self, event):

        # We need to preserve aspect ratio. Figure out bounding box for
        # webcam image.

        im_dx = self._image.width()
        im_dy = self._image.height()
        im_ratio = im_dx / float(im_dy)

        wi_dx = self.width()
        wi_dy = self.height()
        wi_ratio = wi_dx / float(wi_dy)

        if wi_ratio > im_ratio:  # Need to pad on sides

            xmin = wi_dx / 2. - wi_dy / 2. * im_ratio
            ymin = 0.
            width = wi_dy * im_ratio
            height = wi_dy

        else:  # Need to pad on top/bottom

            xmin = 0.
            ymin = wi_dy / 2. - wi_dx / 2. / float(im_ratio)
            width = wi_dx
            height = wi_dx / float(im_ratio)

        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QRect(xmin, ymin, width, height), self._image)


    def _update_image(self):
        if not self._frozen:
            frame = self._webcam.capture_frame()
            self._image = QtGui.QImage(frame.tostring(), frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self._data = frame_to_data(frame)
            self.update()


class QtWebcamImporter(QtGui.QDialog):

    def __init__(self):
        super(QtWebcamImporter, self).__init__()
        self.pil_image = None
        self.ui = load_ui(UI_FILE, self)
        self._webcam_preview = WebcamView()
        self.image.addWidget(self._webcam_preview)
        self.capture.clicked.connect(self.flip_capture_button)
        self.cancel.clicked.connect(self.reject)
        self.ok.clicked.connect(self.finalize)
        self.ok.setEnabled(False)
        self.capture.setDefault(True)
        self.data = []

    def flip_capture_button(self):
        if self._webcam_preview._frozen:
            self._webcam_preview.resume()
            self.capture.setText("Capture")
            self.capture.setDefault(True)
            self.ok.setEnabled(False)
        else:
            self._webcam_preview.freeze()
            self.capture.setText("Try again")
            self.capture.setDefault(False)
            self.ok.setEnabled(True)
            self.ok.setDefault(True)

    def finalize(self):
        self.data = [self._webcam_preview._data]
        self.accept()
