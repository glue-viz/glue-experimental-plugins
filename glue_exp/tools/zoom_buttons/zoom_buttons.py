import os

from glue.viewers.common.qt.mouse_mode import MouseMode

try:
    from glue.external.qt import QtGui
except ImportError:
    from qtpy import QtGui

__all__ = ['ZoomButtonsTool']

ROOT = os.path.dirname(__file__)


class ZoomButtonsTool(object):

    def __init__(self, widget=None):
        self.widget = widget

    def _get_modes(self, axes):
        self._zoomin = ZoomInMode(axes)
        self._zoomout = ZoomOutMode(axes)
        return [self._zoomin, self._zoomout]

    def _display_data_hook(self, data):
        pass

    def close(self):
        pass


class ZoomInMode(MouseMode):
    """Buttom to zoom in."""

    def __init__(self, *args, **kwargs):
        super(ZoomInMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, 'glue_zoomin.png'))
        self.mode_id = 'Zoom In'
        self.action_text = 'Zoom In'
        self.tool_tip = 'Zoom in'

        # TODO: Pressing + should also zoom in.
        self.shortcut = '+'

    def activate(self):
        auto_zoom(self._axes, zoom_type='in')
        # TODO: Need to auto deactivate after zoom.


class ZoomOutMode(MouseMode):
    """Buttom to zoom out."""

    def __init__(self, *args, **kwargs):
        super(ZoomOutMode, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(os.path.join(ROOT, 'glue_zoomout.png'))
        self.mode_id = 'Zoom Out'
        self.action_text = 'Zoom Out'
        self.tool_tip = 'Zoom Out'

        # TODO: Pressing - should also zoom out.
        self.shortcut = '-'

    def activate(self):
        auto_zoom(self._axes, zoom_type='out')
        # TODO: Need to auto deactivate after zoom.


# Adapted from https://gist.github.com/tacaswell/3144287
def auto_zoom(ax, zoom_type='in', base_scale=2.0):
    """Automatically zoom in or out by a pre-defined scale factor.

    Parameters
    ----------
    ax : obj
        Matplotlib axis object.

    zoom_type : {'in', 'out'}
        Indicate action to zoom in or out.

    base_scale : float
        Scale factor.

    """
    if zoom_type == 'in':
        scale_factor = 1.0 / base_scale
    elif zoom_type == 'out':
        scale_factor = base_scale
    else:  # Do nothing.
        return

    # Get the current X and Y limits.
    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()

    cur_dx = (x2 - x1) * 0.5
    cur_dy = (y2 - y1) * 0.5

    xcen = x1 + cur_dx
    ycen = y1 + cur_dy

    dx = cur_dx * scale_factor
    dy = cur_dy * scale_factor

    # Set new limits.
    ax.set_xlim([xcen - dx, xcen + dx])
    ax.set_ylim([ycen - dy, ycen + dy])

    # Force redraw.
    ax.figure.canvas.draw()
