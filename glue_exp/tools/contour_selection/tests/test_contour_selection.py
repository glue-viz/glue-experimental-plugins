import numpy as np
from mock import MagicMock, patch

from glue.viewers.common.qt.tests.test_mouse_mode import TestMouseMode, Event

from ..contour_selection import ContourSelectionTool, contour_to_roi

from .. import contour_selection

try:
    from glue.utils.matplotlib import point_contour
except ImportError:  # glue < 0.5
    point_contour_path = 'glue.core.util.point_contour'
else:
    point_contour_path = 'glue.utils.matplotlib.point_contour'


class TestContourMode(TestMouseMode):

    def mode_factory(self):
        return ContourSelectionTool

    def test_roi_before_event(self):
        data = MagicMock()
        roi = self.mode.roi(data)
        assert roi is None

    def test_roi(self):
        with patch.object(contour_selection, 'contour_to_roi') as cntr:
            data = MagicMock()
            e = Event(1, 2)
            self.mode.press(e)
            self.mode.roi(data)
            cntr.assert_called_once_with(1, 2, data)


class TestContourToRoi(object):

    def test_roi(self):
        p = contour_to_roi(0, 1, np.array([[0., 1.], [2., 3.]]))
        np.testing.assert_array_almost_equal(p.vx, [1., 0.])
        np.testing.assert_array_almost_equal(p.vy, [2./3., 1.])

    def test_roi_null_result(self):
        p = contour_to_roi(0, 1, np.zeros((2,2)))
        assert p is None
