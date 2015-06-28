import numpy as np
from mock import MagicMock, patch

from glue.qt.tests.test_mouse_mode import TestMouseMode, Event

from ..contour_selection import ContourMode, contour_to_roi

try:
    from glue.utils.matplotlib import point_contour
except ImportError:  # glue < 0.5
    point_contour_path = 'glue.core.util.point_contour'
else:
    point_contour_path = 'glue.utils.matplotlib.point_contour'


class TestContourMode(TestMouseMode):

    def mode_factory(self):
        return ContourMode

    def test_roi_before_event(self):
        data = MagicMock()
        roi = self.mode.roi(data)
        assert roi is None

    def test_roi(self):
        with patch('glue_exp.tools.contour_selection.contour_selection.contour_to_roi') as cntr:
            data = MagicMock()
            e = Event(1, 2)
            self.mode.press(e)
            self.mode.roi(data)
            cntr.assert_called_once_with(1, 2, data)


class TestContourToRoi(object):

    def test_roi(self):
        with patch(point_contour_path) as point_contour:
            point_contour.return_value = np.array([[1, 2], [2, 3]])
            p = contour_to_roi(1, 2, None)
            np.testing.assert_array_almost_equal(p.vx, [1, 2])
            np.testing.assert_array_almost_equal(p.vy, [2, 3])

    def test_roi_null_result(self):
        with patch(point_contour_path) as point_contour:
            point_contour.return_value = None
            p = contour_to_roi(1, 2, None)
            assert p is None
