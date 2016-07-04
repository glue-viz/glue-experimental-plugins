import os
import numpy as np

from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.external.qt import QtGui

from .floodfill_scipy import floodfill_scipy

from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import MaskSubsetState

__all__ = ['FloodfillSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when floodfilling large images


class FloodfillSelectionTool(object):

    def __init__(self, widget=None):
        self.widget = widget
        self.data_object = None

    def _get_modes(self, axes):
        self._path = FloodfillMode(axes, move_callback=self._floodfill_roi, release_callback=self._floodfill_roi)
        return [self._path]

    # @set_cursor(Qt.WaitCursor)
    def _floodfill_roi(self, mode):
        """ Callback for FloodfillMode. Set edit_subset as new ROI """

        if mode._start_event is None or mode._end_event is None:
            return

        # Determine length of drag
        width, height = mode._start_event.canvas.get_width_height()
        dx = (mode._end_event.x - mode._start_event.x) / width
        dy = (mode._end_event.y - mode._start_event.y) / height
        length = np.hypot(dx, dy)

        im = self.widget.client.display_data
        self.data_object = im
        att = self.widget.client.display_attribute

        if im is None or att is None:
            return
        if im.size > WARN_THRESH and not self.widget._confirm_large_image(im):
            return
        slc = self.widget.client.slice

        roi = mode.roi(im[att], slc[self.profile_axis], self.data_object, length)
        if roi:
            self.widget.apply_roi(roi)

    @property
    def profile_axis(self):
        # XXX make this settable
        # defaults to the non-xy axis with the most channels
        slc = self.widget.client.slice
        # TODO: slice update function
        candidates = [i for i, s in enumerate(slc) if s not in ['x', 'y']]

        return max(candidates, key=lambda i: self.widget.client.display_data.shape[i])

    def _display_data_hook(self, data):
        pass

    def close(self):
        pass


class FloodfillMode(MouseMode):
    """
    Creates ROIs by using the mouse to 'pick' floodfills out of the data
    """

    def __init__(self, *args, **kwargs):

        super(FloodfillMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, "glue_floodfill.png"))
        self.mode_id = 'Floodfill'
        self.action_text = 'Floodfill'
        self.tool_tip = 'Define a region of intrest via floodfills'
        self.shortcut = 'N'

    def press(self, event):
        self._start_event = event
        super(FloodfillMode, self).press(event)

    def move(self, event):
        self._end_event = event
        super(FloodfillMode, self).move(event)

    def release(self, event):
        self._end_event = event
        super(FloodfillMode, self).release(event)
        self._start_event = None
        self._end_event = None

    def roi(self, data, slc, data_object, length):
        """Caculate an ROI as the floodfill which passes through the mouse

        Parameters
        ----------
        data : `numpy.ndarray`
            The dataset to use

        Returns
        -------
        :class:`~glue.core.roi.PolygonalROI` or `None`
            A new ROI made by the (single) floodfill that passes through the
            mouse location (and `None` if this could not be calculated)
        """
        # here the xy refers to the x and y related to the order of left panel
        x, y = self._start_event.xdata, self._start_event.ydata
        slc = slc
        return floodfill_to_roi(x, y, data, slc, data_object, length)


def floodfill_to_roi(x, y, data, slc, data_object, length):
    """
    Return a PolygonalROI for the floodfill that passes through (x,y) in data

    Parameters
    ----------
    x, y : float
        x and y coordinate of the point
    data : `numpy.ndarray`
        The data

    Returns
    -------
    :class:`~glue.core.roi.PolygonalROI`
        A new ROI made by the (single) floodfill that passes through the
        mouse location (and `None` if this could not be calculated)
    """

    if x is None or y is None:
        return None

    formate_data = np.asarray(data, np.float64)
    z = slc

    # We convert the length in relative figure units to a threshold - we make
    # it so that moving by 0.1 produces a threshold of 1.1, 0.2 -> 2, 0.3 -> 11
    # etc
    threshold = 1 + 10 ** (length / 0.1 - 2)

    # coordinate should be integers as index for array
    mask = floodfill_scipy(formate_data, (z, int(round(y)), int(round(x))), threshold)

    if mask is not None:
        cids = data_object.pixel_component_ids
        subset_state = MaskSubsetState(mask, cids)
        mode = EditSubsetMode()
        mode.update(data_object, subset_state, focus_data=data_object)
