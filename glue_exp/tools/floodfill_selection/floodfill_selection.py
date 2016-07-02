import os
import numpy as np

from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.core import roi
from glue.external.qt import QtGui

from .floodfill_scipy import floodfill_scipy

from glue.core.exceptions import IncompatibleAttribute
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import ElementSubsetState

__all__ = ['FloodfillSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when floodfilling large images


# Copy from glue_vispy_viewers/common/toolbar
class PatchedElementSubsetState(ElementSubsetState):

    # TODO: apply this patch to the core glue code

    def __init__(self, data, indices):
        super(PatchedElementSubsetState, self).__init__(indices=indices)
        self._data = data

    def to_mask(self, data, view=None):
        if data in self._data:
            return super(PatchedElementSubsetState, self).to_mask(data, view=view)
        else:
            # TODO: should really be IncompatibleDataException but many other
            # viewers don't recognize this.
            raise IncompatibleAttribute()

    def copy(self):
        return PatchedElementSubsetState(self._data, self._indices)


class FloodfillSelectionTool(object):

    def __init__(self, widget=None):
        self.widget = widget
        self.data_object = None

    def _get_modes(self, axes):
        self._path = FloodfillMode(axes, release_callback=self._floodfill_roi)
        return [self._path]

    # @set_cursor(Qt.WaitCursor)
    def _floodfill_roi(self, mode):
        """ Callback for FloodfillMode. Set edit_subset as new ROI """
        im = self.widget.client.display_data
        self.data_object = im
        print('what is client display_data', self.widget.client.display_data)
        att = self.widget.client.display_attribute

        if im is None or att is None:
            return
        if im.size > WARN_THRESH and not self.widget._confirm_large_image(im):
            return
        slc = self.widget.client.slice

        roi = mode.roi(im[att], slc[self.profile_axis], self.data_object)
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
        print('icon load!')

    # def move(self, event):

    def roi(self, data, slc, data_object):
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

        x, y = self._event_xdata, self._event_ydata
        slc = slc
        return floodfill_to_roi(x, y, data, slc, data_object)


def floodfill_to_roi(x, y, data, slc, data_object):
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
# TODO: replace
#     xy = point_floodfill(x, y, data)
    # calculate the threshold and call draw visual
    # width = event.pos[0] - self.selection_origin[0]
    # height = event.pos[1] - self.selection_origin[1]
    # drag_distance = math.sqrt(width**2+height**2)
    # canvas_diag = math.sqrt(self._vispy_widget.canvas.size[0]**2
    #                         + self._vispy_widget.canvas.size[1]**2)

    # mask = self.draw_floodfill_visual(drag_distance / canvas_diag)
    formate_data = np.asarray(data, np.float64)
    z = slc
    threshold = 8.
    print('x, y, z', x, y, z)
    # coordinate should be integers as index for array
    mask = floodfill_scipy(formate_data, (z, int(round(y)), int(round(x))), threshold).astype(float) * 5

    if mask is not None:
        new_mask = np.reshape(mask, data.shape)
        new_mask = np.ravel(np.transpose(new_mask))
        print('new_mask', np.sum(new_mask))
        mark_selected(new_mask, data, data_object)
    # if xy is None:
    #     return None

    # p = roi.PolygonalROI(vx=xy[:, 0], vy=xy[:, 1])
    # return p


def mark_selected(mask, visible_data, data_object):
    # We now make a subset state(description for selection). For scatter plots
    # we'll want to use an ElementSubsetState, while for cubes, we'll need to
    # change to a MaskSubsetState.
    subset_state = PatchedElementSubsetState(visible_data, np.where(mask)[0])

    # We now check what the selection mode is, and update the selection as
    # needed (this is delegated to the correct subset mode).
    mode = EditSubsetMode()
    focus = visible_data[0] if len(visible_data) > 0 else None
    # mode.update(self._data_collection, subset_state, focus_data=focus)
    print('input for mark_selected', data_object, subset_state, focus)
    mode.update(data_object, subset_state, focus_data=focus)
