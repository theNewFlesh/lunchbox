from typing import Type  # noqa: F401

from enum import Enum

import click
# ------------------------------------------------------------------------------


class Colorscheme(Enum):
    '''
    Henanigans color scheme.
    '''
    DARK1 = '#040404'
    DARK2 = '#181818'
    BG = '#242424'
    GREY1 = '#343434'
    GREY2 = '#444444'
    LIGHT1 = '#A4A4A4'
    LIGHT2 = '#F4F4F4'
    DIALOG1 = '#444459'
    DIALOG2 = '#5D5D7A'
    RED1 = '#F77E70'
    RED2 = '#DE958E'
    ORANGE1 = '#EB9E58'
    ORANGE2 = '#EBB483'
    YELLOW1 = '#E8EA7E'
    YELLOW2 = '#E9EABE'
    GREEN1 = '#8BD155'
    GREEN2 = '#A0D17B'
    CYAN1 = '#7EC4CF'
    CYAN2 = '#B6ECF3'
    BLUE1 = '#5F95DE'
    BLUE2 = '#93B6E6'
    PURPLE1 = '#C98FDE'
    PURPLE2 = '#AC92DE'


def get_plotly_template(colorscheme=Colorscheme):
    # type: (Type[Colorscheme]) -> dict
    '''
    Create a plotly template from a given color scheme.

    Args:
        colorscheme (colorscheme): colorscheme enum.

    Returns:
        dict: Plotly template.
    '''
    cs = colorscheme
    colors = [
        cs.CYAN2, cs.RED2, cs.GREEN2, cs.BLUE2, cs.ORANGE2, cs.PURPLE2,
        cs.YELLOW2, cs.LIGHT2, cs.DARK2, cs.GREY2, cs.CYAN1, cs.RED1, cs.GREEN1,
        cs.BLUE1, cs.ORANGE1, cs.PURPLE1, cs.YELLOW1, cs.LIGHT1, cs.DARK1,
        cs.GREY1,
    ]

    template = dict(
        layout=dict(
            colorway=[x.value for x in colors],
            plot_bgcolor=cs.DARK2.value,
            paper_bgcolor=cs.DARK2.value,
            bargap=0.15,
            bargroupgap=0.05,
            autosize=True,
            margin=dict(t=80, b=65, l=80, r=105),
            title=dict(font=dict(
                color=cs.LIGHT2.value,
                size=30,
            )),
            legend=dict(
                font=dict(color=cs.LIGHT2.value),
                bgcolor=cs.BG.value,
                bordercolor=cs.BG.value,
                indentation=5,
                borderwidth=4,
            ),
            xaxis=dict(
                title=dict(font=dict(
                    color=cs.LIGHT2.value,
                    size=16,
                )),
                gridcolor=cs.BG.value,
                zerolinecolor=cs.GREY1.value,
                zerolinewidth=5,
                tickfont=dict(color=cs.LIGHT1.value),
                showgrid=True,
                autorange=True,
            ),
            yaxis=dict(
                title=dict(font=dict(
                    color=cs.LIGHT2.value,
                    size=16,
                )),
                gridcolor=cs.BG.value,
                zerolinecolor=cs.GREY1.value,
                zerolinewidth=5,
                tickfont=dict(color=cs.LIGHT1.value),
                showgrid=True,
                autorange=True,
            )
        )
    )
    return template


class ColorFormatter(click.HelpFormatter):
    '''
    ColorForatter makes click CLI output pretty.

    Include the following code to add it to click:
    ```
    from lunchbox.theme import ColorFormatter

    click.Context.formatter_class = ColorFormatter
    ```
    '''
    def __init__(
        self,
        *args,
        heading_color='blue2',
        command_color='cyan2',
        flag_color='green2',
        grayscale=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.current_indent = 4
        self._sep = '='
        self._line_width = 80
        self._write_calls = 0
        self._colors = dict(
            blue1='\033[0;34m',
            blue2='\033[0;94m',
            cyan1='\033[0;36m',
            cyan2='\033[0;96m',
            green1='\033[0;32m',
            green2='\033[0;92m',
            grey1='\033[0;90m',
            grey2='\033[0;37m',
            purple1='\033[0;35m',
            purple2='\033[0;95m',
            red1='\033[0;31m',
            red2='\033[0;91m',
            white='\033[0;97m',
            yellow1='\033[0;33m',
            yellow2='\033[0;93m',
            clear='\033[0m',
        )
        if grayscale:
            self._colors = {k: '' for k in self._colors.keys()}
        self._heading_color = self._colors[heading_color]
        self._command_color = self._colors[command_color]
        self._flag_color = self._colors[flag_color]

    def write_text(self, text):
        self._write_calls += 1
        self.write(
            click.formatting.wrap_text(
                text.format(**self._colors),
                self.width,
                initial_indent='    ',
                subsequent_indent='    ',
                preserve_paragraphs=True,
            )
        )
        self.write('\n')

    def write_usage(self, prog, *args, **kwargs):
        self._write_calls += 1
        text = prog.split(' ')[-1].upper() + ' '
        text = text.ljust(self._line_width, self._sep)
        text = '{h}{text}{clear}\n'.format(
            text=text, h=self._heading_color, **self._colors
        )
        self.write(text)

    def write_dl(self, rows, col_max=30, col_spacing=2):
        self._write_calls += 1
        data = []
        for k, v in rows:
            k = '  {f}{k}{clear}'.format(
                f=self._flag_color, k=k, **self._colors
            )
            v = v.format(**self._colors)
            data.append((k, v))
        super().write_dl(data, col_max, col_spacing)

        if self._write_calls in [4, 5]:
            line = self._sep * self._line_width
            line = '\n{h}{line}{clear}\n'.format(
                line=line, h=self._heading_color, **self._colors
            )
            self.write(line)

    def write_heading(self, heading):
        self._write_calls += 1
        color = self._heading_color
        if heading == 'Options':
            heading = 'FLAGS'
            color = self._flag_color
        elif heading == 'Commands':
            heading = 'COMMANDS'
            color = self._command_color
            self._flag_color = color
        heading += ' '
        buff = f"{'':>{self.current_indent}}"
        text = "{color}{buff}{heading}{clear}\n"
        text = text.format(
            buff=buff, heading=heading, color=color, **self._colors
        )
        self.write(text)
