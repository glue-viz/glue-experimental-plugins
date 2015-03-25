# This plugin requires OpenCV to be installed, and returns a PIL Image object

import os
import sys

import cv2
from PIL import Image

from PyQt4.QtCore import QTimer, QRect
from PyQt4.QtGui import QDialog, QApplication, QPainter, QWidget, QImage
from PyQt4.uic import loadUi


UI_FILE = os.path.join(os.path.dirname(__file__), 'webcam.ui')

class WebcamView(QWidget):

    def __init__(self, parent=None):

        super(QWidget, self).__init__()

        self._frozen = False

        self._init_webcam()

        self._update_image()

        self._timer = QTimer(self)
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

        painter = QPainter(self)
        painter.drawImage(QRect(xmin, ymin, width, height), self._image)

    def _init_webcam(self):
        self._capture = cv2.VideoCapture(0)

    def _get_frame(self):
        ret, frame = self._capture.read()
        return frame

    def _get_qimage(self):
        frame = self._get_frame()
        image = QImage(frame.tostring(), frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
        return image, frame

    def _update_image(self):
        if not self._frozen:
            self._image, self._frame = self._get_qimage()
            self.update()


class WebcamImporter(QDialog):

    def __init__(self):
        super(WebcamImporter, self).__init__()
        self.pil_image = None
        self.ui = loadUi(UI_FILE, self)
        self._webcam_preview = WebcamView()
        self.image.addWidget(self._webcam_preview)
        self.capture.clicked.connect(self.flip_capture_button)
        self.cancel.clicked.connect(self.reject)
        self.ok.clicked.connect(self.finalize)
        self.ok.setEnabled(False)
        self.capture.setDefault(True)

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
        self.pil_image = Image.fromarray(self._webcam_preview._frame[:,:,::-1])
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create an application object
    wi = WebcamImporter()
    wi.show()
    app.exec_()
    wi.pil_image.save('test.png')
