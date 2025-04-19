import unittest

from enum import Enum

import lunchbox.theme as lbc
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
    def test_to_dict(self):
        class TestEnum(lbc.EnumBase):
            FOO = 'foo'
            BAR = 'bar'

        result = TestEnum.to_dict()
        expected = dict(FOO='foo', BAR='bar')
        self.assertEqual(result, expected)

    def test_get_plotly_template(self):
        result = lbc.get_plotly_template(FakeColorscheme)
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


class ThemeFormatterTests(unittest.TestCase):
    def test_init(self):
        result = lbc.ThemeFormatter()

        expected = lbc.TerminalColorscheme.to_dict().items()
        expected = {k.lower(): v for k, v in expected}
        self.assertEqual(result.current_indent, 4)
        self.assertEqual(result._sep, '=')
        self.assertEqual(result._line_width, 80)
        self.assertEqual(result._write_calls, 0)
        self.assertEqual(result._colors, expected)
        self.assertEqual(result._heading_color, expected['blue2'])
        self.assertEqual(result._command_color, expected['cyan2'])
        self.assertEqual(result._flag_color, expected['green2'])

    def test_init_grayscale(self):
        result = lbc.ThemeFormatter(grayscale=True)
        expected = lbc.TerminalColorscheme.to_dict().keys()
        expected = {k.lower(): '' for k in expected}
        self.assertEqual(result._colors, expected)

    def test_write_text(self):
        result = lbc.ThemeFormatter()
        result.write_text('foo\n{cyan2}bar{clear}')
        colors = lbc.TerminalColorscheme.to_dict()
        expected = [
            '    foo {CYAN2}bar{CLEAR}'.format(**colors),
            '\n'
        ]
        self.assertEqual(result.buffer, expected)

    def test_write_usage(self):
        result = lbc.ThemeFormatter()
        result.write_usage('FOOBAR')
        colors = lbc.TerminalColorscheme.to_dict()
        sep = '=' * 73
        expected = ["{BLUE2}FOOBAR {sep}{CLEAR}\n".format(sep=sep, **colors)]
        self.assertEqual(result.buffer, expected)

    def test_write_dl(self):
        cyan2 = lbc.TerminalColorscheme.CYAN2.value
        green2 = lbc.TerminalColorscheme.GREEN2.value
        clear = lbc.TerminalColorscheme.CLEAR.value

        tmp = lbc.ThemeFormatter()
        tmp.write_dl([
            ('key1', 'value1'),
            ('key2', '{cyan2}value2{clear}')
        ])

        result = tmp.buffer
        self.assertEqual(result[0], f'      {green2}key1{clear}')
        self.assertEqual(result[1], '  ')
        self.assertEqual(result[2], 'value1\n')
        self.assertEqual(result[3], f'      {green2}key2{clear}')
        self.assertEqual(result[4], '  ')
        self.assertEqual(result[5], f'{cyan2}value2{clear}\n')

    def test_write_dl_end_section(self):
        blue2 = lbc.TerminalColorscheme.BLUE2.value
        clear = lbc.TerminalColorscheme.CLEAR.value

        tmp = lbc.ThemeFormatter()
        tmp._write_calls = 4
        tmp.write_dl([
            ('key1', 'value1'),
            ('key2', '{blue2}value2{clear}')
        ])
        result = tmp.buffer[-1]

        sep = '=' * 80
        expected = f'\n{blue2}{sep}{clear}\n'
        self.assertEqual(result, expected)

    def test_write_heading(self):
        blue2 = lbc.TerminalColorscheme.BLUE2.value
        cyan2 = lbc.TerminalColorscheme.CYAN2.value
        green2 = lbc.TerminalColorscheme.GREEN2.value
        clear = lbc.TerminalColorscheme.CLEAR.value
        tmp = lbc.ThemeFormatter()

        # other
        tmp.write_heading('pizza')
        result = tmp.buffer[0]
        self.assertEqual(result, f'{blue2}    pizza {clear}\n')

        # options
        tmp.write_heading('Options')
        result = tmp.buffer[1]
        self.assertEqual(result, f'{green2}    FLAGS {clear}\n')

        # commands
        tmp.write_heading('Commands')
        result = tmp.buffer[2]
        self.assertEqual(result, f'{cyan2}    COMMANDS {clear}\n')
