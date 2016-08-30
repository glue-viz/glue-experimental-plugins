import os
import numpy as np

from glue.viewers.common.qt.mouse_mode import MouseMode
from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import MaskSubsetState

from .floodfill_scipy import floodfill_scipy

try:
    from glue.config import viewer_tool
    GLUE_LT_09 = False
except ImportError:  # Compatibility with glue < 0.9
    def viewer_tool(x):
        return x
    GLUE_LT_09 = True

__all__ = ['FloodfillSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 1000000000000  # warn when floodfilling large images


@viewer_tool
class FloodfillSelectionTool(MouseMode):
    """
    Creates selection by using the mouse to pick regions using the flood fill
    algorithm: https://en.wikipedia.org/wiki/Flood_fill
    """

    icon = os.path.join(ROOT, "glue_floodfill.png")
    tool_id = 'Flood fill'
    action_text = 'Flood fill'
    tool_tip = ('Define a region of interest with the flood fill '
                'algorithm. Click to define the starting pixel and '
                'drag (keeping the mouse clicked) to grow the '
                'selection.')

    def __init__(self, *args, **kwargs):

        super(FloodfillSelectionTool, self).__init__(*args, **kwargs)

        self._start_event = None
        self._end_event = None

        self._move_callback = self._floodfill_roi
        self._release_callback = self._floodfill_roi

        if GLUE_LT_09:
            try:
                from glue.external.qt import QtGui
            except:
                from qtpy import QtGui
            self.icon = QtGui.QIcon(os.path.join(ROOT, "glue_floodfill.png"))
            self.mode_id = 'Flood fill'
            self.action_text = 'Flood fill'
            self.tool_tip = ('Define a region of interest with the flood fill '
                             'algorithm. Click to define the starting pixel and '
                             'drag (keeping the mouse clicked) to grow the '
                             'selection.')
            self.viewer = args[0]


    def press(self, event):
        self._start_event = event
        super(FloodfillSelectionTool, self).press(event)

    def move(self, event):
        self._end_event = event
        super(FloodfillSelectionTool, self).move(event)

    def release(self, event):
        self._end_event = event
        super(FloodfillSelectionTool, self).release(event)
        self._start_event = None
        self._end_event = None

    def _floodfill_roi(self, mode):
        """
        Callback for FloodfillSelectionTool.
        """

        if mode._start_event is None or mode._end_event is None:
            return

        data = self.viewer.client.display_data
        att = self.viewer.client.display_attribute

        if data is None or att is None:
            return

        if data.size > WARN_THRESH and not self.viewer._confirm_large_image(data):
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
            z = int(round(self.viewer.client.slice[self.profile_axis]))
            start_coord = (z, y, x)

        # We convert the length in relative figure units to a threshold - we make
        # it so that moving by 0.1 produces a threshold of 1.1, 0.2 -> 2, 0.3 -> 11
        # etc
        threshold = 1 + 10 ** (length / 0.1 - 1)

        # coordinate should be integers as index for array
        values = np.asarray(data[att], dtype=float)
        mask = floodfill_scipy(values, start_coord, threshold)

        if mask is not None:
            cids = data.pixel_component_ids
            subset_state = MaskSubsetState(mask, cids)
            mode = EditSubsetMode()
            mode.update(data, subset_state, focus_data=data)

    @property
    def profile_axis(self):
        slc = self.viewer.client.slice
        candidates = [i for i, s in enumerate(slc) if s not in ['x', 'y']]
        if len(candidates) == 0:
            return None
        else:
            return max(candidates, key=lambda i: self.viewer.client.display_data.shape[i])

    # TODO: the following three methods are for backward-compatibility with 
    #       glue < 0.9, and can be removed once we support only glue >= 0.9.

    def _display_data_hook(self, data):
        pass

    def _get_modes(self, axes):
        return [self]

    def close(self):
        pass
