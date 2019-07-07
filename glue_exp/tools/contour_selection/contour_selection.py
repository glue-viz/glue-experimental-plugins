import os

from qtpy.QtWidgets import QMessageBox

from glue.viewers.matplotlib.qt.toolbar_mode import ToolbarModeBase

from glue.core import roi, Data
from glue.utils.matplotlib import point_contour
from glue.config import viewer_tool

__all__ = ['ContourSelectionTool']

ROOT = os.path.dirname(__file__)

WARN_THRESH = 10000000  # warn when contouring large images


@viewer_tool
class ContourSelectionTool(ToolbarModeBase):
    """
    Creates ROIs by using the mouse to 'pick' contours out of the data
    """

    icon = os.path.join(ROOT, "glue_contour.png")
    tool_id = 'Contour selection'
    action_text = 'Contour'
    tool_tip = 'Define a region of interest via contours'
    status_tip = ('Click on any pixel to select all pixels inside the '
                  'contour passing through that pixel')

    def __init__(self, *args, **kwargs):
        super(ContourSelectionTool, self).__init__(*args, **kwargs)
        self._release_callback = self._contour_roi
        self.viewer.state.add_callback('reference_data', self._on_reference_data_change)
        self._active_layer = None
        self._large_ok = None

    def _on_reference_data_change(self, reference_data):
        if reference_data is not None:
            self.enabled = reference_data.ndim == 2

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

        self._active_layer = visible_data_layers[0]
        super(ContourSelectionTool, self).press(event)

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

        if self._active_layer is None:
            return

        data = self._active_layer.layer
        att = self._active_layer.attribute

        if data is None or att is None:
            return

        if data.size > WARN_THRESH and not self.viewer._confirm_large_image(data):
            return

        roi = mode.roi(data[att])

        if roi:
            self.viewer.apply_roi(roi)

        self._active_layer = None


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

    x = int(round(x))
    y = int(round(y))

    xy = point_contour(x, y, data)
    if xy is None:
        return None

    p = roi.PolygonalROI(vx=xy[:, 0], vy=xy[:, 1])
    return p
