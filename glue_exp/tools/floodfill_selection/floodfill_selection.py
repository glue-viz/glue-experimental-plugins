import os
import numpy as np

from qtpy.QtWidgets import QMessageBox

from glue.core import Data

try:
    from glue.viewers.common.qt.toolbar_mode import ToolbarModeBase
except ImportError:
    from glue.viewers.common.qt.mouse_mode import MouseMode as ToolbarModeBase

from glue.core.edit_subset_mode import EditSubsetMode
from glue.core.subset import MaskSubsetState

from .floodfill_scipy import floodfill_scipy

from glue.config import viewer_tool

__all__ = ['FloodfillSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 4000000  # warn when floodfilling large images


@viewer_tool
class FloodfillSelectionTool(ToolbarModeBase):
    """
    Creates selection by using the mouse to pick regions using the flood fill
    algorithm: https://en.wikipedia.org/wiki/Flood_fill
    """

    icon = os.path.join(ROOT, "glue_floodfill.png")
    tool_id = 'Flood fill'
    action_text = 'Flood fill'
    tool_tip = ('Define a region of interest with the flood fill algorithm.')
    status_tip = ('Click to define a starting pixel and drag (keeping the '
                  'mouse clicked) to grow the selection.')

    def __init__(self, *args, **kwargs):

        super(FloodfillSelectionTool, self).__init__(*args, **kwargs)

        self._start_event = None
        self._end_event = None
        self._active_layer = None
        self._large_ok = None

        self._move_callback = self._floodfill_roi
        self._release_callback = self._floodfill_roi

    @property
    def visible_data_layers(self):
        data_layers = []
        for layer_state in self.viewer.state.layers:
            if layer_state.visible and isinstance(layer_state.layer, Data):
                data_layers.append(layer_state)
        return data_layers

    def press(self, event):

        visible_data_layers = self.visible_data_layers

        if len(visible_data_layers) == 0:
            message = ('There are no visible data layers')
            qmb = QMessageBox(QMessageBox.Critical, "Error", message)
            qmb.exec_()
            return

        if len(visible_data_layers) > 1:
            message = ('There is more than one visible data layer in this '
                       'viewer. This selection tool can only be applied to '
                       'one data layer, so hide any data layer you don\'t need '
                       'by unchecking boxes in the layer list and try again.')
            qmb = QMessageBox(QMessageBox.Critical, "Error", message)
            qmb.exec_()
            return

        if not self._large_ok and visible_data_layers[0].layer.size > WARN_THRESH:

            message = ('The dataset you want to apply this tool to is large '
                       'and you may run in to performance issues. Are you '
                       'sure you want to continue? Note that if you press OK '
                       'this warning will no longer be shown for this viewer. '
                       'You will need to start the selection again once this '
                       'dialog is closed.')

            buttons = QMessageBox.Ok | QMessageBox.Cancel
            result = QMessageBox.warning(self.viewer, 'Large data warning',
                                         message, buttons=buttons,
                                         defaultButton=QMessageBox.Cancel)

            if result == QMessageBox.Ok:
                self._large_ok = True

            return

        self._start_event = event
        self._active_layer = visible_data_layers[0]
        super(FloodfillSelectionTool, self).press(event)

    def move(self, event):
        if self._start_event is None:
            return
        self._end_event = event
        super(FloodfillSelectionTool, self).move(event)

    def release(self, event):
        if self._start_event is None:
            return
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

        data = self._active_layer.layer
        att = self._active_layer.attribute

        if data is None or att is None:
            return

        # Determine length of dragging action in units relative to the figure
        width, height = mode._start_event.canvas.get_width_height()
        dx = (mode._end_event.x - mode._start_event.x) / width
        dy = (mode._end_event.y - mode._start_event.y) / height
        length = np.hypot(dx, dy)

        # Make sure the coordinates are converted to the nearest integer
        x = int(round(mode._start_event.xdata))
        y = int(round(mode._start_event.ydata))

        start_coord = self.viewer.state.wcsaxes_slice[::-1]
        start_coord[start_coord.index('x')] = x
        start_coord[start_coord.index('y')] = y
        start_coord = tuple(start_coord)

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
