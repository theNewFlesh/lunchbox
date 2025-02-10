import unittest

from enum import Enum

import lunchbox.theme as lbtheme
# ------------------------------------------------------------------------------


class FakeColorscheme(Enum):
    DARK1 = '#000000'
    DARK2 = '#000000'
    BG = '#000000'
    GREY1 = '#000000'
    GREY2 = '#000000'
    LIGHT1 = '#000000'
    LIGHT2 = '#000000'
    DIALOG1 = '#000000'
    DIALOG2 = '#000000'
    RED1 = '#000000'
    RED2 = '#000000'
    ORANGE1 = '#000000'
    ORANGE2 = '#000000'
    YELLOW1 = '#000000'
    YELLOW2 = '#000000'
    GREEN1 = '#000000'
    GREEN2 = '#000000'
    CYAN1 = '#000000'
    CYAN2 = '#000000'
    BLUE1 = '#000000'
    BLUE2 = '#000000'
    PURPLE1 = '#000000'
    PURPLE2 = '#000000'


class ThemeTests(unittest.TestCase):
    def test_get_plotly_template(self):
        result = lbtheme.get_plotly_template(FakeColorscheme)
        result = result['layout']
        expected = '#000000'

        self.assertEqual(result['plot_bgcolor'], expected)
        self.assertEqual(result['paper_bgcolor'], expected)
        self.assertEqual(result['title']['font']['color'], expected)
        self.assertEqual(result['legend']['font']['color'], expected)
        self.assertEqual(result['legend']['bgcolor'], expected)
        self.assertEqual(result['legend']['bordercolor'], expected)
        self.assertEqual(result['xaxis']['title']['font']['color'], expected)
        self.assertEqual(result['xaxis']['gridcolor'], expected)
        self.assertEqual(result['xaxis']['zerolinecolor'], expected)
        self.assertEqual(result['xaxis']['tickfont']['color'], expected)
        self.assertEqual(result['yaxis']['title']['font']['color'], expected)
        self.assertEqual(result['yaxis']['gridcolor'], expected)
        self.assertEqual(result['yaxis']['zerolinecolor'], expected)
        self.assertEqual(result['yaxis']['tickfont']['color'], expected)
