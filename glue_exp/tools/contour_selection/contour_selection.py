import os

from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.core import roi

try:
    from glue.utils.matplotlib import point_contour
except ImportError:  # glue < 0.5
    from glue.core.util import point_contour

try:
    from glue.config import viewer_tool
    GLUE_LT_09 = False
except ImportError:  # Compatibility with glue < 0.9
    def viewer_tool(x):
        return x
    GLUE_LT_09 = True

__all__ = ['ContourSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when contouring large images


@viewer_tool
class ContourSelectionTool(MouseMode):
    """
    Creates ROIs by using the mouse to 'pick' contours out of the data
    """
    
    icon = os.path.join(ROOT, "glue_contour.png")
    tool_id = 'Contour selection'
    action_text = 'Contour'
    tool_tip = 'Define a region of interest via contours'
    shortcut = 'N'

    def __init__(self, *args, **kwargs):
        super(ContourSelectionTool, self).__init__(*args, **kwargs)        
        self._release_callback = self._contour_roi
        if GLUE_LT_09:
            try:
                from glue.external.qt import QtGui
            except:
                from qtpy import QtGui
            self.icon = QtGui.QIcon(os.path.join(ROOT, "glue_contour.png"))
            self.mode_id = 'Contour selection'
            self.action_text = 'Contour'
            self.tool_tip = 'Define a region of interest via contours'
            self.shortcut = 'N'
            self.viewer = args[0]

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

    def _contour_roi(self, mode):
        """ Callback for ContourSelectionTool. Set edit_subset as new ROI """
        im = self.viewer.client.display_data
        att = self.viewer.client.display_attribute

        if im is None or att is None:
            return
        if im.size > WARN_THRESH and not self.viewer._confirm_large_image(im):
            return
        roi = mode.roi(im[att])

        if roi:
            self.viewer.apply_roi(roi)

    # TODO: the following three methods are for backward-compatibility with 
    #       glue < 0.9, and can be removed once we support only glue >= 0.9.

    def _display_data_hook(self, data):
        pass

    def _get_modes(self, axes):
        return [self]

    def close(self):
        pass


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

    xy = point_contour(x, y, data)
    if xy is None:
        return None

    p = roi.PolygonalROI(vx=xy[:, 0], vy=xy[:, 1])
    return p
