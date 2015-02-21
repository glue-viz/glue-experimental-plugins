# This is idealized (non-functional) code showing how one might easily write a
# PV slicing tool without any knowledge of glue internals beyond the public API
# to write tools and use viewers.
#
# The only thing that the user really needs to know below is:
#
# - Create a class that inherits from PathTool to make a tool that does
#   something after drawing a path.
#
# - Use the ``on_finish`` method to describe what happens when the user presses
#   'enter' after drawing the path. Note that other standard methods could be
#   defined, such as ``on_start``, ``on_draw``, etc.
#
# - The main widget that the tool is attached to is available as
#    ``self.parent_widget``, and the user would need to know how to access the data
#    from that widget.
#
# - The user can use add_cursor_callback method on widgets to add standard
#   callbacks when the cursor is dragged around.
#
# These can all be easily described in docs describing how to define tools.

from glue.tools import PathTool
from glue.parent_widgets import ImageWidget
from pvextractor import pv_slicer


class PVSlicingTool(PathTool):

    def on_finish(self):

        # Path vertices are available as self.x and self.y

        # Compute PV slice. Tools have a property widget that returns the
        # widget to which they are attached. This means that to access the data
        # we use self.parent_widget.data.
        pv_slice, x_slice, y_slice, wcs = pv_slicer(self.parent_widget.data, self.x, self.y)

        # We now want to initialize a new viewer that will show the PV slice
        if not hasattr(self.slice_viewer):
            self.slice_viewer = ImageWidget(pv_slice, wcs=wcs)
        else:
            self.slice_viewer.set_data(pv_slice, wcs=wcs)

        self.pv_slice = pv_slice
        self.x_slice = x_slice
        self.y_slice = y_slice

        # In addition to the above, the main functionality of the PV slice
        # widget currently is to include the crosshairs. But we may be able to
        # generalize the ImageWidget in order to support linking of crosshairs
        # between widgets.

        # Crosshairs could include either a cross or a full crosshair (or
        # different types of symbols)
        self.slice_viewer.add_cursor_callback(self.update_image_crosshair)

    def cursor_callback(self, xdata, ydata):

        # Here we define what happens if the user clicks inside the PV slice
        # viewer. This is not a required method of PVSlicingTool, but instead
        # is passed to the add_cursor_callback method in ``on_enter``

        # Find position slice where cursor is, clipping to the PV slice edges
        ind = np.clip(xdata, 0, self.pv_slice.shape[1] - 1)

        # Find pixel coordinate in input image for this slice
        x = self.x_slice[ind]
        y = self.y_slice[ind]

        # The 3-rd coordinate in the input WCS is simply the second
        # coordinate in the PV slice.
        z = ydata

        # Update crosshairs in parent widget
        self.parent_widget.move_crosshair(x, y)

        # Also update slice in parent widget
        self.parent_widget.set_slice(int(z))


tool_registry.add(PVSlicingTool, widget_cls=ImageWidget)
