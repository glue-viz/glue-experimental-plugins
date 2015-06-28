import os

from glue.qt.mouse_mode import MouseMode
from glue.qt.qtutil import get_icon
from glue.core import util, roi
from glue.external.qt import QtGui

ROOT = os.path.dirname(__file__)

class ContourMode(MouseMode):
    """
    Creates ROIs by using the mouse to 'pick' contours out of the data
    """

    def __init__(self, *args, **kwargs):

        super(ContourMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, "glue_contour.png"))
        self.mode_id = 'Contour'
        self.action_text = 'Contour'
        self.tool_tip = 'Define a region of intrest via contours'
        self.shortcut = 'N'

    def roi(self, data):
        """Caculate an ROI as the contour which passes through the mouse

        Parameters
        ----------
        data : `numpy.ndarray`
            The dataset to use

        Returns
        -------
        :class:`~glue.core.roi.PolygonalROI` or `None`
            A new ROI made by the (single) contour that passes through the
            mouse location (and `None` if this could not be calculated)
        """
        x, y = self._event_xdata, self._event_ydata
        return contour_to_roi(x, y, data)


def contour_to_roi(x, y, data):
    """
    Return a PolygonalROI for the contour that passes through (x,y) in data

    Parameters
    ----------
    x, y : float
        x and y coordinate of the point
    data : `numpy.ndarray`
        The data

    Returns
    -------
    :class:`~glue.core.roi.PolygonalROI`
        A new ROI made by the (single) contour that passes through the
        mouse location (and `None` if this could not be calculated)
    """

    if x is None or y is None:
        return None

    xy = util.point_contour(x, y, data)
    if xy is None:
        return None

    p = roi.PolygonalROI(vx=xy[:, 0], vy=xy[:, 1])
    return p
