import os

from glue.config import viewer_tool
from glue.viewers.common.qt.tool import Tool


__all__ = ['ZoomInTool', 'ZoomOutTool']

ROOT = os.path.dirname(__file__)


@viewer_tool
class ZoomInTool(Tool):
    """Button to zoom in."""

    icon = os.path.join(ROOT, 'glue_zoomin.png')
    tool_id = 'Zoom In'
    action_text = tool_id
    tool_tip = tool_id
    shortcut = '+'

    def __init__(self, *args, **kwargs):
        super(ZoomInTool, self).__init__(*args, **kwargs)

    def activate(self):
        auto_zoom(self.viewer.axes, zoom_type='in')


@viewer_tool
class ZoomOutTool(Tool):
    """Button to zoom out."""

    icon = os.path.join(ROOT, 'glue_zoomout.png')
    tool_id = 'Zoom Out'
    action_text = tool_id
    tool_tip = tool_id
    shortcut = '-'

    def __init__(self, *args, **kwargs):
        super(ZoomOutTool, self).__init__(*args, **kwargs)

    def activate(self):
        auto_zoom(self.viewer.axes, zoom_type='out')


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
