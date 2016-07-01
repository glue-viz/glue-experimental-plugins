import os

from glue.qt.mouse_mode import MouseMode
from glue.core import roi
from glue.external.qt import QtGui


__all__ = ['FloodfillSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when contouring large images


class FloodfillSelectionTool(object):

    def __init__(self, widget=None):
        self.widget = widget

    def _get_modes(self, axes):
        self._path = FloodfillMode(axes, release_callback=self._floodfill_roi)
        return [self._path]

    # @set_cursor(Qt.WaitCursor)
    def _floodfill_roi(self, mode):
        """ Callback for ContourMode. Set edit_subset as new ROI """
        im = self.widget.client.display_data
        att = self.widget.client.display_attribute

        if im is None or att is None:
            return
        if im.size > WARN_THRESH and not self._confirm_large_image(im):
            return

        roi = mode.roi(im[att])
        if roi:
            self.widget.apply_roi(roi)

    def _display_data_hook(self, data):
        pass

    def close(self):
        pass


class FloodfillMode(MouseMode):
    """
    Creates ROIs by using the mouse to 'pick' contours out of the data
    """

    def __init__(self, *args, **kwargs):

        super(FloodfillMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, "flood_fill.png"))
        self.mode_id = 'Floodfill'
        self.action_text = 'Floodfill'
        self.tool_tip = 'Define a region of intrest via floodfill'
        self.shortcut = 'F'

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
        return floodfill_to_roi(x, y, data)


def floodfill_to_roi(x, y, data):
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

    # xy = point_contour(x, y, data)

    # TODO: replace it with floodfill function, xy as the cursor pos,
    # and return a 3D selected region but on current slice as xy

    if xy is None:
        return None

    p = roi.PolygonalROI(vx=xy[:, 0], vy=xy[:, 1])
    return p
