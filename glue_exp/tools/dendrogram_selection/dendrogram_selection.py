import os
import numpy as np
import numpy.ma as ma

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

        # data['structure'] is a mask of data for each pixel with dendrogram labels
        # d['parent'] gives parent info of each branch
        # -> d['parent'][2] = 5 means branch2 parent is branch 5
        # -> d['parent'][5] = 7 means branch 5 parent is branch 7
        # ...
        """
        if mode._start_event is None or mode._end_event is None:
            return

        data = self.widget.client.display_data
        att = self.widget.client.display_attribute
        d = None
        for each_data in self.widget.client.data:
            if each_data.label == 'Dendrogram':
                d = each_data
                # TODO: 1) the tool icon doesn't show if no dendrogram data
                      # 2) more than one dendrogram data

        if data is None or att is None or d is None:
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

        try:
            branch_label = data['structure'][start_coord]
        except IndexError:
            # if selection pos out of data range
            branch_label = -1

        # no structure found
        if branch_label == -1:
            return None

        # find parent structure when dragging
        while threshold/10. > 1:
            threshold /= 10.
            branch_label = d['parent'][branch_label]

        # similar to DFS to find children
        def get_all_branch(d, branch_label, ini_mask):
            mask = np.logical_or(ini_mask, data['structure'] == branch_label)
            child_label = np.where(d['parent'] == branch_label)

            if len(child_label[0]) != 0:
                for each_child in child_label[0]:
                    mask = get_all_branch(d, each_child, mask)
            return mask

        ini_mask = np.zeros(data['structure'].shape, dtype=bool)
        mask = get_all_branch(d, branch_label, ini_mask)

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
