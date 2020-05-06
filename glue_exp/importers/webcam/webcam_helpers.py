import cv2

from glue.core import Data


class Webcam(object):

    def __init__(self):
        self._capture = cv2.VideoCapture(0)

    def capture_frame(self):
        ret, frame = self._capture.read()
        return frame


def frame_to_data(frame):
    data = Data(red=frame[::-1, ::-1, 2],
                green=frame[::-1, ::-1, 1],
                blue=frame[::-1, ::-1, 0])
    data.label = "Webcam Snapshot"
    return data
