import os
import numpy as np

from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.external.qt import QtGui

from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import MaskSubsetState

__all__ = ['DendrogramSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when dendrogram selection on large images


class DendrogramSelectionTool(object):

    def __init__(self, widget=None):
        self.widget = widget
        self.data_object = None

    def _get_modes(self, axes):
        self._mode = DendrogramMode(axes,
                                   move_callback=self._dendrogram_roi,
                                   release_callback=self._dendrogram_roi)
        return [self._mode]

    # @set_cursor(Qt.WaitCursor)
    def _dendrogram_roi(self, mode):
        """
        Callback for DendrogramMode.
        """
        if mode._start_event is None or mode._end_event is None:
            return

        # TODO: how to get data from other widges??
        data = self.widget.client.display_data
        att = self.widget.client.display_attribute
        dendro_att = 'structure'

        print('data and att', data, att)

        # assume I got the dendrogram structure here as d
        d = data[dendro_att]  # here is ndarray data

        if data is None or att is None:
            return

        if data.size > WARN_THRESH and not self.widget._confirm_large_image(data):
            return

        # Determine length of dragging action in units relative to the figure
        width, height = mode._start_event.canvas.get_width_height()
        dx = (mode._end_event.x - mode._start_event.x) / width
        dy = (mode._end_event.y - mode._start_event.y) / height
        length = np.hypot(dx, dy)

        # Make sure the coordinates are converted to the nearest integer
        x = int(round(mode._start_event.xdata))
        y = int(round(mode._start_event.ydata))

        if data.ndim == 2:
            start_coord = (y, x)
        else:
            z = int(round(self.widget.client.slice[self.profile_axis]))
            start_coord = (z, y, x)

        # We convert the length in relative figure units to a threshold - we make
        # it so that moving by 0.1 produces a threshold of 1.1, 0.2 -> 2, 0.3 -> 11
        # etc
        threshold = 1 + 10 ** (length / 0.1 - 1)

        # get branch from pos
        branch = d.structure_at(start_coord)
        # TODO: this needs to be iterated
        if threshold > 2:
            branch = branch.parent

        mask = branch.get_mask()
        if mask is not None:
            cids = data.pixel_component_ids
            subset_state = MaskSubsetState(mask, cids)
            mode = EditSubsetMode()
            mode.update(data, subset_state, focus_data=data)

    @property
    def profile_axis(self):
        slc = self.widget.client.slice
        candidates = [i for i, s in enumerate(slc) if s not in ['x', 'y']]
        if len(candidates) == 0:
            return None
        else:
            return max(candidates, key=lambda i: self.widget.client.display_data.shape[i])

    def _display_data_hook(self, data):
        pass

    def close(self):
        pass


class DendrogramMode(MouseMode):
    """
    Select a region of interest with predefined dendrogram structure.
    """

    def __init__(self, *args, **kwargs):

        super(DendrogramMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, "glue_dendrogram.png"))
        self.mode_id = 'Dendrogram'
        self.action_text = 'Dendrogram'
        self.tool_tip = ('Select a region of interest with predefined dendrogram'
                         'structure. Click to define the starting pixel and '
                         'drag (keeping the mouse clicked) to grow the '
                         'selection.')
        self._start_event = None
        self._end_event = None

    def press(self, event):
        self._start_event = event
        super(DendrogramMode, self).press(event)

    def move(self, event):
        self._end_event = event
        super(DendrogramMode, self).move(event)

    def release(self, event):
        self._end_event = event
        super(DendrogramMode, self).release(event)
        self._start_event = None
        self._end_event = None
