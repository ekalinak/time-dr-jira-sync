import unittest
from ...time_doctor.timedoctor import TimeDoctor


class WidgetTestCase(unittest.TestCase):
    """
    First attempt for Unit tests
    """

    def __init__(self):
        self._test_data = []

    def setUp(self):
        self.time_doctor = TimeDoctor('The widget')

    def test_default_widget_size(self):
        self.assertEqual(self.widget.size(), (50, 50),
                         'incorrect default size')

    def test_widget_resize(self):
        self.widget.resize(100, 150)
        self.assertEqual(self.widget.size(), (100, 150),
                         'wrong size after resize')
